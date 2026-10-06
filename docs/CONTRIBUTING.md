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

1. Open a pull request from `chewshen` to `main` on GitHub.
2. When CI is green, merge it with **Create a merge commit**.
3. Fast-forward `chewshen` to the merge commit. `main` is never checked out locally, so it doesn't need pulling; only the fetch is needed, because the merge commit exists only on GitHub until then.

   ```sh
   git switch chewshen
   git fetch origin
   git merge --ff-only origin/main
   git push
   ```

**Never use "Squash and merge" or "Rebase and merge".** Both rewrite the commits, so `chewshen` and `main` stop sharing history and every later merge conflicts.

## Releasing

Versions follow [Semantic Versioning](https://semver.org/). Tags use the SemVer spelling (`v2.0.0-alpha.1`); `pyproject.toml` uses the equivalent [PEP 440](https://peps.python.org/pep-0440/) spelling (`2.0.0a1`).

On `chewshen`:

1. In [`CHANGELOG.md`](CHANGELOG.md), move the **Unreleased** entries under a new version heading with today's date, and update the comparison links at the bottom.
2. Set `version` in `pyproject.toml`, then run `uv lock` to update the lockfile.
3. Commit as `Release vX.Y.Z`.

Then merge the pull request and fast-forward `chewshen` as above, and tag the merge commit:

```sh
git tag -a vX.Y.Z -m "vX.Y.Z" origin/main
git push origin vX.Y.Z
```

Tags only ever point at merge commits on `main`.

## Keeping the docs current

Update these in the same commit as the change they describe:

- [`ROADMAP.md`](ROADMAP.md): tick off completed items and keep the milestone status table current.
- [`CHANGELOG.md`](CHANGELOG.md): add user-visible changes under **Unreleased**.
- [`decisions.md`](decisions.md): add an entry when a change involves a real trade-off (a new dependency, a schema design, a hosting choice).
