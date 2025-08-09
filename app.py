import os
import requests
from flask import Flask, render_template, request
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = "https://newsapi.org/v2/top-headlines"
PAGE_SIZE = 4

# Supported topics by NewsAPI
TOPICS = ["business", "technology", "health", "science", "sports", "entertainment"]

def fetch_articles(page=1, topic=None):
    params = {
        'apiKey': API_KEY,
        'country': 'us',
        'pageSize': PAGE_SIZE,
        'page': page
    }

    if topic:
        params['category'] = topic

    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        if data.get("status") != "ok":
            raise Exception("NewsAPI error")

        total_results = data.get("totalResults", 0)
        articles = []

        for item in data.get('articles', []):
            if not item.get("title") or not item.get("url"):
                continue

            articles.append({
                'title': item['title'],
                'content': item['description'] or 'No description available.',
                'image': item['urlToImage'] or "https://via.placeholder.com/300",
                'source': item['source']['name'],
                'link': item['url'],
                'timestamp': datetime.strptime(item['publishedAt'], "%Y-%m-%dT%H:%M:%SZ")
            })

        return articles, total_results

    except Exception as e:
        print(f"[ERROR] Failed to fetch articles: {e}")
        return [], 0

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    topic = request.args.get('topic', default=None)

    articles, total_results = fetch_articles(page=page, topic=topic)
    total_pages = (total_results + PAGE_SIZE - 1) // PAGE_SIZE

    return render_template(
        'index.html',
        articles=articles,
        current_page=page,
        total_pages=total_pages,
        current_topic=topic,
        topics=TOPICS
    )

if __name__ == '__main__':
    app.run(debug=True)
