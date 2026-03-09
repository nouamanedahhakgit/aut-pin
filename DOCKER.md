# Docker and Docker Hub

## Before First Run

Create `.env` files from examples (required for docker-compose):

```bash
cp multi-domain-clean/.env.example multi-domain-clean/.env
cp pin_generator/.env.example pin_generator/.env
cp articles-website-generator/.env.example articles-website-generator/.env  # if exists
cp website-parts-generator/.env.example website-parts-generator/.env       # if exists
```

Edit `multi-domain-clean/.env` with database credentials and API keys. For Docker, use `host.docker.internal` as MySQL host when the DB runs on your host machine.

## Quick Start (local build)

```bash
docker compose up -d
```

Access multi-domain-clean at http://localhost:5001

## Build and Push to Docker Hub

Replace `<username>` with your Docker Hub username.

```bash
# Build all images
docker compose build

# Tag for Docker Hub
docker tag aut-pin-multi-domain-clean:latest <username>/aut-pin-multi-domain-clean:latest
docker tag aut-pin-pin-generator:latest <username>/aut-pin-pin-generator:latest
docker tag aut-pin-articles-website-generator:latest <username>/aut-pin-articles-website-generator:latest
docker tag aut-pin-website-parts-generator:latest <username>/aut-pin-website-parts-generator:latest
docker tag aut-pin-llamacpp-manager:latest <username>/aut-pin-llamacpp-manager:latest

# Or build and tag individually:
docker build -t <username>/aut-pin-multi-domain-clean:latest ./multi-domain-clean
docker build -t <username>/aut-pin-pin-generator:latest -f pin_generator/Dockerfile .
docker build -t <username>/aut-pin-articles-website-generator:latest -f articles-website-generator/Dockerfile .
docker build -t <username>/aut-pin-website-parts-generator:latest ./website-parts-generator
docker build -t <username>/aut-pin-llamacpp-manager:latest -f llamacpp_manager/Dockerfile .

# Push
docker push <username>/aut-pin-multi-domain-clean:latest
docker push <username>/aut-pin-pin-generator:latest
docker push <username>/aut-pin-articles-website-generator:latest
docker push <username>/aut-pin-website-parts-generator:latest
docker push <username>/aut-pin-llamacpp-manager:latest
```

## Run from Docker Hub

Set `DOCKERHUB_USERNAME` and use the hub compose file:

```bash
export DOCKERHUB_USERNAME=your_username
docker compose -f docker-compose.hub.yml pull
docker compose -f docker-compose.hub.yml up -d
```

Or edit `docker-compose.hub.yml` and replace `<username>` with your username.
