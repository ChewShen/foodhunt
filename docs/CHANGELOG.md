# Changelog

All notable changes to this project are recorded here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses [Semantic Versioning](https://semver.org/). Python package versions use the [PEP 440](https://peps.python.org/pep-0440/) spelling (for example `2.0.0a1` for `2.0.0-alpha.1`).

## [Unreleased]

### Planned
- Pipeline: raw OSM layer, pure transforms, upsert keyed on OSM id, run history.
- Data quality checks with a quarantine table for rejected rows.
- Scheduled pipeline runs.
- REST API with geo queries (nearby, within area).

## [2.0.0-alpha.1] - 2026-10-05

Ground-up rewrite in a new repository. The original code is archived at [ChewShen/foodhunt-archive](https://github.com/ChewShen/foodhunt-archive).

### Added
- Django 6.1 project with GeoDjango, and empty `places` and `pipeline` apps.
- PostgreSQL 17 + PostGIS 3.5 via Docker Compose.
- Settings driven by environment variables, with production HTTPS and secure-cookie defaults.
- `/health/` endpoint that checks database connectivity.
- Smoke tests for the health check and the PostGIS extension.
- GitHub Actions CI: ruff lint and format check, missing-migration check, pytest against PostGIS.
- Dependency management with uv and a committed lockfile.
- `docs/` with this changelog, the decision log, and the branching and release workflow (`CONTRIBUTING.md`).

### Changed
- The project's focus moves from a restaurant listing site to the data pipeline and API behind it. See [decisions](decisions.md).

### Removed
- Everything from 1.x. Nothing is carried over as-is; the old import logic is used only as a reference.

## [1.0.0] - 2025-12-08

The original university project, recorded after the fact from the archived git history. It was not versioned at the time.

### Added
- Django site listing restaurants by area, with name search, a multi-select cuisine filter, sorting and pagination.
- "Pick a random restaurant" JSON endpoint.
- `fetch_shops` management command that imported restaurants from OpenStreetMap with osmnx for SS15, Mid Valley and Cyberjaya.
- Tailwind CSS styling.
- Deployment to Railway with PostgreSQL.

[Unreleased]: https://github.com/ChewShen/foodhunt/compare/v2.0.0-alpha.1...HEAD
[2.0.0-alpha.1]: https://github.com/ChewShen/foodhunt/releases/tag/v2.0.0-alpha.1
[1.0.0]: https://github.com/ChewShen/foodhunt-archive
