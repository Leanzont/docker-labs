# Lab 05 — Docker Networking

## What this lab does

Demonstrates how Docker networking works — how containers communicate with each other
using names instead of IPs, how network isolation works, and what happens when containers
are on different networks.

---

## What is Docker networking

Docker networking allows containers to communicate with each other through names, not IPs.
Docker creates an internal DNS — so instead of connecting to `172.18.0.3`, you connect to
`nginx-server` and Docker resolves it automatically.

This is exactly what happened in lab02 and lab03 with `DB_HOST: db` — Docker Compose was
creating a custom network automatically behind the scenes. In this lab we do it manually.

---

## Default network vs custom network

| | Default bridge | Custom bridge |
|---|---|---|
| Created by | Docker automatically | You, manually |
| Name resolution | Not available — IP only | Available — containers resolve by name |
| Isolation | All containers share it | Only containers you explicitly connect |

This is the key difference. On the default bridge network, `ping container1` fails with
`bad address` because there is no DNS. On a custom network, it works.

---

## File structure

```
lab05_docker_networking/
├── app/
│   ├── app.py
│   └── Dockerfile
└── README.md
```

---

## app.py

Python script that makes an HTTP request to `nginx-server` by name — no IP, no hardcoding.

```python
import urllib.request

url = "http://nginx-server"

try:
    response = urllib.request.urlopen(url)
    print(f"Connected to {url}")
    print(f"Status: {response.status}")
    print(f"Response: {response.read(100).decode()}")
except Exception as e:
    print(f"Failed to connect: {e}")
```

## Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY app.py .
CMD ["python", "app.py"]
```

---

## How to reproduce

### 1. Create the custom network

```bash
docker network create my-network
```

Verify it was created:

```bash
docker network ls
```

You should see `my-network` with DRIVER `bridge` and SCOPE `local`.

### 2. Test name resolution — two containers on the same network

Open two terminals and run one command in each:

```bash
# Terminal 1
docker run -it --rm --name container1 --network my-network alpine sh

# Terminal 2
docker run -it --rm --name container2 --network my-network alpine sh
```

From container1, ping container2 by name:

```bash
ping container2
```

It works — Docker resolves `container2` to its internal IP automatically.

### 3. Test isolation — container on the default network

```bash
docker run -it --rm --name container3 alpine sh
```

From container3, try to reach container1:

```bash
ping container1
```

Output: `ping: bad address 'container1'`

container3 is on the default bridge network. container1 is on `my-network`.
Different networks — no visibility between them.

### 4. Real HTTP communication between containers

```bash
# Build the Python app image
docker build -t network-app ./app

# Start nginx on my-network
docker run -d --name nginx-server --network my-network nginx

# Run the Python app on my-network
docker run --rm --name network-app --network my-network network-app
```

Expected output:

```
Connected to http://nginx-server
Status: 200
Response: <!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
...
```

`network-app` resolved `nginx-server` by name and got a 200 response.
Both containers are on `my-network` — that is why it works.

---

## Flag reference

| Flag | Description |
|---|---|
| `-it` | `-i` keeps STDIN open, `-t` assigns a virtual terminal — together they allow interactive access |
| `--rm` | Removes the container automatically when it stops |
| `--name` | Assigns a name to the container — this name is what other containers use to reach it |
| `--network` | Connects the container to a specific network |
| `-d` | Runs the container in the background (detached mode) |

---

## Key concepts

**Custom bridge network** — a Docker-managed network you create manually. Enables DNS
resolution between containers by name. Required for containers to communicate without
hardcoding IPs.

**DNS resolution** — on a custom network, Docker automatically resolves container names
to their internal IPs. `http://nginx-server` works because `nginx-server` is the container name.

**Network isolation** — containers on different networks cannot reach each other.
This is how you control which services can communicate in a real application.

**`--name` vs image name** — in `docker run --name network-app network-app`, the first
`network-app` is the container name (what you see in `docker ps`), the second is the image.
They happen to be the same here but they are independent.

---

## Cleanup

```bash
docker stop nginx-server
docker rm nginx-server
docker network rm my-network
```
