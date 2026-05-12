from datetime import date
from flask import Flask, Response, jsonify, render_template, request, url_for
from pymongo import MongoClient
import os


app = Flask(__name__)


def get_db():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    db_name = os.getenv("MONGO_DB_NAME", "london_kids_preschool")
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=1500)
    db = client[db_name]
    return db, client


def load_testimonials():
    fallback = [
        {
            "name": "Priya S.",
            "relation": "Mother of Nursery Student",
            "text": "The teachers are warm and caring. My child is excited to go to school every day.",
        },
        {
            "name": "Rahul K.",
            "relation": "Father of Junior KG Student",
            "text": "Excellent activity-based learning and a very safe, clean campus environment.",
        },
        {
            "name": "Megha P.",
            "relation": "Mother of Senior KG Student",
            "text": "A premium preschool feel with strong values, smart learning, and friendly staff.",
        },
    ]

    try:
        db, client = get_db()
        items = list(
            db.testimonials.find(
                {},
                {"_id": 0, "name": 1, "relation": 1, "text": 1},
            ).limit(6)
        )
        client.close()
        return items if items else fallback
    except Exception:
        return fallback


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/robots.txt")
def robots():
    base = request.url_root.rstrip("/")
    content = "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            f"Sitemap: {base}/sitemap.xml",
        ]
    )
    return Response(content, mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap():
    today = date.today().isoformat()
    home_url = url_for("home", _external=True)
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{home_url}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>"""
    return Response(xml, mimetype="application/xml")


@app.route("/api/testimonials")
def testimonials():
    return jsonify(load_testimonials())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
