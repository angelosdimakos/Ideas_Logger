.PHONY: build-all build-prod build-test build-dev run-prod run-test run-dev clean

# Build all images
build-all: build-prod build-test build-dev

# Build production image
build-prod:
	docker build -t ghcr.io/angelosdimakos/ideas_logger:prod -f Dockerfile.prod .

# Build test image
build-test:
	docker build -t ghcr.io/angelosdimakos/ideas_logger:test -f Dockerfile.test .

# Build development image
build-dev:
	docker build -t ghcr.io/angelosdimakos/ideas_logger:dev -f Dockerfile.dev .

# Run production container
run-prod:
	docker run --rm ghcr.io/angelosdimakos/ideas_logger:prod

# Run tests
run-test:
	docker run --rm ghcr.io/angelosdimakos/ideas_logger:test

# Start development environment
run-dev:
	docker run -it --rm -v $(PWD):/app ghcr.io/angelosdimakos/ideas_logger:dev

# Start with docker-compose
compose-up:
	docker-compose up -d dev

# Clean up
clean:
	docker-compose down
	docker system prune -f

# Show image sizes
image-sizes:
	@echo "Image sizes:"
	@docker images | grep ideas_logger

# Initialize the project structure if needed
init:
	@mkdir -p src tests data config scripts
	@touch src/__init__.py tests/__init__.py
	@echo "Project structure initialized"