.PHONY: proto-go proto-python proto-all clean

PROTO_DIR := .
GO_OUT := ../services/stream-gateway/internal/proto
PYTHON_OUT := ../services/ai-inference/src/proto

proto-all: proto-go proto-python

proto-go:
	@echo "Generating Go gRPC code..."
	@mkdir -p $(GO_OUT)
	protoc --go_out=$(GO_OUT) --go_opt=paths=source_relative \
		--go-grpc_out=$(GO_OUT) --go-grpc_opt=paths=source_relative \
		$(PROTO_DIR)/detection.proto

proto-python:
	@echo "Generating Python gRPC code..."
	@mkdir -p $(PYTHON_OUT)
	python -m grpc_tools.protoc -I$(PROTO_DIR) \
		--python_out=$(PYTHON_OUT) \
		--grpc_python_out=$(PYTHON_OUT) \
		$(PROTO_DIR)/detection.proto

clean:
	rm -rf $(GO_OUT)/*.pb.go
	rm -rf $(PYTHON_OUT)/*_pb2*.py
