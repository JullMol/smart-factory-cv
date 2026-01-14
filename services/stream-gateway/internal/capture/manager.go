package capture

import (
	"bufio"
	"bytes"
	"image"
	"image/jpeg"
	"io"
	"os/exec"
	"sync"
	"time"

	"go.uber.org/zap"
)

type Camera struct {
	ID           string
	Name         string
	URL          string
	Type         string
	Active       bool
	Connected    bool
	LastFrameAt  time.Time
	buffer       *RingBuffer
	stopChan     chan struct{}
	reconnecting bool
	mu           sync.RWMutex
	log          *zap.Logger
}

type CameraConfig struct {
	ID   string `json:"id" yaml:"id"`
	Name string `json:"name" yaml:"name"`
	URL  string `json:"url" yaml:"url"`
	Type string `json:"type" yaml:"type"`
}

type Manager struct {
	cameras map[string]*Camera
	mu      sync.RWMutex
	log     *zap.Logger
}

func NewManager(log *zap.Logger) *Manager {
	return &Manager{
		cameras: make(map[string]*Camera),
		log:     log,
	}
}

func (m *Manager) AddCamera(cfg CameraConfig) error {
	m.mu.Lock()
	defer m.mu.Unlock()

	cam := &Camera{
		ID:       cfg.ID,
		Name:     cfg.Name,
		URL:      cfg.URL,
		Type:     cfg.Type,
		Active:   false,
		buffer:   NewRingBuffer(30),
		stopChan: make(chan struct{}),
		log:      m.log.With(zap.String("camera", cfg.ID)),
	}

	m.cameras[cfg.ID] = cam
	m.log.Info("camera added", zap.String("id", cfg.ID), zap.String("url", cfg.URL))

	return nil
}

func (m *Manager) RemoveCamera(id string) bool {
	m.mu.Lock()
	defer m.mu.Unlock()

	cam, exists := m.cameras[id]
	if !exists {
		return false
	}

	if cam.Active {
		cam.Stop()
	}

	delete(m.cameras, id)
	m.log.Info("camera removed", zap.String("id", id))
	return true
}

func (m *Manager) StartCamera(id string) error {
	m.mu.RLock()
	cam, exists := m.cameras[id]
	m.mu.RUnlock()

	if !exists {
		return nil
	}

	go cam.Start()
	return nil
}

func (m *Manager) StopCamera(id string) error {
	m.mu.RLock()
	cam, exists := m.cameras[id]
	m.mu.RUnlock()

	if !exists {
		return nil
	}

	cam.Stop()
	return nil
}

func (m *Manager) GetCamera(id string) (*Camera, bool) {
	m.mu.RLock()
	defer m.mu.RUnlock()
	cam, exists := m.cameras[id]
	return cam, exists
}

func (m *Manager) GetActiveCameras() []*Camera {
	m.mu.RLock()
	defer m.mu.RUnlock()

	var active []*Camera
	for _, cam := range m.cameras {
		if cam.Active && cam.Connected {
			active = append(active, cam)
		}
	}
	return active
}

func (m *Manager) GetAllCameras() []CameraStatus {
	m.mu.RLock()
	defer m.mu.RUnlock()

	var statuses []CameraStatus
	for _, cam := range m.cameras {
		statuses = append(statuses, CameraStatus{
			ID:          cam.ID,
			Name:        cam.Name,
			URL:         cam.URL,
			Type:        cam.Type,
			Active:      cam.Active,
			Connected:   cam.Connected,
			LastFrameAt: cam.LastFrameAt,
		})
	}
	return statuses
}

type CameraStatus struct {
	ID          string    `json:"id"`
	Name        string    `json:"name"`
	URL         string    `json:"url"`
	Type        string    `json:"type"`
	Active      bool      `json:"active"`
	Connected   bool      `json:"connected"`
	LastFrameAt time.Time `json:"last_frame_at"`
}

func (c *Camera) Start() {
	c.mu.Lock()
	c.Active = true
	c.stopChan = make(chan struct{})
	c.mu.Unlock()

	c.log.Info("camera starting", zap.String("type", c.Type))

	switch c.Type {
	case "webcam":
		c.captureWebcam()
	case "rtsp":
		c.captureRTSP()
	case "demo":
		c.captureDemo()
	default:
		c.captureDemo()
	}
}

func (c *Camera) Stop() {
	c.mu.Lock()
	defer c.mu.Unlock()

	if !c.Active {
		return
	}

	c.Active = false
	close(c.stopChan)
	c.log.Info("camera stopped")
}

func (c *Camera) GetLatestFrame() ([]byte, bool) {
	return c.buffer.GetLatest()
}

func (c *Camera) captureDemo() {
	c.mu.Lock()
	c.Connected = true
	c.mu.Unlock()

	ticker := time.NewTicker(100 * time.Millisecond)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			frame := generateDemoFrame(640, 480)
			c.buffer.Push(frame)
			c.mu.Lock()
			c.LastFrameAt = time.Now()
			c.mu.Unlock()
		case <-c.stopChan:
			return
		}
	}
}

func (c *Camera) captureWebcam() {
	c.log.Warn("webcam capture not implemented, using demo mode")
	c.captureDemo()
}

func (c *Camera) captureRTSP() {
	if c.URL == "" {
		c.log.Error("RTSP URL is empty")
		return
	}

	c.mu.Lock()
	c.Connected = false
	c.mu.Unlock()

	backoff := time.Second

	for {
		select {
		case <-c.stopChan:
			return
		default:
			// Reset backoff if we had a successful connection
			if c.Connected {
				backoff = time.Second
			}

			c.log.Info("connecting to RTSP stream", zap.String("url", c.URL))

			// Use ffmpeg to read RTSP and output MJPEG to stdout
			// -re is not needed for reading, but helpful for file inputs. 
			// Here we assume RTSP source controls timing, or we accept as fast as possible.
			// -rtsp_transport tcp gives better reliability (less packet drop artifacts)
			cmd := exec.Command("ffmpeg",
				"-rtsp_transport", "tcp",
				"-i", c.URL,
				"-f", "image2pipe",
				"-vcodec", "mjpeg",
				"-q:v", "5", // Balance quality/size
				"-",
			)

			stdout, err := cmd.StdoutPipe()
			if err != nil {
				c.log.Error("failed to create stdout pipe", zap.Error(err))
				time.Sleep(backoff)
				continue
			}

			stderr, err := cmd.StderrPipe()
			if err != nil {
				c.log.Error("failed to create stderr pipe", zap.Error(err))
			}

			if err := cmd.Start(); err != nil {
				c.log.Error("failed to start ffmpeg", zap.Error(err))
				time.Sleep(backoff)
				backoff *= 2
				if backoff > 30*time.Second {
					backoff = 30 * time.Second
				}
				continue
			}

			// Read stderr in background to avoid blocking
			go func() {
				scanner := bufio.NewScanner(stderr)
				for scanner.Scan() {
					line := scanner.Text()
					c.log.Warn("ffmpeg stderr", zap.String("line", line))
				}
			}()

			c.mu.Lock()
			c.Connected = true
			c.reconnecting = false
			c.mu.Unlock()
			c.log.Info("connected to RTSP stream")

			// Reader for MJPEG stream
			reader := bufio.NewReader(stdout)
			
			// JPEG Magic Numbers
			var soi = []byte{0xFF, 0xD8}
			var eoi = []byte{0xFF, 0xD9}

			for {
				select {
				case <-c.stopChan:
					if cmd.Process != nil {
						cmd.Process.Kill()
					}
					return
				default:
				}

				// Look for Start Of Image
				// Using ReadSlice is efficient but we need to handle if logic splits headers
				// Scan until we find SOI
				
				// Simple parser: Read until 0xFF, restart if next byte isn't 0xD8
				// This is a naive implementation but works for most ffmpeg mjpeg streams
				// Specific to ffmpeg image2pipe mjpeg format
				
				// Read until we encounter 0xFF 0xD8
				
				// Robust approach: Read generic bytes, search for SOI
				// Since we are in a loop, let's use a specialized scanner approach or just read bytes
				
				// P.S. ffmpeg image2pipe simply concatenates JPEGs. 
				// Reading Length is hard because it's not length-prefixed.
				// We MUST search for EOI 0xFF 0xD9
				
				// PHASE 1: Find SOI
				peekBytes, err := reader.Peek(2)
				if err != nil {
					break // Stream ended or error
				}
				
				if !bytes.Equal(peekBytes, soi) {
					// Discard 1 byte and try again
					_, _ = reader.Discard(1)
					continue
				}

				// We found SOI, now read until EOI
				// We'll read into a buffer growing it until we find EOI
				
				var frameBuffer []byte
				// Read headers (approx)
				headerBuf := make([]byte, 2)
				_, err = io.ReadFull(reader, headerBuf)
				if err != nil {
					break
				}
				frameBuffer = append(frameBuffer, headerBuf...)

				// Read rest until EOI
				// We can read byte by byte or chunk. Chunk is better.
				chunk := make([]byte, 1024)
				foundEOI := false
				
				for !foundEOI {
					n, err := reader.Read(chunk)
					if err != nil {
						break
					}
					if n == 0 {
						break
					}
					
					frameBuffer = append(frameBuffer, chunk[:n]...)
					
					// Check last few bytes for EOI
					// It might be in the middle of chunk, but usually end of image
					// Search backwards
					if len(frameBuffer) >= 2 {
						// Optimized: search for 0xFF 0xD9 in the appended chunk + 1 prev byte
						// Simply searching from end of buffer is usually fine for MJPEG stream
						
						// Scan the whole buffer for EOI? No, too slow.
						// Scan just the new data? Yes.
						// But EOI might be split.
						
						// Simplest robust way: Scan form where we last checked.
						// Or simply: FFmpeg usually sends complete packets if buffer is big enough.
						// Let's index.
						
						idx := bytes.LastIndex(frameBuffer, eoi)
						if idx != -1 {
							// Found EOI.
							// Truncate at EOI + 2
							frameBuffer = frameBuffer[:idx+2]
							foundEOI = true
						}
					}
				}
				
				if !foundEOI {
					break // Error parsing or stream closed
				}

				// Valid JPEG frame in frameBuffer
				// Push to ring buffer
				// Provide a copy because buffer might operate on refs? 
				// RingBuffer usually copies or holds ref. 
				// We reuse frameBuffer var in loop? No, we redeclare var frameBuffer inside loop?
				// Actually `var frameBuffer []byte` is inside loop, but `chunk` is reused.
				// However `append` creates new slice if needed. `frameBuffer` is fresh per loop iteration.
				// So it is safe to pass `frameBuffer` reference if RingBuffer doesn't modify it.
				
				// Optimization: Check if it's a valid image (optional)
				// config, _, err := image.DecodeConfig(bytes.NewReader(frameBuffer))
				// if err == nil { ... }
				
				c.buffer.Push(frameBuffer)
				c.mu.Lock()
				c.LastFrameAt = time.Now()
				c.mu.Unlock()
			}

			// Loop broke = process died or error
			if cmd.Process != nil {
				cmd.Process.Kill()
			}
			cmd.Wait() // Clean up zombies
			
			c.log.Warn("RTSP stream disconnected, reconnecting...", zap.String("url", c.URL))
			
			c.mu.Lock()
			c.Connected = false
			c.reconnecting = true
			c.mu.Unlock()

			time.Sleep(backoff)
			backoff *= 2
			if backoff > 30*time.Second {
				backoff = 30 * time.Second
			}
		}
	}
}

func generateDemoFrame(width, height int) []byte {
	img := image.NewRGBA(image.Rect(0, 0, width, height))

	for y := 0; y < height; y++ {
		for x := 0; x < width; x++ {
			offset := (y*width + x) * 4
			gray := uint8((x + y + int(time.Now().UnixMilli()/100)) % 256)
			img.Pix[offset] = gray
			img.Pix[offset+1] = gray
			img.Pix[offset+2] = gray
			img.Pix[offset+3] = 255
		}
	}

	var buf bytes.Buffer
	jpeg.Encode(&buf, img, &jpeg.Options{Quality: 80})
	return buf.Bytes()
}
