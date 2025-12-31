from flask import Flask
from flask import render_template
from flask import request

import os
import sys
import json

# Ensure project root (src) is on sys.path so we can import scraptors
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

import importlib.util

# Import the central scraptor runner by file path to avoid a circular
# import when this file is executed as a script (it is also named main.py).
try:
    main_path = os.path.join(BASE_DIR, "main.py")
    spec = importlib.util.spec_from_file_location("mm_main", main_path)
    mm_main = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mm_main)
    run_scraptors = getattr(mm_main, "run_scraptors")
except Exception as e:
    # Fall back to a noop runner so the web UI can still start for templating
    print(f"Warning: could not import run_scraptors: {e}")
    def run_scraptors(product=None, parallel=True):
        print("run_scraptors unavailable")


app = Flask(__name__)



# :)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
@app.route("/search", methods=["POST"])
def search(realRun=True):
    query = request.form.get("q", "").strip()  # always get query

    # Base JSON directory (shared output of all scraptors)
    json_dir = os.path.join(BASE_DIR, "json")
    json_count = 0
    if os.path.isdir(json_dir):
        json_count = sum(
            1
            for name in os.listdir(json_dir)
            if name.lower().endswith(".json") and os.path.isfile(os.path.join(json_dir, name))
        )

    if not query:
        return render_template(
            "search.html",
            search_query=query,
            results_json="{}",
            cards=[],
            json_count=json_count,
            error="هیچ کالایی وارد نشده است.",
        )

    if realRun:
        # Run all scraptors via central runner (may run in parallel) and
        # receive results directly (no intermediate JSON files).
        try:
            # When called from the Flask request context, running scraptors
            # in a process pool can fail (Playwright / multiprocessing issues).
            # Run sequentially here for reliability and faster visible feedback.
            results = run_scraptors(product=query, parallel=False) or {}
            print(f"run_scraptors returned keys: {list(results.keys())}")
        except Exception as e:
            print(f"Error running scraptors: {e}")
            import traceback
            traceback.print_exc()
            results = {}

        # If scraptors didn't yield results (common in restricted/container
        # environments where Playwright can't run), try to load previously
        # saved JSON outputs from the `json/` folder. This provides quicker
        # visible feedback without launching browsers during the request.
        if not results:
            try:
                for name in os.listdir(json_dir):
                    if not name.lower().endswith('.json'):
                        continue
                    src_name = os.path.splitext(name)[0]
                    path = os.path.join(json_dir, name)
                    try:
                        with open(path, 'r', encoding='utf-8') as fh:
                            data = json.load(fh)
                        results[src_name] = data
                        print(f"Loaded fallback data from {path}")
                    except Exception as e:
                        print(f"Failed loading JSON {path}: {e}")
            except Exception as e:
                print(f"Error listing json dir {json_dir}: {e}")

    else:
        # MOCK / QUICK LOAD MODE
        results = {
            "divar": [
                {
                    "name": "Test Product A",
                    "price": 123000,
                    "link": "/p/test-a",
                    "image": "https://via.placeholder.com/150"
                }
            ],
            "torob": [
                {
                    "name": "Test Product B",
                    "price": 456000,
                    "link": "/p/test-b",
                    "image": "https://via.placeholder.com/150"
                }
            ]
        }

    # Final fallback: if we still have no results, show a small mock result
    # so the UI displays something useful instead of an empty page.
    if not results:
        results = {
            "mock": [
                {"name": f"نتیجه نمونه برای '{query}'", "price": None, "link": "", "image": ""}
            ]
        }

    # Build a unified list of cards for the template
    cards = []
    base_urls = {
        "divar": "https://divar.ir",
        "torob": "https://torob.com",
    }

    for source, data in results.items():
        if isinstance(data, dict):
            # Skip obvious error / no-result dicts returned by some scraptors
            if data.get("error") and len(data.keys()) <= 3:
                print(f"Skipping {source} (error response): {data}")
                continue
            items = [data]
        elif isinstance(data, list):
            items = data
        else:
            continue

        for item in items:
            if not isinstance(item, dict):
                continue

            name = item.get("name", "")
            price = item.get("price")
            link = item.get("link", "")
            image = item.get("image") or ""

            # Build full link if relative
            if isinstance(link, str) and link.startswith("/"):
                base = base_urls.get(source, "")
                full_link = (base + link) if base else link
            else:
                full_link = link

            cards.append(
                {
                    "source": source,
                    "name": name,
                    "price": price,
                    "link": full_link,
                    "image": image,
                }
            )

    results_json = json.dumps(results, ensure_ascii=False, indent=2)

    return render_template(
        "search.html",
        search_query=query,
        results_json=results_json,
        cards=cards,
        json_count=json_count,
        error=None,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5123)


