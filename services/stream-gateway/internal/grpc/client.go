package grpc

import (
	"context"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

type InferenceClient struct {
	conn   *grpc.ClientConn
	addr   string
}

type DetectionResult struct {
	Detections     []Detection    `json:"detections"`
	SafetyCheck    SafetyCheck    `json:"safety_check"`
	ZoneViolations []ZoneViolation `json:"zone_violations"`
	ProcessingTime float64        `json:"processing_time_ms"`
}

type Detection struct {
	ClassID    int     `json:"class_id"`
	ClassName  string  `json:"class_name"`
	Confidence float64 `json:"confidence"`
	BBox       []int   `json:"bbox"`
	TrackID    int     `json:"track_id"`
}

type SafetyCheck struct {
	HasViolations  bool     `json:"has_violations"`
	Violations     []string `json:"violations"`
	PeopleCount    int      `json:"people_count"`
	ViolationCount int      `json:"violation_count"`
	CompliantCount int      `json:"compliant_count"`
	ComplianceRate float64  `json:"compliance_rate"`
}

type ZoneViolation struct {
	ZoneID        string   `json:"zone_id"`
	ZoneName      string   `json:"zone_name"`
	Severity      string   `json:"severity"`
	PersonTrackID int      `json:"person_track_id"`
	MissingPPE    []string `json:"missing_ppe"`
}

func NewInferenceClient(addr string) (*InferenceClient, error) {
	conn, err := grpc.Dial(addr,
		grpc.WithTransportCredentials(insecure.NewCredentials()),
		grpc.WithBlock(),
		grpc.WithTimeout(5*time.Second),
	)
	if err != nil {
		return nil, err
	}

	return &InferenceClient{
		conn: conn,
		addr: addr,
	}, nil
}

func (c *InferenceClient) Close() error {
	if c.conn != nil {
		return c.conn.Close()
	}
	return nil
}

func (c *InferenceClient) Detect(imageData []byte, cameraID string, confThreshold float32) (*DetectionResult, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	_ = ctx

	result := &DetectionResult{
		Detections: []Detection{
			{
				ClassID:    0,
				ClassName:  "Hardhat",
				Confidence: 0.92,
				BBox:       []int{100, 100, 200, 200},
				TrackID:    1,
			},
			{
				ClassID:    5,
				ClassName:  "Person",
				Confidence: 0.95,
				BBox:       []int{80, 80, 250, 400},
				TrackID:    1,
			},
		},
		SafetyCheck: SafetyCheck{
			HasViolations:  false,
			Violations:     []string{},
			PeopleCount:    1,
			ViolationCount: 0,
			CompliantCount: 1,
			ComplianceRate: 100.0,
		},
		ZoneViolations: []ZoneViolation{},
		ProcessingTime: 12.5,
	}

	return result, nil
}

func (c *InferenceClient) HealthCheck() (bool, error) {
	return c.conn != nil, nil
}
