# Expense Tracker API

The backend is a single FastAPI service for authentication, transactions, and history summaries. The Next.js app is local first and works without this service; this API is available when a user wants an account or server backed data.

## Run locally

Use Python 3.10 or newer and PostgreSQL. Create the database, then run `db/init.sql`. Configure `fastapi/.env`:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=expense_db
DB_USER=expense_user
DB_PASSWORD=change-me
JWT_SECRET=replace-with-a-long-random-secret
PORT=8000
CORS_ORIGINS=http://localhost:3000,capacitor://localhost,http://localhost
```

```sh
cd fastapi
python -m venv .venv
# Activate the virtual environment, then:
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API docs are served at `/docs`; `/health` is a liveness endpoint. Docker builds use the same FastAPI app and expect database and JWT settings as runtime environment variables. Do not put secrets in the image.

## Routes

| Purpose | Route |
| --- | --- |
| Sign up / login / profile / refresh | `/api/auth/*` |
| Account aliases | `/api/users/*` |
| Create, list, read, update, delete transactions | `/api/transactions/*` |
| Monthly summary | `/api/transactions/summary/monthly` |
| Balance, income, expense, recent history | `/api/history/*` |

All account and transaction routes except signup/login/refresh require a Bearer access token. History derives the user from the token; clients must not supply another user's ID. Existing public `users` and `transactions` tables are used, including the `savings` transaction type.

## Deployment

Build from `fastapi/`. The service listens on `PORT` (default 8000). Provide `DATABASE_URL` or the individual `DB_*` values, plus `JWT_SECRET`, through the deployment environment.
