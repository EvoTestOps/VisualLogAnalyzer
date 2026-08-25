# Testing VisualLogAnalyzer against an unreleased LogLead branch

Use this when you want to test LogLead changes on GitHub (a branch not yet
released to PyPI) against VisualLogAnalyzer.

## 1. Point requirements.txt at the branch

Edit [`requirements.txt`](../requirements.txt) and replace the pinned line
```
LogLead==1.2.3
```
with a direct URL to a source tarball of the branch:

```
LogLead @ https://github.com/EvoTestOps/LogLead/archive/refs/heads/<BRANCH_NAME>.tar.gz
```

Swap `<BRANCH_NAME>` for whichever branch you're testing, e.g. `feature/more-loaders`.

Note: this uses a plain HTTPS tarball, not a `git+https://...` reference —
a `git+` URL would need the `git` binary inside the build image, which the
`python:3.12-slim` base image doesn't include, and we don't want a
permanent Dockerfile change just for occasional branch testing.

## 2. Rebuild the Docker images

LogLead is installed at image build time (`Dockerfile` runs
`pip install -r requirements.txt`), so a container restart alone won't
pick up the change — you need to rebuild:

```bash
docker compose -f docker-compose-dev.yml build app celery
docker compose -f docker-compose-dev.yml up -d
```

(use `docker-compose.yml` instead of `docker-compose-dev.yml` if you're
not using the dev override).

If you re-run this later to pick up *new* commits pushed to the same
branch, Docker's layer cache won't notice the branch moved (the
requirements.txt text is unchanged), so force it:

```bash
docker compose -f docker-compose-dev.yml build --no-cache app celery
```

## 3. Verify what actually got installed

```bash
docker compose -f docker-compose-dev.yml exec app pip freeze | grep -i loglead
```

You should see the tarball URL you set in step 1, confirming the branch
version installed rather than the PyPI release, e.g.:

```
LogLead @ https://github.com/EvoTestOps/LogLead/archive/refs/heads/feature/more-loaders.tar.gz
```

## 4. Automated smoke test

Tests need the repo's bundled `log_data/LO2` mounted at `/app/log_data`, so (re)create the containers with `.env.sample` (`LOG_DATA_DIRECTORY=./log_data`) rather than your own `.env` — a plain `exec` on an already-running container won't change its mounts:

```bash
docker compose -f docker-compose-dev.yml --env-file .env.sample up -d --force-recreate app celery
docker compose -f docker-compose-dev.yml exec app pytest tests
curl -s http://localhost:5000/health
```

## 5. Switch back to your own data

Recreate `app`/`celery` again, this time without `--env-file .env.sample`, so they pick up your regular `.env` (e.g. `LOG_DATA_DIRECTORY=~/Datasets`) instead:

```bash
docker compose -f docker-compose-dev.yml up -d --force-recreate app celery
```

## 6. Running and Manual Testing

This repeats the relevant parts of [usage_guide.md](usage_guide.md) — see
that file for the full walkthrough and screenshots.

1. Make sure `LOG_DATA_DIRECTORY` and `RESULTS_DIRECTORY` in `.env` (or
   `.env.sample`) point at the correct folders:
   ```
   LOG_DATA_DIRECTORY=./log_data
   RESULTS_DIRECTORY=./analysis_results
   ```
2. Start the stack (already done in step 2 above if you rebuilt with
   `up -d`; otherwise `docker compose -f docker-compose-dev.yml --env-file
   .env up`).
3. Open <http://localhost:5000/dash/> in a browser.

## 7. Revert back to the released version when done

```
LogLead==1.2.3
```

then rebuild again (step 2). Don't leave a branch pin committed to `main`
long-term — it's a floating target (CI and anyone else building the image
would silently pick up whatever the branch currently contains).
