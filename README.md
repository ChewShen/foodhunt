# FoodHunt

[![CI](https://github.com/ChewShen/foodhunt/actions/workflows/ci.yml/badge.svg)](https://github.com/ChewShen/foodhunt/actions/workflows/ci.yml)
![Version](https://img.shields.io/badge/version-2.0.0--alpha.1-blue)
![Python](https://img.shields.io/badge/python-3.13-blue)

An ETL pipeline that pulls restaurant data for the Klang Valley from OpenStreetMap, cleans it, and serves it through a geo-aware REST API.

> **Status: early rewrite.** The foundation is in place; the pipeline and API are being built. See the [roadmap](docs/ROADMAP.md).

## Background

FoodHunt started in 2025 as a university project: a Django site that listed restaurants in SS15, Mid Valley and Cyberjaya, filled by a one-off OpenStreetMap import script. That version is archived at [ChewShen/foodhunt-archive](https://github.com/ChewShen/foodhunt-archive).

Version 2 is a ground-up rewrite. It treats the data pipeline as the product: repeatable runs, a record of every run, data quality checks and spatial queries, rather than a website with an import script attached. The reasoning behind this and other choices is in the [decision log](docs/decisions.md).

## How it works

```
OpenStreetMap ──extract──▶ raw layer ──transform──▶ clean places ──▶ REST API
 (Overpass)                (untouched   (pure functions,  (PostGIS,
                           payloads,    validation,       upsert on
                           per run)     quarantine)       OSM id)
                                 └──────── run history ────────┘
```

Planned design, being built in stages:

- **Extract** fetches restaurants for each configured area and stores the untouched response, tagged with the run that fetched it.
- **Transform** turns raw records into clean ones with pure functions that are tested without a database or network.
- **Load** upserts on the OSM id, so re-running changes nothing, and marks places that disappear from OSM as closed.
- **Run history** records counts and duration for every run.

## Stack

- Python 3.13, Django 6.1 + GeoDjango, Django REST Framework
- PostgreSQL 17 + PostGIS 3.5
- uv for dependencies, ruff for lint and format, pytest
- Docker Compose for local development, GitHub Actions for CI

## Running locally

Requires Docker.

```sh
cp .env.example .env          # optional; compose sets dev defaults
docker compose up --build     # app on http://localhost:8000
curl localhost:8000/health/   # {"status": "ok", "database": "ok"}
```

If port 8000 is taken, use another one: `WEB_PORT=8001 docker compose up`.

The official PostGIS image has no arm64 build, so on Apple Silicon the database runs under emulation. It is slower but identical to CI.

### Tests and checks

```sh
docker compose run --rm web pytest
docker compose run --rm web ruff check .
docker compose run --rm web ruff format --check .
```

CI runs the same checks, plus a missing-migration check, on every push and pull request.

### Configuration

All settings come from environment variables; see [`.env.example`](.env.example). With `DJANGO_DEBUG` off, the app requires `DJANGO_SECRET_KEY` and enforces HTTPS and secure cookies.

## Project layout

```
config/     Django settings, root URLs, health check
places/     Clean restaurant data and the public API
pipeline/   Extract → transform → load, run history, data quality
tests/      pytest suite
docs/       Roadmap, changelog, decision log, contributing guide
```

## Roadmap

Foundation ✅ → **Pipeline core** 🚧 → Data quality → Scheduled runs → REST API → Frontend → Deployment

Milestones, task checklists and progress are tracked in [docs/ROADMAP.md](docs/ROADMAP.md).

## Documentation

- [Roadmap](docs/ROADMAP.md): what's planned and how far along it is
- [Changelog](docs/CHANGELOG.md): what changed in each version
- [Decision log](docs/decisions.md): why things are built the way they are
- [Contributing](docs/CONTRIBUTING.md): branching, merging and release flow

## Data attribution

Restaurant data © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), available under the [Open Database License](https://opendatacommons.org/licenses/odbl/).
