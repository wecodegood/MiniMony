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
def index():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    query = request.form.get("q", "").strip()

    if not query:
        return render_template(
            "search.html",
            search_query=query,
            results_json="{}",
            error="هیچ کالایی وارد نشده است.",
        )

    # Run scraptors headlessly for this query
    divarScraptor.run(query)
    torobScraptor.run(query)

    # Read results from the shared json directory
    json_dir = os.path.join(BASE_DIR, "json")
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

    results_json = json.dumps(results, ensure_ascii=False, indent=2)

    return render_template(
        "search.html",
        search_query=query,
        results_json=results_json,
        error=None,
    )


if __name__ == "__main__":
    app.run(debug=True)


