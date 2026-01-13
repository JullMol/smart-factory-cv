package capture

import (
	"bytes"
	"image"
	"image/jpeg"
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
	c.log.Warn("RTSP capture not implemented, using demo mode")
	c.captureDemo()
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
