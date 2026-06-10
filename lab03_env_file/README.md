# Lab 03 — .env File and Health Checks with Docker Compose

## What this lab does
Extends the Flask + MySQL application from lab02 with two production-relevant concepts:
a `.env` file to keep credentials out of the codebase, and a health check to ensure
Flask never connects to MySQL before it is actually ready.

## Project structure

```
lab03_env_file/
├── app/
│   ├── app.py        # Flask application (unchanged from lab02)
│   ├── Dockerfile    # Image definition (unchanged from lab02)
│   └── init.sql      # Creates the visits table on first startup
├── docker-compose.yml
├── .env              # Real credentials — never pushed to GitHub
└── .env.example      # Template showing which variables are required
```

## What changed from lab02

| | lab02 | lab03 |
|---|---|---|
| Credentials | Hardcoded in docker-compose.yml | Stored in .env file |
| Startup order | depends_on (container start only) | health check (service ready) |

---

## .env file

The `.env` file stores all sensitive values — credentials, passwords, and configuration
that should never be visible in the codebase or on GitHub.

```
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_DATABASE=visitsdb
MYSQL_USER=flaskuser
MYSQL_PASSWORD=flaskpassword
DB_USER=flaskuser
DB_PASSWORD=flaskpassword
DB_NAME=visitsdb
```

This file goes in `.gitignore` — it never reaches GitHub.

The `.env.example` is the public template. It shows which variables are needed
without exposing real values:

```
MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_DATABASE=your_database_name
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=your_db_name
```

Anyone who clones the repo copies `.env.example` to `.env` and fills in their own values.

Docker Compose reads the `.env` file automatically — no extra configuration needed.
Variables are referenced in `docker-compose.yml` using `${VARIABLE_NAME}` syntax.

---

## Health check

`depends_on` only waits for the container to start — not for the service inside it to be ready.
MySQL takes a few seconds to initialize after the container starts. If Flask tries to connect
too early, the app crashes.

A health check solves this by running a test command inside the container on a schedule.
Docker only marks the container as healthy when the test succeeds — and only then allows
dependent services to start.

```yaml
healthcheck:
  test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
  interval: 5s
  timeout: 3s
  retries: 5
```

| Field | Description |
|---|---|
| `test` | Command Docker runs inside the container to check if MySQL is ready |
| `interval` | How often the test runs — every 5 seconds |
| `timeout` | How long Docker waits for a response before marking the test as failed — 3 seconds |
| `retries` | How many consecutive failures before marking the container as unhealthy — 5 attempts × 5 seconds = up to 25 seconds for MySQL to be ready |

With `condition: service_healthy` in `depends_on`, Flask waits until MySQL passes the health check:

```yaml
depends_on:
  db:
    condition: service_healthy
```

### Startup flow

```
db container starts
        ↓
Docker runs mysqladmin ping every 5s
        ↓
MySQL not ready yet → fails → waits 5s → tries again
        ↓
MySQL ready → responds OK → container marked as healthy
        ↓
app container starts → Flask connects to MySQL successfully
```

Without a health check, this flow is not guaranteed — Flask can start before MySQL is ready
and fail on the first connection attempt.

---

## docker-compose.yml

```yaml
services:
  db:
    image: mysql:8.0
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 5s
      timeout: 3s
      retries: 5
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    volumes:
      - db_data:/var/lib/mysql
      - ./app/init.sql:/docker-entrypoint-initdb.d/init.sql

  app:
    build: ./app
    ports:
      - "5000:5000"
    environment:
      DB_HOST: db
      DB_USER: ${DB_USER}
      DB_PASSWORD: ${DB_PASSWORD}
      DB_NAME: ${DB_NAME}
    depends_on:
      db:
        condition: service_healthy

volumes:
  db_data:
```

---

## Key concepts

- **`.env` file** — stores sensitive values outside the codebase; read automatically by Docker Compose
- **`.env.example`** — public template that documents required variables without exposing real values
- **`${VARIABLE}` syntax** — references `.env` values inside `docker-compose.yml`
- **Health check** — verifies the service inside the container is ready, not just the container itself
- **`condition: service_healthy`** — makes `depends_on` wait for a passing health check before starting the dependent service

## How to use

```bash
# Copy the template and fill in your values
cp .env.example .env

# Start all containers
docker compose up

# Verify health check in logs
# You should see: Container lab03-db-1  Waiting → Healthy

# Open in browser
http://localhost:5000

# Stop containers
docker compose down

# Stop and delete all data
docker compose down --volumes
```
