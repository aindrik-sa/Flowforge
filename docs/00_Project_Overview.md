# FlowForge — Project Overview

## What is FlowForge?

FlowForge is an enterprise-grade project management SaaS platform inspired by Jira, Linear, ClickUp, Asana, and Monday.com.

It enables organizations to manage users, projects, tasks, boards, sprints, and workflows through a well-designed REST API.

## Purpose

This project demonstrates intermediate-to-advanced Python/Django backend engineering skills:

- Custom authentication with JWT
- Multi-tenant architecture with organization-based isolation
- Role-based access control (RBAC)
- Modular monolith architecture
- PostgreSQL with proper indexing and constraints
- Redis for caching and message brokering
- Celery for background task processing
- Comprehensive testing with pytest
- Docker-based development and deployment
- API-first design with OpenAPI documentation

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11+ |
| Framework | Django 5.2, Django REST Framework |
| Database | PostgreSQL 17 |
| Cache | Redis 7 |
| Background Jobs | Celery |
| Auth | JWT (SimpleJWT) |
| API Docs | drf-spectacular (Swagger) |
| Containers | Docker, Docker Compose |
| Testing | pytest, pytest-django |
| Code Quality | Ruff, Black |

## Getting Started

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Git

### Setup

```bash
# Clone the repository
git clone <repo-url>
cd FlowForge

# Start infrastructure services
docker compose up -d

# Set up Python environment
cd backend
python -m venv .venv
.venv/Scripts/activate  # Windows
source .venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements/development.txt

# Configure environment
cp ../.env.example .env
# Edit .env with your values

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Access Points

- API: http://localhost:8000/api/v1/
- Swagger UI: http://localhost:8000/api/schema/swagger-ui/
- Django Admin: http://localhost:8000/admin/

### Running Tests

```bash
cd backend
python -m pytest --tb=short -v
```
