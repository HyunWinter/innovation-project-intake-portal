# Innovation Project Intake Portal

A single auditable system covering the full lifecycle of bottom-up engineering proposals: submission, committee review, presentation, funding decision, and execution tracking.

## Screen Recording

[Watch Demo on Google Drive](https://drive.google.com/file/d/1dzCbBIX42EJBO5HvQV-Ze5_IW04O3F-L/view?usp=sharing)

## Tech Stack

**Frontend**
- Vue 3 (Composition API)
- Tailwind CSS & shadcn-vue
- Vite (Build Tool)

**Backend**
- Django 5 & Django REST Framework (DRF)
- PostgreSQL 16 (Relational Database)
- Gunicorn & Whitenoise (WSGI & Static Files)

**Infrastructure & Deployment**
- Caddy (Reverse Proxy & Auto-TLS)
- Docker & Docker Compose (Containerization)
- GitHub Actions (CI/CD Pipeline)
- AWS EC2 (Hosting)

## Documentation

- [System Design](docs/SYSTEM_DESIGN.md) - architecture, expected traffic, dev vs prod
- [Project Setup](docs/PROJECT_SETUP.md) - project scaffolding, dockerization, settings, and env
- [Data Handling](docs/DATA_HANDLING.md) - data model and schema
- [State Development](docs/STATE_DEVELOPMENT.md) - roles, API endpoints, state machine
- [Interface Design](docs/INTERFACE_DESIGN.md) - frontend screens
- [Quality Assurance](docs/QUALITY_ASSURANCE.md) - tests
- [Deployment](docs/DEPLOYMENT.md) - provisioning, domain, CI/CD

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

The frontend reads API endpoint from `.env` as well

```bash
cp frontend/.env.example frontend/.env
```

### Run

You can run the backend and database in Docker containers with the following command:

```bash
cd backend
docker compose up --build
```

By default, the API is served at http://localhost:8000.

The frontend dev server runs with pnpm:

```bash
cd frontend
pnpm install
pnpm dev
```

By default, the app is served at http://localhost:5173.

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

### Frontend (Portal)
For demo, you can use following accounts for testing purposes.

| Username | Password | Name | Role |
| --- | --- | --- | --- |
| `andrew.submitter@example.com` | `demo1234` | Andrew Submitter | Submitter |
| `aleece.submitter2@example.com` | `demo1234` | Aleece Submitter | Submitter |
| `ben.committee@example.com` | `demo1234` | Ben Committee | Committee |
| `bethany.committee2@example.com` | `demo1234` | Bethany Committee | Committee |
| `colin.management@example.com` | `demo1234` | Colin Management | Management |
| `cooper.management@example.com` | `demo1234` | Cooper Management | Management |

### Backend (Django Admin)
The admin panel (`/admin/`) requires a superuser

| Username | Password | Name | Role |
| --- | --- | --- | --- |
| `admin@example.com` | `demo1234` | Admin | Superuser |

## Happy-path Walkthrough

### Category A (No Funding)
| Actor | Action | Result |
| --- | --- | --- |
| Submitter | Creates request | `pending` |
| Committee | Selects `proceed_independently` | `approved` |

### Category B (Funding Required)
| Actor | Action | Result |
| --- | --- | --- |
| Submitter | Creates request | `pending` |
| Committee | Selects `request_presentation` | `under_review` |
| Committee | Schedules presentation | `under_review` (Scheduled) |
| Committee | Marks presentation advanced | `under_review` (Completed) |
| Management | Selects `go` (Funding Approved)| `approved` |

## Architecture Notes

- **State Machine Engine:** All transition rules are strictly enforced server side. Invalid transitions (like action after reject) reliably return HTTP 400.
- **Audit Trails & Soft Deletes:** Every state change logs an `AuditEvent` with the actor in the same transaction. Soft deletes ensure historical integrity.
- **SSE & Inbox Pattern:** Lightweight SSE sync notifications. The DB acts as the single source of truth while the frontend buffers locally.
- **Containerized Infrastructure:** Production parity demo uses GitHub Actions and Docker Compose (Postgres, Django, Vite, Caddy) for simplicity and ease of deployment.

## Trade-offs

- **Drafts in JSONB:** Unfinished submissions use raw JSONB to allow flexible auto saves. Full validation is not done until actual submission.
- **Accumulating Data:** Drafts and notifications accumulate over time. We may want to purge them periodically when the userbase increases.
- **Tech Category Enum:** Hardcoded for simplicity. If categories change frequently, this should be moved to a standalone relational table like snippets.
- **SSE vs WebSockets:** I chose SSE because notifications are strictly one way (from server to client). This prevents heavy WebSocket overhead.
- **Single-Node Demo:** Opted for a monolithic EC2 Docker Compose deployment for demo simplicity. We could move to managed AWS cloud native setup later.

## What I'd Do With Another Week

1. **Cloud Native AWS Setup:** Migrate to AWS ECS Fargate for auto scaling compute, RDS for Multi-AZ database, and ElastiCache for Redis.
2. **Draft Purging Job:** Implement a Celery worker to automatically purge incomplete `DraftRequest` records older than 30 days.
3. **E2E Browser Testing:** Add Playwright to automate and verify the complex multi role state transitions inside the browser.
4. **Adopt Target Stack:** Learn and rebuild the backend using the team's preferred stack (PHP Slim Framework + Eloquent).