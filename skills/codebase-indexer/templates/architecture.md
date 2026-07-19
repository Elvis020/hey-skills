# Architecture

## Project Type
[Stack name, e.g., "Spring Boot 3 REST API (Java 21)"]

## Directory Map
[Top-level tree, 3 levels max — omit build artifacts]

## Module Overview
| Module/Package | Purpose |
|---|---|
| `module-name` | One-line description |

## Execution Entry Map
| Entry Point | Type | Notes |
|---|---|---|
| `src/main.py:main` | CLI/Runtime | Process start |
| `src/server.ts:app.listen` | HTTP | Public API bootstrap |

## Data Flow
[Prose or simple diagram: how a request moves through the system]

## Multi-Layer Context Artifacts
| Artifact | Location | Why It Matters |
|---|---|---|
| Database schema | `schema.prisma` / `*.sql` | Data model and constraints |
| API contract | `openapi*.yaml` / `openapi*.json` | Endpoint definitions and payload shapes |
| Runtime topology | `docker-compose*.yml` | Service boundaries and integration points |

## External Dependencies
| Name | Purpose |
|---|---|
| `library-name` | What it does |
