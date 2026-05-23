import feedparser
import sqlite3
import requests
from datetime import datetime

BOT_TOKEN = "8796188861:AAGlWJFSSSG9mtUwPdzRan2aj5rHmmEBNR4"
CHAT_ID = "483743563"

conn = sqlite3.connect('news.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS sent_news (
    link TEXT PRIMARY KEY
)
''')

conn.commit()


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    requests.post(url, data=data)


with open('feeds.txt', 'r') as file:
    feeds = file.readlines()


for feed_url in feeds:
    feed_url = feed_url.strip()

    feed = feedparser.parse(feed_url)

    for entry in feed.entries[:5]:
        title = entry.title
        link = entry.link

        cursor.execute(
            "SELECT link FROM sent_news WHERE link=?",
            (link,)
        )

        exists = cursor.fetchone()

        if not exists:
            message = f"🚀 AI UPDATE\n\n{title}\n\n{link}"

            send_telegram(message)

            cursor.execute(
                "INSERT INTO sent_news (link) VALUES (?)",
                (link,)
            )

            conn.commit()

print("Done")
