# Research

## Architectural Decision
Use a single `GET /dashboard` API.

### Reasons
- One network request
- Faster loading
- Simpler frontend
- Easier testing
- Easier caching

Rejected Alternative:
Multiple APIs from the Home page because they increase complexity.
