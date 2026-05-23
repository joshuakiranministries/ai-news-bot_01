import feedparser
import sqlite3
import requests
from datetime import datetime
from deep_translator import GoogleTranslator

BOT_TOKEN = "8796188861:AAGlWJFSSSG9mtUwPdzRan2aj5rHmmEBNR4"
CHAT_ID = "483743563"

# =========================
# DATABASE SETUP
# =========================

conn = sqlite3.connect('news.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS sent_news (
    link TEXT PRIMARY KEY
)
''')

conn.commit()


# =========================
# TELEGRAM FUNCTION
# =========================

def send_telegram(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    response = requests.post(url, data=data)

    print("Telegram Response:", response.text)


# =========================
# LOAD RSS FEEDS
# =========================

with open('feeds.txt', 'r') as file:
    feeds = file.readlines()


# =========================
# MAIN LOOP
# =========================

for feed_url in feeds:

    feed_url = feed_url.strip()

    print(f"\nChecking Feed: {feed_url}")

    feed = feedparser.parse(feed_url)

    for entry in feed.entries[:5]:

        title = entry.title
        link = entry.link

        print(f"\nFound News: {title}")

        # =========================
        # DUPLICATE CHECK
        # =========================

        cursor.execute(
            "SELECT link FROM sent_news WHERE link=?",
            (link,)
        )

        exists = cursor.fetchone()

        if exists:

            print("Already Sent")

            continue


        # =========================
        # TELUGU TRANSLATION
        # =========================

        try:

            telugu_title = GoogleTranslator(
                source='auto',
                target='te'
            ).translate(title)

        except Exception as e:

            print("Translation Error:", e)

            telugu_title = title


        # =========================
        # TELEGRAM MESSAGE
        # =========================

        message = f"""
🚀 AI తాజా అప్డేట్

📰 వార్త:
{telugu_title}

🔗 లింక్:
{link}
"""


        print("\nSending Telegram Message...")
        print(message)


        # =========================
        # SEND TO TELEGRAM
        # =========================

        try:

            send_telegram(message)

            cursor.execute(
                "INSERT INTO sent_news (link) VALUES (?)",
                (link,)
            )

            conn.commit()

            print("Saved To Database")

        except Exception as e:

            print("Telegram Send Error:", e)


print("\n=========================")
print("ALL FEEDS COMPLETED")
print("=========================")
