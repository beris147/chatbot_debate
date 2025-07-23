# Variables
PYTHON := $(shell command -v python3 2>/dev/null)
PIP := $(shell command -v pip3 2>/dev/null)
DOCKER := $(shell command -v docker 2>/dev/null)
UVICORN := $(shell uvicorn --help 2>/dev/null)
VENV := .venv
CONTAINER_NAME = beristain-chatbot-debate-container
IMAGE_NAME = beristain-chatbot-debate-image

.PHONY: all help install test run down clean

all: help

help:
	@echo ""
	@echo "Available make commands:"
	@echo "  make install     - Install Python dependencies"
	@echo "  make test        - Run tests"
	@echo "  make run         - Run the app and services via Docker"
	@echo "  make down        - Stop services"
	@echo "  make clean       - Stop and remove all Docker containers, networks, and volumes"
	@echo ""

install:
ifndef PYTHON
	@echo "Error: python3 not found. Please install Python 3: https://www.python.org/downloads/"
	exit 1
endif
ifndef PIP
	@echo "Error: pip3 not found. Please install pip: https://pip.pypa.io/en/stable/installation/"
	exit 1
endif
	@echo "Creating virtual environment..."
	@$(PYTHON) -m venv $(VENV)
	@. $(VENV)/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
	@echo "Dependencies installed successfully."
ifndef UVICORN
	@echo "UVICORN needs to be install Python 3: https://www.python.org/downloads/"
	exit 1
endif


test:
	@. $(VENV)/bin/activate && pytest

run:
ifndef DOCKER
	@echo "Error: Docker is not installed. Please install Docker: https://docs.docker.com/get-docker/"
	exit 1
endif
	@$(DOCKER) build -t ${IMAGE_NAME} . && ${DOCKER} run -d -p 8000:8000 --name ${CONTAINER_NAME} ${IMAGE_NAME} 

down:
ifndef DOCKER
	@echo "Error: docker-compose not found. Please install it: https://docs.docker.com/compose/install/"
	exit 1
endif
	@$(DOCKER) stop ${CONTAINER_NAME}

clean:
ifndef DOCKER
	@echo "Error: docker-compose not found. Please install it: https://docs.docker.com/compose/install/"
	exit 1
endif
	@$(DOCKER) rm -f ${CONTAINER_NAME} && ${DOCKER} rmi -f ${IMAGE_NAME}
