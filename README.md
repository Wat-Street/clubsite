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

## Production notes

The `/api/*` rewrite targets `http://localhost:5050`, which only works locally. For production, replace the rewrite destination with the deployed API URL (or front the Flask service behind the same domain).
