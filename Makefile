.PHONY: dev build up down clean proto test lint export help

help:
	@echo "Smart Factory CV - Available Commands"
	@echo "======================================"
	@echo "  dev       - Start development servers (local)"
	@echo "  build     - Build all Docker images"
	@echo "  up        - Start all services with Docker Compose"
	@echo "  down      - Stop all services"
	@echo "  clean     - Remove containers and volumes"
	@echo "  proto     - Generate gRPC code from proto files"
	@echo "  test      - Run all tests"
	@echo "  lint      - Run linters on all services"
	@echo "  export    - Export model to ONNX format"

dev:
	@echo "Starting development servers..."
	@powershell -Command "Start-Process -FilePath 'python' -ArgumentList 'services/ai-inference/src/main.py' -WorkingDirectory '$(CURDIR)'"
	@powershell -Command "Start-Sleep -Seconds 3"
	@powershell -Command "Start-Process -FilePath 'go' -ArgumentList 'run ./cmd/server' -WorkingDirectory '$(CURDIR)/services/stream-gateway'"
	@powershell -Command "Start-Sleep -Seconds 2"
	@cd services/dashboard && npm run dev

build:
	docker build -t smartfactory/ai-inference ./services/ai-inference
	docker build -t smartfactory/stream-gateway ./services/stream-gateway
	docker build -t smartfactory/dashboard ./services/dashboard

up:
	docker-compose -f deploy/docker-compose.yml up -d

down:
	docker-compose -f deploy/docker-compose.yml down

clean:
	docker-compose -f deploy/docker-compose.yml down -v
	docker system prune -f

proto:
	cd proto && $(MAKE) proto-all

test:
	cd services/stream-gateway && go test ./... -race -cover
	cd services/ai-inference && python -m pytest tests/ -v

lint:
	cd services/stream-gateway && golangci-lint run
	cd services/ai-inference && black --check src/ && ruff check src/
	cd services/dashboard && npm run lint

export:
	cd services/ai-inference && python scripts/export_model.py onnx --model ../models/best.pt
