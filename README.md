# FoodHunt

An ETL pipeline that pulls restaurant data for the Klang Valley from OpenStreetMap, cleans it, and serves it through a geo-aware REST API.

Rebuilt from a university project. The original was a Django site backed by a one-off OSM import script; this version treats the pipeline as the product.

> Work in progress — see [Roadmap](#roadmap).

## Stack

- Python 3.13, Django + GeoDjango, Django REST Framework
- PostgreSQL 17 + PostGIS 3.5
- uv for dependencies, ruff for lint/format, pytest
- Docker Compose for local development, GitHub Actions for CI

## Running locally

Requires Docker.

```sh
cp .env.example .env          # optional; compose sets sensible dev defaults
docker compose up --build     # app on http://localhost:8000
curl localhost:8000/health/
```

If port 8000 is taken, run `WEB_PORT=8001 docker compose up` instead.

The PostGIS image has no arm64 build, so on Apple Silicon it runs under emulation.

Run tests and checks inside the container:

```sh
docker compose run --rm web pytest
docker compose run --rm web ruff check .
```

## Project layout

```
config/     Django settings, root URLs, health check
places/     Clean restaurant data and the public API
pipeline/   Extract → transform → load, run history, data quality
tests/
```

## Roadmap

- [x] Foundation: Docker + PostGIS, settings from env, CI, health check
- [ ] Pipeline: raw OSM layer, pure transforms, upsert on OSM id, run log
- [ ] Data quality: normalisation, validation, quarantine of bad rows
- [ ] Scheduled runs
- [ ] REST API with geo queries (nearby, within area)
- [ ] Deployment
