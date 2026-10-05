# Contributing and releasing

FoodHunt is a solo side project, so the workflow is deliberately light: one protected `main`, one working branch.

## Branches

| Branch     | Purpose                                                      |
| ---------- | ------------------------------------------------------------ |
| `main`     | Always passing CI and releasable. Never committed to directly. |
| `chewshen` | Long-lived working branch. All day-to-day commits go here.  |

There are no per-feature or per-fix branches. If a change ever needs isolating, a short-lived branch off `main` is fine, but it is the exception.

## Day-to-day work

```sh
git switch chewshen
# ...work, commit...
git push
```

## Merging into main

1. Make sure CI is green on `chewshen`.
2. Merge it into `main`, either way:
   - **On GitHub:** open a pull request from `chewshen` to `main` and use **Create a merge commit**.
   - **Locally:** `git switch main && git merge --ff-only chewshen && git push`.
3. Bring `chewshen` back in line with `main`:

   ```sh
   git switch chewshen
   git pull --ff-only origin main
   git push
   ```

**Never use "Squash and merge" or "Rebase and merge".** Both rewrite the commits, so `chewshen` and `main` stop sharing history and every later merge conflicts.

## Releasing

Versions follow [Semantic Versioning](https://semver.org/). Tags use the SemVer spelling (`v2.0.0-alpha.1`); `pyproject.toml` uses the equivalent [PEP 440](https://peps.python.org/pep-0440/) spelling (`2.0.0a1`).

On `chewshen`:

1. In [`CHANGELOG.md`](CHANGELOG.md), move the **Unreleased** entries under a new version heading with today's date, and update the comparison links at the bottom.
2. Set `version` in `pyproject.toml`, then run `uv lock` to update the lockfile.
3. Commit as `Release vX.Y.Z`.

Then merge into `main` as above, and tag the merge on `main`:

```sh
git switch main
git pull
git tag -a vX.Y.Z -m "vX.Y.Z"
git push origin vX.Y.Z
```

Tags are only ever created on `main`.

## Decisions

When a change involves a real trade-off (a new dependency, a schema design, a hosting choice), add an entry to [`decisions.md`](decisions.md) in the same commit.
