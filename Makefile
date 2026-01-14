.PHONY: dev build up down clean test help

help:
	@echo "Smart Factory CV - Available Commands"
	@echo "======================================"
	@echo "  dev       - Start development servers"
	@echo "  ai        - Start AI inference server only"
	@echo "  dashboard - Start dashboard only"
	@echo "  test      - Run tests"
	@echo "  clean     - Clean cache files"

dev:
	@echo "Starting development servers..."
	@echo "Run each command in separate terminals:"
	@echo ""
	@echo "  1. AI Server:   cd services/ai-inference && python src/main.py"
	@echo "  2. Dashboard:   cd services/dashboard && npm run dev"
	@echo ""

ai:
	cd services/ai-inference && python src/main.py

dashboard:
	cd services/dashboard && npm run dev

test:
	cd services/ai-inference && python -m pytest tests/ -v

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
