# FoodHunt

ETL pipeline + geo API (Django 6.1, GeoDjango, PostGIS). Everything runs in Docker; GDAL isn't installed on the host.

## Git workflow

Follow [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md):

- Never commit to `main`. Work on the `chewshen` branch.
- Merge into `main` only through a GitHub pull request with "Create a merge commit"; never squash or rebase merges, never push to `main` directly. Afterwards `git fetch origin && git merge --ff-only origin/main` on `chewshen`.
- Tags (`vX.Y.Z`, SemVer spelling) go on the PR merge commit (`origin/main`), after the release PR is merged.
- Update `docs/CHANGELOG.md` under **Unreleased** for user-visible changes, and add to `docs/decisions.md` for real trade-offs.
- Tick items in `docs/ROADMAP.md` in the same change that completes them, and keep its milestone status table current.

## Commands

```sh
docker compose up -d                       # WEB_PORT=8001 if 8000 is taken
docker compose run --rm -T web pytest
uv run ruff check . && uv run ruff format --check .
```
