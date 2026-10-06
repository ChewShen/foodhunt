# Roadmap

What is planned, in order, and how far along it is. Each milestone ends in a tagged release; what actually shipped is recorded in the [changelog](CHANGELOG.md), and the reasoning behind design choices in the [decision log](decisions.md).

Tick items off in the same pull request that completes them. Plans change: edit, reorder or drop items freely, and note anything significant in the decision log.

**Status:** ✅ done · 🚧 in progress · ⏳ not started

| Milestone | Version | Status |
| --- | --- | --- |
| [1. Foundation](#1-foundation) | 2.0.0-alpha.1 | ✅ 2026-10-05 |
| [2. Pipeline core](#2-pipeline-core) | 2.0.0-alpha.2 | 🚧 |
| [3. Data quality](#3-data-quality) | 2.0.0-alpha.3 | ⏳ |
| [4. Scheduled runs](#4-scheduled-runs) | 2.0.0-alpha.4 | ⏳ |
| [5. REST API](#5-rest-api) | 2.0.0-beta.1 | ⏳ |
| [6. Frontend](#6-frontend) | 2.0.0-beta.2 | ⏳ |
| [7. Deployment](#7-deployment) | 2.0.0 | ⏳ |

---

## 1. Foundation

Released as 2.0.0-alpha.1.

- [x] Django + GeoDjango project with `places` and `pipeline` apps
- [x] PostgreSQL + PostGIS via Docker Compose
- [x] Settings from environment variables, production security defaults
- [x] `/health/` endpoint and smoke tests
- [x] CI: lint, format, migration check, tests against PostGIS
- [x] Docs: changelog, decision log, contributing guide, roadmap

## 2. Pipeline core

Turn OpenStreetMap data into clean, deduplicated places, repeatably. See decision D-10.

Step 1: models and loading, tested offline against saved sample data:

- [ ] `Area` and `Place` models; seed SS15, Mid Valley and Cyberjaya
- [ ] `PipelineRun` (one per area, with counts and duration) and `RawRecord` (untouched payloads)
- [ ] Pure transform functions from raw OSM element to clean place
- [ ] Load: upsert on OSM id, detect unchanged rows, close places that disappear, reopen ones that return
- [ ] Tests: re-running changes nothing; chain branches in one area are kept apart; an empty extract closes nothing

Step 2: real data:

- [ ] Overpass extractor
- [ ] `run_pipeline` management command (all areas or one)
- [ ] First real run, browsable in the admin
- [ ] Replay a past run from raw data without calling OSM

## 3. Data quality

- [ ] Normalise phone numbers to Malaysian E.164 (`+60…`)
- [ ] Validate and normalise website URLs
- [ ] Parse `opening_hours` where possible; keep the raw value otherwise
- [ ] Quarantine table for rejected records, with the reason
- [ ] Data quality summary per run (fill rate per field, rejection reasons)

## 4. Scheduled runs

See decision D-11.

- [ ] Prevent overlapping runs with a database lock
- [ ] Retry transient Overpass failures with backoff
- [ ] Retention policy for raw records
- [ ] Schedule runs locally with cron (production schedule comes with deployment)

## 5. REST API

- [ ] List and detail endpoints for places and areas
- [ ] Filters: area, cuisine, name search, open or closed
- [ ] Geo queries: nearby (point and radius), sorted by distance
- [ ] Random pick, carried over from 1.x
- [ ] Pipeline run history endpoint
- [ ] OpenAPI schema and interactive docs
- [ ] OpenStreetMap attribution in responses

## 6. Frontend

A thin client of the API, rebuilt from the 1.x pages in [foodhunt-archive](https://github.com/ChewShen/foodhunt-archive).

- [ ] Landing page
- [ ] Browse by area with search, cuisine filter, sorting and pagination
- [ ] "Pick for me" random restaurant
- [ ] Map view
- [ ] OpenStreetMap attribution

## 7. Deployment

See decision D-6.

- [ ] Choose a host that supports PostGIS (recorded as a decision)
- [ ] Deploy from `main` with production settings
- [ ] Scheduled pipeline runs in production
- [ ] Live URL in the README; enable HSTS once the domain is permanent (D-9)

## Later

Ideas, not commitments.

- A second data source, merged and deduplicated against OSM (check its licence first)
- More areas across the Klang Valley
- Metrics and alerting for pipeline runs
