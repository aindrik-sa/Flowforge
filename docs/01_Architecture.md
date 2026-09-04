# FlowForge — Architecture

## Architectural Style

FlowForge uses a **modular Django monolith**.

This means:
- All code lives in a single Django project
- Features are organized into independent Django apps
- Each app has clear boundaries and responsibilities
- The architecture can be split into services later if needed

## Why Not Microservices?

At this scale, microservices would add complexity without benefit:
- Network latency between services
- Distributed transaction challenges
- Deployment complexity
- Operational overhead

A well-structured monolith is the right choice until the team or traffic demands otherwise.

## Request Flow

### Write Operations (Create, Update, Delete)

```
HTTP Request
    ↓
URL Router
    ↓
View (thin — delegates to serializer/service)
    ↓
Serializer (input validation, shape)
    ↓
Service (business logic, orchestration)
    ↓
Model / Manager (database operations)
    ↓
PostgreSQL
```

### Read Operations

```
HTTP Request
    ↓
View
    ↓
Selector (query logic)
    ↓
Serializer (output shape)
    ↓
Response
```

## Layer Responsibilities

| Layer | Responsibility | Should NOT do |
|-------|---------------|--------------|
| **View** | HTTP handling, status codes, permissions | Business logic, complex queries |
| **Serializer** | Input/output validation and shape | Database writes, business rules |
| **Service** | Business logic, orchestration, transactions | HTTP handling, serialization |
| **Selector** | Complex read queries, annotations | Write operations |
| **Model** | Schema, constraints, simple methods | Orchestration, HTTP |
| **Manager** | Object creation, custom querysets | Business logic |

## Application Structure

```
FlowForge/
├── backend/
│   ├── apps/
│   │   ├── accounts/        # Users, authentication
│   │   ├── common/          # Shared models, utilities
│   │   ├── organizations/   # Multi-tenancy, memberships
│   │   ├── projects/        # Projects (future)
│   │   └── tasks/           # Tasks (future)
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py          # Shared settings
│   │   │   ├── development.py   # Dev overrides
│   │   │   ├── production.py    # Prod overrides
│   │   │   └── test.py          # Test overrides
│   │   ├── urls.py          # Root URL configuration
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── conftest.py          # Shared test fixtures
│   ├── manage.py
│   └── requirements/
│       ├── base.txt
│       ├── development.txt
│       └── production.txt
├── docker/
├── docs/
├── scripts/
├── docker-compose.yml
└── .env.example
```

## App Internal Structure

```
app/
├── api/
│   ├── serializers.py   # Input/output shapes
│   ├── views.py         # HTTP endpoints
│   └── urls.py          # URL routing
├── models.py            # Database schema
├── managers.py          # Custom managers
├── services.py          # Business logic
├── selectors.py         # Complex queries
├── permissions.py       # Authorization
├── admin.py             # Django admin
└── tests/
    ├── test_models.py
    └── test_api.py
```

## Key Principles

1. **Fat services, thin views** — Views handle HTTP; services handle logic
2. **No business logic in serializers** — Serializers validate shape, not rules
3. **Selectors for reads** — Centralize query logic to prevent N+1 issues
4. **Explicit permissions** — Every endpoint has clear authorization
5. **Tenant isolation** — Organization data never leaks across boundaries
