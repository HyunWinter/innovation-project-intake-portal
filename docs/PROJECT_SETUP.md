# Project Setup

## Tickets

### 1. Scaffold project
- [x] Create Django project and apps (accounts, proposals)
- [x] Create workflow package
- [x] Add requirements.txt

### 2. Dockerize
- [x] Create Dockerfile
- [x] Create docker-compose with db and backend services
- [x] Run backend in container against db

### 3. Settings and env
- [x] Configure settings from env
- [x] Set up DRF, JWT, and CORS
- [x] Add .env.example and .gitignore

## Services

| Service | Purpose |
| --- | --- |
| db | PostgreSQL |
| backend | Django API |

## Environment Variables

Backend:

```
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_HOST
POSTGRES_PORT
SECRET_KEY
DEBUG
```

Frontend:

```
VITE_API_BASE
```

## Run

```bash
docker compose up --build
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py seed_demo
```