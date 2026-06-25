# System Design

## Overview

This project is an internal Innovation Project Intake Portal for a single company. This document covers the system design, tech stacks, expected traffic and storage, and a comparison between development and production environments.

## Tech Stacks

- Django (Python)
- Docker
- Vue.js
- TailwindCSS
- AWS EC2 (t3.small)

## Expected Prod Traffic / Storage

This is all hypothetical for demo purposes.

- Internal tool for a company with ~2000 employees
- Submission write: ~1000 per year = average ~2.7 per day
- State write: average ~50 per day
- Read: average ~1000 per day
- Peak users: ~50 per day

## Dev vs Prod Comparison

Comparison between dev and prod environments for scaling purposes. The demo environment is a single EC2 instance with a small Postgres database. The production environment can expand to 1-2 Fargate instances to start. Then we can start adding CloudFront caching system, OpenSearch, and other scaling solutions as needed.

| | Dev | Production |
| :--- | :--- | :--- |
| Compute | AWS EC2 | AWS ECS Fargate |
| Database | Postgres | AWS RDS Postgres |
| Redis | Redis | AWS ElastiCache micro |
| Static | nginx + Caddy | AWS CloudFront + S3 |
| TLS | Caddy + Let's Encrypt | AWS Cloudfront |
| Backup | S3 (pg_dump) | AWS RDS Snapshot |
| Expected cost | ~$15 | ~$100 |