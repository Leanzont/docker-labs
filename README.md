# Docker Labs

Personal Docker labs built as part of a self-directed Cloud/DevOps engineering learning path.
Each lab focuses on a specific concept, building on the previous one — from containers and images
to multi-container applications and production-ready deployments.

---

## Labs

| Lab                                                                  | Description                                                                                                                | Concepts                                                                                             |
| -------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| [Lab 01 — Dockerized Port Scanner](./lab01_dockerized_port_scanner/) | Python port scanner packaged and run inside a Docker container                                                             | Dockerfile, images, containers, volumes, CLI arguments, JSON output                                  |
| [Lab 02 — Flask + MySQL with Docker Compose](./lab02_flask_mysql/)   | Two-container application — Flask web app connected to a MySQL database, tracking page visits                              | Docker Compose, multi-container networking, named volumes, bind mounts, environment variables, Flask |
| [Lab 03 — .env File and Health Checks](./lab03_env_file/)            | Lab 02 extended with credential management via .env file and health checks to guarantee MySQL is ready before Flask starts | .env file, .env.example, environment variable injection, health checks, condition: service_healthy   |
| [Lab 04 — Multi-Stage Build with Go](./lab04_multi_stage_go/)        | Go HTTP server built with a multi-stage Dockerfile to produce a minimal production-ready image                             | Multi-stage builds, Alpine Linux, static binaries, CGO_ENABLED, image size optimization              |

---

## Tech Stack

- Docker
- Python 3
- Flask
- MySQL
- Bash
- Linux
- Go

---

## Goals

Building a solid foundation in containerization to complement Terraform and AWS skills,
working toward a remote Cloud/DevOps Engineer role.
