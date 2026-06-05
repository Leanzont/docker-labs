# Lab 02 — Flask + MySQL with Docker Compose

## What this lab does
Deploys a two-container application using Docker Compose — a Flask web app and a MySQL database communicating over Docker's internal network. Each page visit is recorded in the database and the total count is displayed in the browser.

## Why Docker Compose
Without Docker Compose, you would need to manually run each container with `docker run`, configure the network manually, and manage everything separately. Docker Compose solves this by defining all containers, their configuration, and how they communicate in a single file.

## Project structure

```
lab02_flask_mysql/
├── app/
│   ├── app.py        # Flask application
│   ├── Dockerfile    # Image definition for the app container
│   └── init.sql      # SQL script to create the visits table
└── docker-compose.yml
```

## How it works

```
Browser
   ↓
app container (Flask - port 5000)
   ↓
db container (MySQL - internal network)
   ↓
db_data volume (persistent storage)
```

Every request to `localhost:5000` inserts a row into the `visits` table and returns the total count.

## Files explained

### docker-compose.yml
The orchestrator — defines both services, their configuration, and how they relate to each other.

**Service `db`:**
- Uses the official `mysql:8.0` image from Docker Hub — no Dockerfile needed
- Environment variables configure MySQL on first start: creates the database, user, and password automatically. These values are read by MySQL itself — not by the Python code
- Two volumes:
  - `db_data:/var/lib/mysql` — persists MySQL data outside the container so it survives restarts
  - `./app/init.sql:/docker-entrypoint-initdb.d/init.sql` — bind mount that places the local `init.sql` inside the container; MySQL automatically executes any `.sql` file it finds in that directory on first startup

**Service `app`:**
- Built from `./app/Dockerfile` — not a pre-built image
- `ports: "5000:5000"` — exposes the container's port 5000 to your machine's port 5000
- Environment variables are read by `app.py` via `os.environ` — these are the values Python uses to connect to the database
- `DB_HOST: db` — the hostname of the database is literally `db`, the service name; Docker Compose creates an internal network where each service is reachable by its name. Cannot use `localhost` because each container has its own localhost
- `depends_on: db` — ensures the `db` container starts before `app`

**Named volume declaration:**
```yaml
volumes:
  db_data:
```
Required — declares the named volume so Docker creates and manages it. Without this declaration, the reference in the `db` service would fail.

### app/Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY app.py .
RUN pip install flask mysql-connector-python
CMD ["python", "app.py"]
```
- `FROM` — base image from Docker Hub
- `WORKDIR` — sets the working directory inside the container
- `COPY` — copies `app.py` from your machine into the container
- `RUN` — installs dependencies at build time
- `CMD` — command executed when the container starts

### app/init.sql
```sql
CREATE TABLE IF NOT EXISTS visits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    visited_at DATETIME
);
```
Executed automatically by MySQL on first startup via the bind mount. Creates the `visits` table.

### app/app.py
Flask application with a single route. On every request it inserts a row into `visits` and returns the total count. Credentials come from environment variables — nothing hardcoded.

## Key concepts

- **Docker Compose** — orchestrates multiple containers from a single file
- **Internal network** — Docker Compose creates it automatically; services communicate by service name
- **`image` vs `build`** — `image` pulls from Docker Hub, `build` constructs from a local Dockerfile
- **Named volume** — Docker-managed persistent storage; survives `docker compose down`
- **Bind mount** — maps a local file directly into the container at a specific path
- **Environment variables** — credentials passed to containers without hardcoding them in code
- **`depends_on`** — controls startup order between services

## About credentials and hardcoding

The `docker-compose.yml` has two separate blocks of environment variables:

**Service `db` — MySQL configuration:**
```yaml
environment:
  MYSQL_ROOT_PASSWORD: rootpassword
  MYSQL_DATABASE: visitsdb
  MYSQL_USER: flaskuser
  MYSQL_PASSWORD: flaskpassword
```
These are read by MySQL itself to set up the database on first start. The Python code never reads these directly.

**Service `app` — application configuration:**
```yaml
environment:
  DB_HOST: db
  DB_USER: flaskuser
  DB_PASSWORD: flaskpassword
  DB_NAME: visitsdb
```
These are read by Python via `os.environ`:
```python
def get_db():
    return mysql.connector.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"]
    )
```
The values in `db` and `app` must match — same user, same password — because `app` is connecting to `db`.

`DB_HOST` must always be `db` — the name of the other service. Changing it would break the connection.
The rest (`DB_USER`, `DB_PASSWORD`, `DB_NAME`) can be anything as long as both services use the same values.

**In this lab** the credentials are written directly in `docker-compose.yml` because it is a local lab — the file never reaches GitHub.

**In production** the real values would live in a `.env` file:
```
DB_PASSWORD=realpassword
DB_USER=realuser
```

And `docker-compose.yml` would reference them:
```yaml
environment:
  DB_PASSWORD: ${DB_PASSWORD}
```

The `.env` file goes in `.gitignore` — same concept as `terraform.tfvars` in Terraform labs. The credentials never reach GitHub.

## How to use

```bash
# Start all containers
docker compose up

# Open in browser
http://localhost:5000

# Stop containers (data persists)
docker compose down

# Stop containers and delete all data
docker compose down --volumes
```

## docker compose down vs docker compose down --volumes

| Command | Containers | Volume `db_data` |
|---|---|---|
| `docker compose down` | Removed | Survives |
| `docker compose down --volumes` | Removed | Deleted |

Use `--volumes` when you want a clean start from zero.
