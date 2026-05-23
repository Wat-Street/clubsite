# Clubsite

Wat Street's public-facing site and home for our project demos. Built with Next.js (App Router) for the frontend; project pages can be backed by their own service when they need live data.

## Architecture

```
Browser ──► Next.js (localhost:3000)
                │
                │  fetch("/api/...")
                ▼
       next.config.mjs rewrites /api/*
                │
                ▼
       Flask API  (localhost:5050)
                │
                │  yfinance
                ▼
         Yahoo Finance
```

The Next dev server proxies `/api/*` to the correlation backend, so the browser only ever talks to `localhost:3000`. No CORS gymnastics in dev.

## Running locally

You need **two** processes running side-by-side: the Next site and the correlation Flask API. Open two terminals.

### Terminal 1 — Next.js site

```bash
npm install
npm run dev
```

Site comes up at http://localhost:3000.

### Terminal 2 — Correlation Trading API

```bash
cd correlation-api
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

API comes up at http://localhost:5050. Health check: `curl http://localhost:5050/api/pairs`.

### Verify end-to-end

Open http://localhost:3000, click **Correlation Trading** under projects, pick a pair. You should see:

1. A pair-selector grid (the 14 pre-configured pairs, each with a live signal badge)
2. After clicking a pair: lag-correlation chart, spread + z-score charts, metrics, histogram

If the page loads but charts say "Could not load data", the Flask API isn't running on 5050.

## Repository layout

```
clubsite/
├── app/                          # Next.js routes
│   ├── page.tsx                  # Landing page
│   ├── research/                 # Research blog
│   └── correlation-trading/      # Project page
├── components/
│   ├── clubsite/                 # Site chrome (header, footer, landing)
│   └── correlation/              # Charts, selectors, panels for the project page
├── lib/
│   ├── data.ts                   # Static content (project list, team, etc.)
│   └── correlationTypes.ts       # Shared types for the project page
├── correlation-api/              # Flask backend — see its README for details
└── next.config.mjs               # /api/* rewrite lives here
```

## Adding a project

1. Add a route under `app/<slug>/page.tsx`
2. Append an entry to the project list in `lib/data.ts`
3. If it needs a backend, add a sibling directory (e.g. `clubsite/<name>-api/`) and extend `next.config.mjs` with another rewrite rule

## Deployment

```
Browser ──► Netlify (Next.js site)
                │  /api/* rewrite (next.config.mjs)
                ▼
       Render (Flask correlation-api)
                │
                ▼
         Yahoo Finance
```

- **Frontend** deploys to Netlify from `main` (current site: `watstreet.netlify.app`).
- **Backend** deploys to Render from `main` via `render.yaml`. The service builds from `correlation-api/`, installs `requirements.txt`, and runs `gunicorn`.
- The rewrite destination is parameterised: `next.config.mjs` reads `CORRELATION_API_URL` and falls back to `http://localhost:5050` for local dev.

### First-time setup

1. **Render** — In the Render dashboard, create a new Blueprint from this repo. It picks up `render.yaml` and provisions the `correlation-api` service automatically. Copy the resulting URL (e.g. `https://correlation-api-xxxx.onrender.com`).
2. **Netlify** — Add an environment variable `CORRELATION_API_URL` set to the Render URL above, then trigger a redeploy. The Next rewrite now proxies `/api/*` to Render.

### Notes

- Render's free tier spins down after 15 min of inactivity. First request after a cold start takes ~30s.
- After any change to `correlation-api/`, Render auto-redeploys on push to `main`.
- The `/api/*` rewrite is server-side (Netlify proxies to Render), so the browser only ever sees the Netlify domain — no CORS gymnastics needed.
