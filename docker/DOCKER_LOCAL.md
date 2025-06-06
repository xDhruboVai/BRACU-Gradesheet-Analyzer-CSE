# BRACU Gradesheet Analyzer - Docker Setup

Simple Docker setup to run the BRACU Gradesheet Analyzer locally.

## Prerequisites

- Docker installed on your system
- Docker Compose (usually included with Docker Desktop)

### Installing Docker (if you don't have it)

**Windows & macOS:**
1. Download [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Install and restart your computer
3. Docker Compose is included automatically

**Linux (Ubuntu/Debian):**
```bash
# Update package index
sudo apt update

# Install Docker
sudo apt install docker.io docker-compose

# Add your user to docker group (to run without sudo)
sudo usermod -aG docker $USER

# Restart terminal or log out/in for group changes to take effect
```

**Linux (Other distributions):**
- **Fedora/RHEL:** `sudo dnf install docker docker-compose`
- **Arch:** `sudo pacman -S docker docker-compose`

**Verify installation:**
```bash
docker --version
docker-compose --version
```

## Quick Start

```bash
# Go to docker directory
cd docker

# Start the application
./run.sh start

# Access at http://localhost:8501
```

## Available Commands

```bash
cd docker

./run.sh start      # Build and start the application
./run.sh stop       # Stop the application
./run.sh restart    # Restart the application
./run.sh logs       # Show application logs
./run.sh status     # Show container status
./run.sh build      # Build Docker image
./run.sh clean      # Remove all containers and images
```

## Alternative: Direct Docker Compose

```bash
cd docker
docker-compose up --build -d    # Start
docker-compose down             # Stop
```

## File Structure

```
├── docker/
│   ├── Dockerfile              # Docker configuration
│   ├── docker-compose.yml      # Docker Compose configuration
│   ├── run.sh                  # Management script
│   └── .dockerignore           # Files to exclude from build
├── app.py                      # Main application
├── requirements.txt            # Dependencies
└── temp/                       # Uploaded files
```

## Access

Once running: **http://localhost:8501**

## Troubleshooting

```bash
# Port already in use
./run.sh stop

# Build issues
./run.sh clean
./run.sh build

# View logs
./run.sh logs
```

That's it! Simple Docker setup for local development.
