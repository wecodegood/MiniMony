# MiniMony

MiniMony is a lightweight price search aggregator for Persian marketplaces. It combines a Flask web interface with browser-based scraping modules to collect and present low-price listings from supported sites.

## What this project includes

- `run_flask.py` — helper entry point for running the Flask web app
- `src/gui/web/main.py` — Flask application and search UI
- `src/main.py` — scraper runner that discovers and executes marketplace scraper modules
- `src/scraptor/` — scraper implementations for marketplaces such as Divar, Torob, and Digikala
- `src/json/` — runtime output directory for scraper JSON results (ignored by git)

## Requirements

- Python 3.12+
- `pip`
- `playwright`

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python3 -m playwright install firefox
```

## Run the web app

```bash
python run_flask.py
```

Then open `http://127.0.0.1:5000` in your browser.

## Run scrapers directly

```bash
python src/main.py
```

This will discover scraper modules under `src/scraptor/` and execute them.

## Notes

- Generated runtime artifacts such as `src/json/*.json` and `*.pyc` files are ignored by git.
- If a scraper fails, the web UI may fall back to cached or mock results.
- Use the `requirements.txt` file to install dependencies in a clean environment.

## Project structure

- `src/gui/web/` — Flask templates, static assets, and web app logic
- `src/scraptor/` — marketplace scraper modules
- `src/main.py` — scraper orchestration and parallel runner
- `README_LIVE_SHARE.md` — Live Share helper instructions

## Cleanup

This repository now excludes generated artifacts and keeps the source code and documentation ready for use.
