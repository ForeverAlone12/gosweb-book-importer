import json

from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
from bson import ObjectId
from scraper import Scrapper
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Подключение к MongoDB
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(mongo_uri)
db = client["web_scraper_db"]
scraped_data_collection = db["scraped_data"]


@app.route('/')
def index():
    recent_scrapes = list(scraped_data_collection.find().sort("_id", -1))
    return render_template('index.html', recent_scrapes=recent_scrapes)


@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.form.get('url')
    if not url:
        return redirect(url_for('index'))

    scraper = Scrapper()

    # Используем Selenium для скрапинга
    scraped_data = scraper.scrape_with_selenium(url)

    # Сохраняем в MongoDB
    scraped_data_collection.insert_one(scraped_data)

    return redirect(url_for('index'))


@app.route('/delete', methods=['POST'])
def delete():
    try:
        item_id = request.form.get('item_id')
        obj_id = ObjectId(item_id)
        scraped_data_collection.delete_one({'_id': obj_id})

        return json.dumps({'success':True})

    except Exception as e:
        return json.dumps({'status':str(e)})

if __name__ == '__main__':
    app.run(debug=True)
