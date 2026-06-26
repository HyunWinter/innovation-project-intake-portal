# Innovation Project Intake Portal

A single auditable system covering the full lifecycle of bottom-up engineering proposals: submission, committee review, presentation, funding decision, and execution tracking.

## Tech Stack

- Vue.js, TailwindCSS
- Vite (dev frontend)
- Caddy (demo frontend + proxy + TLS)
- Django, Django REST Framework
- PostgreSQL
- Docker, docker compose
- AWS EC2 (demo hosting)

## Documentation

- [Project Setup](docs/PROJECT_SETUP.md) - project scaffolding, dockerization, settings, and env
- [System Design](docs/SYSTEM_DESIGN.md) - architecture, expected traffic, dev vs prod
- [Data Handling](docs/DATA_HANDLING.md) - data model and schema
- [State Development](docs/STATE_DEVELOPMENT.md) - roles, API endpoints, state machine
- [Interface Design](docs/INTERFACE_DESIGN.md) - frontend screens
- [Quality Assurance](docs/QUALITY_ASSURANCE.md) - tests

## Setup

### Prerequisites

This project uses [Docker](https://docs.docker.com/get-docker/) with Docker Compose
for both the backend and PostgreSQL.

```bash
git clone https://github.com/HyunWinter/innovation-project-intake-portal
cd innovation-project-intake-portal
```

### Configure environment variables

The backend uses a `.env` file to configure the database connection and other settings.
For more info, please check out the [Project Setup](docs/PROJECT_SETUP.md) documentation.

```bash
cp backend/.env.example backend/.env
```

TODO: Frontend

### Run

You can run the backend and database in Docker containers with the following command:

```bash
cd backend
docker compose up --build
```

By default, the API is served at http://localhost:8000.

TODO: Frontend

### Migration, superuser, and seed

Once the backend is running, you can run the following commands to apply migrations,
create a superuser, and seed the database with demo data:

```bash
cd backend
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py seed_demo
```

### Development

Code is linted and formatted with [Ruff](https://docs.astral.sh/ruff/)
And run automatically on every commit via [pre-commit](https://pre-commit.com/).

```bash
cd D:\dev\innovation-project-intake-portal\
pip install pre-commit
pre-commit install          # git hook
pre-commit run --all-files  # runs on all backend files
```

## Demo Credentials

## Walkthrough

## Architecture Notes

## What I'd Do With Another Week