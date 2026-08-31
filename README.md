# Custom Music API — Heroku Ready

## Files

- `app.py`
- `requirements.txt`
- `Procfile`
- `runtime.txt`
- `app.json`

This version intentionally uses Heroku's **Python buildpack**, not a Docker/heroku.yml build.

## Deploy

```bash
unzip custom-music-api-heroku-fixed.zip
cd music_api_fixed

heroku login
heroku create YOUR-UNIQUE-APP-NAME
heroku config:set API_KEY="CHANGE_ME_TO_A_LONG_RANDOM_SECRET"
git init
git add .
git commit -m "Initial Heroku Music API"
git branch -M main
git push heroku main
heroku ps:scale web=1
```

## Test

Public health check:

```bash
curl https://YOUR-APP.herokuapp.com/api/health
```

Protected search:

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
"https://YOUR-APP.herokuapp.com/api/search?q=Arijit%20Singh&limit=5"
```

Protected info:

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
"https://YOUR-APP.herokuapp.com/api/info?id=VIDEO_ID"
```

## Important

Do not put your real API key in GitHub or in source code.

This API provides YouTube search/metadata. Do not use it to bypass platform restrictions or redistribute copyrighted audio without the required rights/permissions.
