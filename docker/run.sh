#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not available. Please install Docker Compose first."
    exit 1
fi

show_usage() {
    echo "BRACU Gradesheet Analyzer - Docker Runner"
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start           Build and start the application"
    echo "  stop            Stop the application"
    echo "  restart         Restart the application"
    echo "  build           Build the Docker image"
    echo "  logs            Show application logs"
    echo "  status          Show container status"
    echo "  clean           Clean up containers and images"
    echo "  help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start        # Start the application"
    echo "  $0 logs         # View logs"
    echo "  $0 stop         # Stop the application"
}

mkdir -p ../temp

if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    DOCKER_COMPOSE="docker compose"
fi

case "${1:-help}" in
    start)
        print_status "Starting BRACU Gradesheet Analyzer..."
        $DOCKER_COMPOSE up --build -d
        print_success "Application started successfully!"
        print_status "Access the application at: http://localhost:8501"
        ;;
    stop)
        print_status "Stopping BRACU Gradesheet Analyzer..."
        $DOCKER_COMPOSE down
        print_success "Application stopped successfully!"
        ;;
    restart)
        print_status "Restarting BRACU Gradesheet Analyzer..."
        $DOCKER_COMPOSE restart
        print_success "Application restarted successfully!"
        ;;
    build)
        print_status "Building Docker image..."
        $DOCKER_COMPOSE build --no-cache
        print_success "Docker image built successfully!"
        ;;
    logs)
        print_status "Showing application logs (Press Ctrl+C to exit)..."
        $DOCKER_COMPOSE logs -f bracu-analyzer
        ;;
    status)
        print_status "Container status:"
        $DOCKER_COMPOSE ps
        ;;
    clean)
        print_warning "This will remove all containers and images related to this project."
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Cleaning up..."
            $DOCKER_COMPOSE down --rmi all --volumes --remove-orphans
            docker system prune -f
            print_success "Cleanup completed!"
        else
            print_status "Cleanup cancelled."
        fi
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac
