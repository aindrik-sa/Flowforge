# ADR-001: Use UUID Primary Keys

## Status
Accepted

## Context
We need to choose a primary key strategy for all application models.

Options:
1. Auto-incrementing integers (Django default)
2. UUIDs

## Decision
Use UUID v4 as the primary key for all application models via `BaseModel`.

## Rationale
- **Security**: Sequential IDs leak information (total count, creation order). UUIDs are opaque.
- **URL safety**: UUIDs can be safely exposed in URLs without enabling enumeration attacks.
- **Distributed readiness**: If we ever split into services, UUIDs are globally unique without coordination.
- **Merge-friendly**: No conflicts when importing/exporting data between environments.

## Trade-offs
- Slightly larger storage (16 bytes vs 4-8 bytes)
- Less human-readable in logs
- No natural ordering (use `created_at` instead)

## Implementation
```python
class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
```
