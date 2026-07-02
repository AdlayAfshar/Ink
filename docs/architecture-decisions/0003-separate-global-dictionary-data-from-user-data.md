# 0003 Separate Global Dictionary Data From User Data

## Context

Dictionary definitions are shared facts, while saved words, notes, tags, and review progress belong to individual users.

## Decision

Model global dictionary data separately from user-specific learning data.

## Consequences

Shared word data can be cached and reused across users. User data remains private and easier to reason about. Queries may require joins between shared word tables and user-owned tables.
