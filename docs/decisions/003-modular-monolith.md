# ADR-003: Modular Monolith Architecture

## Status
Accepted

## Context
We need to choose between microservices and a monolithic architecture.

## Decision
Use a modular Django monolith with clear app boundaries.

## Rationale
- **Simplicity**: One deployment, one database, one codebase.
- **Speed**: No network overhead between components.
- **Transactions**: Full ACID transactions across all models.
- **Team size**: A single developer doesn't benefit from service boundaries.
- **Extractable**: Well-defined Django apps with service layers can be extracted into services later.

## Architecture Rules
1. Each Django app owns its own models, services, and API
2. Apps communicate through service functions, not direct model imports
3. No circular dependencies between apps
4. Shared utilities go in `apps.common`
5. Views are thin — business logic lives in services
6. Complex reads use selectors
