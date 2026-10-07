# Decision log

Significant technical decisions, why they were made, and what they cost. New entries go at the bottom. A decision is never edited after it is accepted; if it changes, add a new entry that supersedes it and update the old one's status.

Status is one of **Proposed**, **Accepted**, or **Superseded by D-n**.

| #    | Decision                                         | Status   |
| ---- | ------------------------------------------------ | -------- |
| D-1  | Rewrite in a new repository                      | Accepted |
| D-2  | Make the pipeline the product                    | Accepted |
| D-3  | Stay on Django, add GeoDjango and DRF            | Accepted |
| D-4  | PostgreSQL with PostGIS                          | Accepted |
| D-5  | OpenStreetMap as the first data source           | Accepted |
| D-6  | Develop with Docker Compose, defer hosting       | Accepted |
| D-7  | Configuration from environment variables only    | Accepted |
| D-8  | uv and ruff for tooling                          | Accepted |
| D-9  | Leave HSTS off by default                        | Accepted |
| D-10 | Keep raw data, upsert on OSM id                  | Accepted |
| D-11 | Start scheduling with cron, not Celery           | Proposed |
| D-12 | One working branch merged into main              | Accepted |
| D-13 | Query Overpass directly, not through osmnx       | Accepted |
| D-14 | One run per area; areas must not overlap         | Accepted |

---

## D-1: Rewrite in a new repository

**Date:** 2026-10-05 · **Status:** Accepted

**Context.** The 1.x code was a university project: no tests, no README, committed `node_modules` and uploads, dead code, and a git history of seven commits. The local copy had also drifted from what git tracked.

**Decision.** Start a clean repository at `ChewShen/foodhunt` and rename the original to `ChewShen/foodhunt-archive`.

**Consequences.** A clean history that shows how the project is built, step by step. Nothing worth keeping is lost: the archive stays public and is linked from the README and changelog. The old import command is reread for reference, not copied.

## D-2: Make the pipeline the product

**Date:** 2026-10-05 · **Status:** Accepted

**Context.** Restaurant finder sites are a common portfolio project. The interesting engineering in 1.x was the OpenStreetMap import, but it was a single script with no idempotency, no history and no data checks.

**Decision.** Design the project around the ETL pipeline and the API that serves its output. Any frontend is a thin consumer.

**Consequences.** Effort goes into idempotent loads, run history, data quality and geo queries. The UI gets minimal attention.

## D-3: Stay on Django, add GeoDjango and DRF

**Date:** 2026-10-05 · **Status:** Accepted

**Context.** FastAPI was the main alternative. 1.x was already Django.

**Decision.** Keep Django. Use GeoDjango for spatial models and queries and Django REST Framework for the API.

**Consequences.** The admin, migrations and ORM come for free, and GeoDjango is a mature PostGIS integration. GeoDjango needs the GDAL/GEOS system libraries, so the app runs in Docker rather than directly on macOS.

## D-4: PostgreSQL with PostGIS

**Date:** 2026-10-05 · **Status:** Accepted

**Context.** 1.x stored latitude and longitude as plain floats, which rules out efficient "within X metres" queries.

**Decision.** Use PostgreSQL 17 with PostGIS 3.5, the official `postgis/postgis` image locally and in CI.

**Consequences.** Real spatial indexes and distance queries. The official image has no arm64 build, so on Apple Silicon it runs under amd64 emulation (`platform: linux/amd64` in `compose.yaml`). That is slower but keeps local and CI identical. Hosting options are limited to providers that support the PostGIS extension.

## D-5: OpenStreetMap as the first data source

**Date:** 2026-10-05 · **Status:** Accepted

**Context.** The data must be free to use and redistribute in a public project.

**Decision.** Use OpenStreetMap through the Overpass API (via osmnx or direct queries, decided when the extractor is built).

**Consequences.** The data is licensed under the [ODbL](https://opendatacommons.org/licenses/odbl/), which requires attribution ("© OpenStreetMap contributors") anywhere the data is shown or served. OSM coverage in Malaysia is uneven: fields such as `price` and `opening_hours` are often missing, which shapes what the data quality checks can promise. A second source may be added later, subject to its licence.

## D-6: Develop with Docker Compose, defer hosting

**Date:** 2026-10-05 · **Status:** Accepted

**Context.** 1.x was hosted on Railway, whose free tier has since expired. Free hosting tiers change often.

**Decision.** Run everything locally with Docker Compose. Choose a host when there is something worth deploying.

**Consequences.** No hosting cost or lock-in during development. The image is already production-shaped (gunicorn, whitenoise, non-root user, `PORT` variable) so most container hosts will work. The decision on a host gets its own entry.

## D-7: Configuration from environment variables only

**Date:** 2026-10-05 · **Status:** Accepted

**Context.** 1.x mixed hardcoded values with environment variables and had `ALLOWED_HOSTS = ['*']`.

**Decision.** All environment-specific settings come from environment variables, documented in `.env.example`. With `DJANGO_DEBUG` off, the app refuses to start without `DJANGO_SECRET_KEY`.

**Consequences.** The same image runs locally, in CI and in production. Misconfiguration fails loudly at startup instead of running insecurely.

## D-8: uv and ruff for tooling

**Date:** 2026-10-05 · **Status:** Accepted

**Decision.** uv manages Python, dependencies and the lockfile. ruff handles both linting and formatting. pytest with pytest-django runs the tests.

**Consequences.** Fast, reproducible installs from `uv.lock` in Docker and CI. One tool replaces flake8, isort and black.

## D-9: Leave HSTS off by default

**Date:** 2026-10-05 · **Status:** Accepted

**Context.** `manage.py check --deploy` warns that `SECURE_HSTS_SECONDS` is unset.

**Decision.** Keep HSTS off until the site has a permanent HTTPS domain. It can be enabled with `DJANGO_SECURE_HSTS_SECONDS`.

**Consequences.** One known deploy-check warning remains. This is deliberate: browsers cache HSTS, so enabling it on a temporary or misconfigured domain is hard to undo.

## D-10: Keep raw data, upsert on OSM id

**Date:** 2026-10-05 · **Status:** Accepted (implemented 2026-10-07)

**Context.** 1.x used `get_or_create(name, area)`. Two branches of the same chain in one area collapsed into one row, and changes in OSM never reached the database.

**Decision.** Store each extract's untouched payload in a raw table tagged with the run that fetched it. Transform it with pure functions into the clean table, upserting on `(osm_type, osm_id)`. Places missing from a later extract are marked closed rather than deleted. Every run is recorded with its counts and duration.

**Consequences.** Runs are idempotent and can be replayed from raw data without calling OSM again. Raw storage grows with each run, so it will need a retention policy.

## D-11: Start scheduling with cron, not Celery

**Date:** 2026-10-05 · **Status:** Proposed

**Context.** The pipeline needs to run periodically, a few times a day at most.

**Decision.** Run the pipeline as a management command triggered by cron or the host's scheduler. Add a task queue only if a real need appears.

**Consequences.** No broker or worker to operate. Retries and concurrency control must be handled inside the command, for example with a database lock to prevent overlapping runs.

## D-12: One working branch merged into main

**Date:** 2026-10-05 · **Status:** Accepted

**Context.** Committing straight to `main` means unreviewed, possibly failing code lands on the branch that releases are tagged from. A branch per feature or fix is the usual remedy, but it is a lot of ceremony for one person working on a side project.

**Decision.** `main` only receives merges. All work happens on a single long-lived branch, `chewshen`, which is merged into `main` through a GitHub pull request with a merge commit, never a squash or rebase. Releases are tagged on the merge commit. The full flow is in [CONTRIBUTING.md](CONTRIBUTING.md).

**Consequences.** `main` stays green and every tag points at code that passed CI. The cost is keeping `chewshen` in sync after each merge; squash or rebase merges would break that, which is why they are ruled out. CI runs on pushes to both branches.

## D-13: Query Overpass directly, not through osmnx

**Date:** 2026-10-07 · **Status:** Accepted

**Context.** 1.x used osmnx, which returns a GeoDataFrame and pulls in geopandas, shapely, pyproj and pandas. D-5 left the choice open until the pipeline was built.

**Decision.** Call the Overpass API directly and ask for `out center tags`, so every element arrives as plain JSON with either its own coordinates (nodes) or a centre point (ways and relations).

**Consequences.** The raw layer stores exactly what Overpass returned, which is what makes replaying a run possible. The transform reads a small, documented format, and the dependency list stays short. The cost is writing the Overpass query and HTTP handling ourselves, including retries and Overpass's rate limits.

## D-14: One run per area; areas must not overlap

**Date:** 2026-10-07 · **Status:** Accepted

**Context.** The load step closes places that a run no longer sees. It needs a clear rule for which places a run is responsible for.

**Decision.** Each pipeline run covers exactly one area, and a run can only close places in its own area. A place belongs to the area that last reported it. If an extract contains no usable places at all, nothing is closed, because that almost always means a bad response rather than every restaurant shutting down.

**Consequences.** A failure in one area doesn't affect the others, and the counts in each run are easy to read. Areas must not overlap: if two did, a place in both would move back and forth between them on each run. The three seeded areas are far apart, so this holds today; it needs checking when areas are added.
