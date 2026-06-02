# Lab 01 — Dockerized Port Scanner

A Python port scanner packaged in a Docker container. Scans a target host for open TCP ports and saves the results to a JSON file — no local Python installation required.

---

## Key Features

- Scans a configurable range of TCP ports on any host
- Exports results to a structured `result.json` file
- Fully containerized — runs identically on any machine with Docker
- Supports volume mounting to persist output outside the container

---

## Tech Stack

- Python 3.11
- Docker
- `socket` — TCP connection probing
- `argparse` — CLI argument parsing
- `json` — structured output

---

## Project Structure

```
lab01_dockerized_port_scanner/
├── Dockerfile
├── port_scanner.py
└── README.md
```

---

## How It Works

The scanner attempts a TCP connection to each port in the specified range using Python's `socket` module. If the connection succeeds (return code `0`), the port is marked as open and added to the results.

```python
result = s.connect_ex((host, port))
return result == 0  # 0 = open, anything else = closed/filtered
```

Results are serialized to JSON:

```json
[
  { "port": 80, "status": "Open" },
  { "port": 443, "status": "Open" }
]
```

---

## Docker Concepts Practiced

| Concept | Description |
|---|---|
| `FROM` | Base image — `python:3.11-slim` provides a minimal Python environment |
| `WORKDIR` | Sets the working directory inside the container (`/app`) |
| `COPY` | Copies the script from the host into the container image |
| `CMD` | Default command executed when the container starts |
| `docker build` | Builds an image from the Dockerfile |
| `docker run` | Creates and starts a container from an image |
| `docker ps -a` | Lists all containers, including stopped ones |
| Volumes (`-v`) | Mounts a host directory into the container to persist output |

### Docker Architecture

```
Your terminal              Docker daemon
(client)                 (background service)
    │                           │
    │── docker run ────────────▶│
    │                           │── pull/load image
    │                           │── create container
    │                           │── execute CMD
    │◀─── output ───────────────│
```

---

## Usage

### 1. Build the image

```bash
docker build -t port-scanner .
```

### 2. Run with default settings (ports 1–1024 on scanme.nmap.org)

```bash
docker run port-scanner
```

### 3. Run with custom host and port range, saving results locally

```bash
mkdir -p test_output

docker run -v $(pwd)/test_output:/app/output port-scanner \
  python port_scanner.py --host scanme.nmap.org --start 79 --end 82
```

The `-v` flag mounts `test_output/` on your machine to `/app/output` inside the container, so `result.json` is saved locally after the container stops.

### CLI Arguments

| Argument | Required | Default | Description |
|---|---|---|---|
| `--host` | ✅ | — | Target hostname or IP |
| `--start` | ❌ | `1` | First port to scan |
| `--end` | ❌ | `1024` | Last port to scan |

---

## Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY port_scanner.py .
CMD ["python", "port_scanner.py", "--host", "scanme.nmap.org"]
```

---

## One-Time Docker Setup (Linux)

```bash
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER   # run Docker without sudo (re-login required)
```
