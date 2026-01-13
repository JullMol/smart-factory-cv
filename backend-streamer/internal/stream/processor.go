package stream

import (
	"encoding/json"
	"log"
	"time"

	"github.com/yourusername/smart-factory-cv/backend-streamer/internal/websocket"
)

type Processor struct {
	rtspURL     string
	aiEngineURL string
	hub         *websocket.Hub
	running     bool
	stopChan    chan bool
}

type DetectionResult struct {
	Detections []Detection `json:"detections"`
	SafetyCheck SafetyCheck `json:"safety_check"`
	ProcessingTimeMs float64 `json:"processing_time_ms"`
}

type Detection struct {
	ClassID    int     `json:"class_id"`
	ClassName  string  `json:"class_name"`
	Confidence float64 `json:"confidence"`
	BBox       []int   `json:"bbox"`
}

type SafetyCheck struct {
	HasViolations  bool     `json:"has_violations"`
	Violations     []string `json:"violations"`
	PeopleCount    int      `json:"people_count"`
	ViolationCount int      `json:"violation_count"`
}

func NewProcessor(rtspURL, aiEngineURL string, hub *websocket.Hub) *Processor {
	return &Processor{
		rtspURL:     rtspURL,
		aiEngineURL: aiEngineURL,
		hub:         hub,
		running:     false,
		stopChan:    make(chan bool),
	}
}

func (p *Processor) Start() {
	p.running = true

	ticker := time.NewTicker(time.Second * 2)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			if p.running {
				p.processFrame()
			}

		case <-p.stopChan:
			return
		}
	}
}

func (p *Processor) Stop() {
	p.running = false
	p.stopChan <- true
}

func (p *Processor) processFrame() {
	result := DetectionResult{
		Detections: []Detection{
			{
				ClassID:    0,
				ClassName:  "Hardhat",
				Confidence: 0.95,
				BBox:       []int{100, 100, 200, 200},
			},
		},
		SafetyCheck: SafetyCheck{
			HasViolations:  false,
			Violations:     []string{},
			PeopleCount:    1,
			ViolationCount: 0,
		},
		ProcessingTimeMs: 45.2,
	}

	jsonData, err := json.Marshal(result)
	if err != nil {
		log.Printf("JSON marshal error: %v\n", err)
		return
	}

	p.hub.Broadcast(jsonData)
}
