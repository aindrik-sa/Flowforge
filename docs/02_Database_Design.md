# FlowForge — Database Design

## Principles

- **UUID primary keys** for all application models (via `BaseModel`)
- **Timestamps** (`created_at`, `updated_at`) on all models
- **Foreign keys** with appropriate `on_delete` behavior
- **Database constraints** to enforce business rules
- **Indexes** on frequently queried fields
- **No unnecessary denormalization**

## BaseModel

All application models inherit from `BaseModel`:

```python
class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

### Why UUIDs?

- Safe to expose in URLs (no sequential guessing)
- Globally unique across tables and services
- Compatible with future service extraction
- No need for auto-increment coordination

## Sprint 1 Schema

### User

```
┌─────────────────────────────────┐
│ accounts_user                   │
├─────────────────────────────────┤
│ id          UUID PK             │
│ email       VARCHAR UNIQUE      │
│ password    VARCHAR             │
│ first_name  VARCHAR(150)        │
│ last_name   VARCHAR(150)        │
│ is_staff    BOOLEAN             │
│ is_active   BOOLEAN             │
│ is_superuser BOOLEAN            │
│ last_login  DATETIME NULL       │
│ created_at  DATETIME            │
│ updated_at  DATETIME            │
├─────────────────────────────────┤
│ UNIQUE(email)                   │
└─────────────────────────────────┘
```

## Performance Guidelines

- Use `select_related()` for ForeignKey joins
- Use `prefetch_related()` for reverse/M2M relations
- Add `db_index=True` on frequently filtered fields
- Use `annotate()` / `aggregate()` instead of Python-side computation
- Wrap multi-step writes in `transaction.atomic()`
- Never return unbounded querysets from API endpoints
