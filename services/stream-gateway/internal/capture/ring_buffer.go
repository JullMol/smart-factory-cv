package capture

import (
	"sync"
)

type RingBuffer struct {
	data     [][]byte
	head     int
	tail     int
	size     int
	capacity int
	mu       sync.RWMutex
}

func NewRingBuffer(capacity int) *RingBuffer {
	return &RingBuffer{
		data:     make([][]byte, capacity),
		capacity: capacity,
	}
}

func (rb *RingBuffer) Push(frame []byte) {
	rb.mu.Lock()
	defer rb.mu.Unlock()

	rb.data[rb.head] = frame
	rb.head = (rb.head + 1) % rb.capacity

	if rb.size < rb.capacity {
		rb.size++
	} else {
		rb.tail = (rb.tail + 1) % rb.capacity
	}
}

func (rb *RingBuffer) GetLatest() ([]byte, bool) {
	rb.mu.RLock()
	defer rb.mu.RUnlock()

	if rb.size == 0 {
		return nil, false
	}

	idx := (rb.head - 1 + rb.capacity) % rb.capacity
	return rb.data[idx], true
}

func (rb *RingBuffer) Pop() ([]byte, bool) {
	rb.mu.Lock()
	defer rb.mu.Unlock()

	if rb.size == 0 {
		return nil, false
	}

	frame := rb.data[rb.tail]
	rb.data[rb.tail] = nil
	rb.tail = (rb.tail + 1) % rb.capacity
	rb.size--

	return frame, true
}

func (rb *RingBuffer) Size() int {
	rb.mu.RLock()
	defer rb.mu.RUnlock()
	return rb.size
}

func (rb *RingBuffer) Clear() {
	rb.mu.Lock()
	defer rb.mu.Unlock()

	rb.data = make([][]byte, rb.capacity)
	rb.head = 0
	rb.tail = 0
	rb.size = 0
}
