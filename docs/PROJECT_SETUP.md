# Project Setup

## Tickets

### 1. Scaffold project
- [x] Create Django project and apps (accounts, proposals)
- [x] Create workflow package
- [x] Add requirements.txt

### 2. Dockerize
- [ ] Create Dockerfile
- [ ] Create docker-compose with db and backend services
- [ ] Run backend in container against db

### 3. Settings and env
- [ ] Configure settings from env
- [ ] Set up DRF, JWT, and CORS
- [ ] Add .env.example and .gitignore

## Services

| Service | Purpose |
| --- | --- |
| db | PostgreSQL |
| backend | Django API |

## Environment Variables

```
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_HOST
POSTGRES_PORT
SECRET_KEY
DEBUG
```

## Run

```bash
docker compose up --build
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py seed_demo
```