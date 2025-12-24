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

from scraptor.divar import divarScraptor
from scraptor.torob import torobScraptor


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    query = request.form.get("q", "").strip() # q is the name of the varable that we keep the search name inside it  

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

    # Run scraptors headlessly for this query
    divarScraptor.run(query)
    torobScraptor.run(query)

    # Read results from the shared json directory
    sources = ["divar", "torob"]
    results = {}

    for source in sources:
        path = os.path.join(json_dir, f"{source}.json")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    results[source] = json.load(f)
            except Exception:
                results[source] = []
        else:
            results[source] = []

    # Build a unified list of cards for the template
    cards = []
    base_urls = {
        "divar": "https://divar.ir",
        "torob": "https://torob.com",
    }

    for source, data in results.items():
        if isinstance(data, dict):
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
    app.run(debug=True)


