# MiniMony

![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-experimental-orange)

Tired of opening multiple Persian marketplaces just to compare prices? MiniMony centralizes price search results from Divar, Torob, Digikala, and more into a single local web app.

## Quick start

```bash
git clone https://github.com/wecodegood/MiniMony.git
cd MiniMony
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python3 -m playwright install firefox
python run_flask.py
```

Open `http://127.0.0.1:5000` in your browser and search for a product.

## What MiniMony does

- Aggregates listings from multiple Persian marketplaces
- Uses browser automation to scrape search results
- Shows combined results in a clean local UI
- Keeps the testing setup simple and self-contained

## Features

- Flask web app for search and result display
- Marketplace scraper orchestration in `src/main.py`
- Playwright-powered scraping modules under `src/scraptor/`
- JSON result caching under `src/json/`
- Easy extendability for new marketplaces

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

## Run scrapers manually

```bash
python src/main.py
```

This discovers scrapers under `src/scraptor/` and runs each available module.

## Example workflow

1. Start the web app with `python run_flask.py`
2. Open `http://127.0.0.1:5000`
3. Enter a search query such as `گوشی` or `laptop`
4. Browse results from supported marketplaces

## Project structure

- `run_flask.py` — helper script for launching the Flask app
- `src/gui/web/main.py` — Flask application and search views
- `src/main.py` — scraper discovery and execution logic
- `src/scraptor/` — marketplace scraper modules
- `src/json/` — runtime output directory (ignored by git)
- `README_LIVE_SHARE.md` — Live Share helper instructions

## Notes

- `src/json/` is ignored by git because it contains generated output files.
- Marketplace scraping can break when site layouts change, so updates may be required over time.
- The app includes fallback behavior when scrapers cannot return fresh data.

## Troubleshooting

- Confirm `playwright` is installed and browser components are installed:
  `python3 -m playwright install firefox`
- Run from the repository root to avoid path issues
- Review terminal logs if a scraper fails or search returns no results

## Contributing

1. Fork the repository
2. Create a new branch
3. Open a pull request with a clear summary

If you find a marketplace scraper failure, please open an issue with the affected marketplace and search term.

## License

This project is licensed under the MIT License.

