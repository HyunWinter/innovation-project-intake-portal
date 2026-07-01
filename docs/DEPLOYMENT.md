# Deployment

## Infrastructure

- **Server**: AWS EC2 (`t3.small`)
- **Web Server**: Caddy (Reverse proxy & Auto TLS via Let's Encrypt)
- **Backend Server**: Gunicorn + Whitenoise (Admin static files)
- **Database**: PostgreSQL 16
- **CI/CD**: GitHub Actions

## Setup Guide

### 1. EC2 Provisioning
- **OS**: Ubuntu 24.04 LTS
- **Security Group**: Ports `80` (HTTP), `443` (HTTPS), and `22` (SSH)
- **Dependencies**: Docker and Git

### 2. Domain Registration
- Purchase a domain in Route 53 and point to the EC2.

### 3. GitHub Secrets (CI/CD)
Add the following secrets to your repository's `Settings > Secrets and variables > Actions`:
- `EC2_HOST`: EC2 Public IP
- `EC2_USERNAME`: `ubuntu`
- `EC2_SSH_KEY`: The full `.pem` private key content
- `DOMAIN`: domain

### 4. Initial Seeding
After triggerring the GitHub Action, SSH into the EC2 instance to seed the database with demo users:
```bash
cd ~/innovation-portal
docker compose exec backend python manage.py seed_demo
docker compose exec backend python manage.py createsuperuser
```
