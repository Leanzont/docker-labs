# Lab 04 — Multi-Stage Build with Go

## What this lab does

Demonstrates how multi-stage builds work in Docker using a Go HTTP server.
The goal is to produce a production-ready image significantly smaller
than a standard single-stage build.

## File structure

```
lab04_multi_stage_go/
├── Dockerfile
├── go.mod
├── main.go
└── README.md
```

## Dockerfile

```dockerfile
# Stage 1 — builder
FROM golang:1.26 AS builder
WORKDIR /app
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o server .

# Stage 2 — final image
FROM alpine:latest
WORKDIR /app
COPY --from=builder /app/server .
CMD ["./server"]
```

## Key concepts

**Multi-stage builds**
A Dockerfile can have multiple FROM instructions. Each one starts a new stage.
The final image only contains what you explicitly copy into it — everything else
from previous stages is discarded.

**Stage 1 — builder**
Uses `golang:1.26` which includes the Go compiler and all build tools (~1GB).
This stage compiles the binary. It is heavy but temporary.

**Stage 2 — final**
Uses `alpine:latest`, a minimal Linux distribution (~5MB).
Only the compiled binary is copied from stage 1. No compiler, no source code,
no build tools.

**CGO_ENABLED=0**
Compiles the binary statically, without depending on system libraries.
Required because Alpine is so minimal it does not include those libraries.

**GOOS=linux**
Tells Go to compile for Linux, regardless of the host OS.

## Size comparison

| Image                          | Disk Usage | Content Size |
| ------------------------------ | ---------- | ------------ |
| go-single (builder stage only) | 1.41GB     | 338MB        |
| go-multi (final multi-stage)   | 26MB       | 8.52MB       |
The final image is over 10x smaller than the builder stage alone.

## How to use

```bash
# Initialize Go modules (first time only)
go mod init lab04

# Build the final multi-stage image
docker build -t go-multi .

# Build only the builder stage (for comparison)
docker build --target builder -t go-single .

# Run the container
docker run -p 8080:8080 go-multi

# Test
curl http://localhost:8080
```

---
