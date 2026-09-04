# ADR-004: PostgreSQL as Primary Database

## Status
Accepted

## Context
We need to choose a database for an enterprise project management platform.

## Decision
Use PostgreSQL 17 as the primary (and only) database.

## Rationale
- **Industry standard**: Most production Django applications use PostgreSQL.
- **Feature-rich**: Full-text search, JSON fields, array fields, CTEs, window functions.
- **Constraints**: CHECK constraints, exclusion constraints, partial indexes.
- **Concurrency**: MVCC with excellent write throughput.
- **Future-ready**: Full-text search eliminates the need for Elasticsearch initially.

## Trade-offs
- Requires a running PostgreSQL instance (solved with Docker)
- Slightly more complex setup than SQLite

## Configuration
- Docker container: `postgres:17`
- Host port: `5433` (avoids conflict with local PostgreSQL)
- Internal port: `5432`
- Database: `flowforge`
