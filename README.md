# FastAPI Music API — Heroku Fixed v3

This version is configured for a normal Heroku Python buildpack deployment.

## IMPORTANT

Do NOT add `heroku.yml`.
Do NOT use Docker/container deployment for this project.

Required root files:

```text
app/
Procfile
requirements.txt
.python-version
app.json
.gitignore
```

## Heroku

Connect your GitHub repository:

1. Heroku Dashboard
2. Open your app
3. Deploy
4. Deployment method: GitHub
5. Select repository
6. Select `main`
7. Deploy Branch

Heroku should detect the Python buildpack from `app.json`.

## Config Vars

In Heroku Settings -> Config Vars:

```text
API_KEYS=your-long-random-secret
CACHE_TTL=300
```

Never commit a real secret to GitHub.

## Test

After deployment:

```text
/
 /api/health
 /docs
```

Search:

```text
/api/search?q=Arijit&limit=5
```

If API_KEYS is configured, send:

```text
X-API-Key: your-long-random-secret
```

## Local

```bash
python -m venv .venv
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

This project provides search and metadata functionality. Do not use it to
host or redistribute copyrighted audio without authorization.
