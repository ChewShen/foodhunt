# FoodHunt

ETL pipeline + geo API (Django 6.1, GeoDjango, PostGIS). Everything runs in Docker; GDAL isn't installed on the host.

## Git workflow

Follow [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md):

- Never commit to `main`. Work on the `chewshen` branch.
- Merge into `main` only with a merge commit or `--ff-only`; never squash or rebase merges. Afterwards fast-forward `chewshen` to `main`.
- Tags (`vX.Y.Z`, SemVer spelling) are created on `main` only, after the release commit is merged.
- Update `docs/CHANGELOG.md` under **Unreleased** for user-visible changes, and add to `docs/decisions.md` for real trade-offs.

## Commands

```sh
docker compose up -d                       # WEB_PORT=8001 if 8000 is taken
docker compose run --rm -T web pytest
uv run ruff check . && uv run ruff format --check .
```
