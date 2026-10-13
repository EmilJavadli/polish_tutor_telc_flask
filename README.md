# Polish Tutor Flask

Full Flask conversion of the Streamlit Polish Tutor architecture. The application keeps user-scoped PostgreSQL repositories, Google OIDC identity, placement, personalized starting positions, lessons, exercises, writing, speaking, quiz, audio and tutor chat. Browser actions use `fetch()` so lesson panels update without Streamlit reruns.

## Local setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python app.py
```

By default, local development uses SQLite and `DEV_LOGIN=1`. Open `http://127.0.0.1:5000`, then use the development login. For real Google login set `DEV_LOGIN=0`, configure Google variables, and register:

```text
http://127.0.0.1:5000/auth/callback
```

## PostgreSQL and migrations

Set `DATABASE_URL`, then run:

```powershell
python tools/migrate.py
```

The existing schema is user-scoped. Do not use the legacy shared file repository in production.

## Production deployment

Use Gunicorn:

```bash
gunicorn app:app --bind 0.0.0.0:$PORT
```

On Render/Railway set all values from `.env.example` as environment variables. Register the deployed Google callback URL:

```text
https://YOUR-DOMAIN/auth/callback
```

Set `DEV_LOGIN=0` in production.

## Media storage

Lessons and progress are stored in the database. Generated audio and speaking recordings currently use `data/audio/{user_id}`. For durable cloud deployment, replace local media storage with private object storage.

## Important conversion notes

- The uploaded placement modules mixed structured CEFR dictionaries with numeric scores. This package normalizes both formats and applies conservative skill gates.
- The generated lesson fallback in `agent/lesson_generator.py` is deterministic so the app works locally without OpenAI. Replace that module with the full uploaded production generator when maintaining the exact original prompt pipeline.
- Writing/speaking grading currently uses the uploaded CEFR placement grader for placement and a lightweight lesson feedback fallback. Your original AI graders can be dropped into the same endpoints.
