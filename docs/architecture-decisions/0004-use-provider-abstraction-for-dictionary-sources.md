# 0004 Use Provider Abstraction For Dictionary Sources

## Context

The first dictionary source will be Free Dictionary API, but external APIs can change, fail, or be replaced.

## Decision

Access dictionary sources through a provider abstraction instead of coupling application code directly to one API.

## Consequences

The project can add or replace providers later with less disruption. The abstraction adds a small amount of design work upfront, but it keeps external API details out of core glossary workflows.
