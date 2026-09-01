# E-commerce Price Tracker

A portfolio-ready Python app for monitoring Amazon and Flipkart product prices. Add a product URL and target price; the app fetches structured product data, saves a history of observed prices, and sends a SendGrid email when a target is reached.

> Respect each retailer's terms of use and robots policy. The tracker is deliberately rate-limited and intended for personal monitoring only.

## Features

- Dashboard with current price, target price, retailer, and price-change status
- Amazon and Flipkart extraction with JSON-LD fallback patterns
- Persistent SQLite storage (replaceable with any SQLAlchemy-supported database)
- Price history and a JSON API for charts/integrations
- SendGrid alerting, with safe no-op behavior until credentials are configured
- Daily scheduler and a CLI suitable for Windows Task Scheduler or cron
- Docker, Render, and GitHub Actions deployment/automation configuration

## Run locally

```bash
python -m venv .venv
.venv\\Scripts\\activate  # Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000`. Add products from the dashboard, then use **Check now** to fetch their latest prices.

## Scheduled checks

For an always-on process, run `python -m app.scheduler`. For Windows Task Scheduler, create a daily task whose program is your virtualenv's `python.exe` and whose arguments are `-m app.jobs`; set the start directory to the project folder. On Linux cron, use:

```cron
0 9 * * * /path/to/python -m app.jobs
```

## Deploy

The included [`render.yaml`](render.yaml) creates a web service and an independent daily cron job. Add `SENDGRID_API_KEY`, `ALERT_FROM_EMAIL`, and `ALERT_TO_EMAIL` as environment variables in your deployment dashboard. For a durable production database, set `DATABASE_URL` to a managed Postgres URL.

GitHub Actions runs the test suite on pushes and pull requests. The daily workflow is an optional alternative scheduler, but needs the same environment secrets and a publicly reachable deployed API; the Render cron is simpler for this project.

## API

- `GET /api/products` — tracked products
- `GET /api/products/{id}/history` — chronological saved prices
- `POST /api/products/{id}/check` — check one product
