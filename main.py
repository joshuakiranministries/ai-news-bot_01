import feedparser
import sqlite3
import requests
from datetime import datetime
from deep_translator import GoogleTranslator

BOT_TOKEN = "8796188861:AAGlWJFSSSG9mtUwPdzRan2aj5rHmmEBNR4"
CHAT_ID = "834122182"

# ============================================
# DATABASE SETUP
# ============================================

conn = sqlite3.connect('news.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS sent_news (
    link TEXT PRIMARY KEY
)
''')

conn.commit()


# ============================================
# CLEAN HTML FUNCTION
# ============================================

def clean_html(raw_html):

    clean_text = re.sub('<.*?>', '', raw_html)

    clean_text = clean_text.replace("&nbsp;", " ")

    clean_text = clean_text.replace("&amp;", "&")

    return clean_text.strip()


# ============================================
# TELEGRAM SEND FUNCTION
# ============================================

def send_telegram(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    response = requests.post(url, data=data)

    print("\nTelegram Response:")
    print(response.text)


# ============================================
# LOAD RSS FEEDS
# ============================================

with open('feeds.txt', 'r') as file:

    feeds = file.readlines()


# ============================================
# MAIN LOOP
# ============================================

for feed_url in feeds:

    feed_url = feed_url.strip()

    print("\n================================")
    print(f"Checking Feed: {feed_url}")
    print("================================")

    feed = feedparser.parse(feed_url)

    for entry in feed.entries[:5]:

        try:

            title = entry.title
            link = entry.link

            print(f"\nFound News: {title}")

            # ============================================
            # DUPLICATE CHECK
            # ============================================

            cursor.execute(
                "SELECT link FROM sent_news WHERE link=?",
                (link,)
            )

            exists = cursor.fetchone()

            if exists:

                print("Already Sent")

                continue


            # ============================================
            # GET SUMMARY
            # ============================================

            summary = ""

            if hasattr(entry, 'summary'):

                summary = entry.summary

            elif hasattr(entry, 'description'):

                summary = entry.description

            else:

                summary = "Summary not available."


            # ============================================
            # CLEAN HTML
            # ============================================

            clean_summary = clean_html(summary)


            # ============================================
            # LIMIT SUMMARY SIZE
            # ============================================

            clean_summary = clean_summary[:1000]


            # ============================================
            # TRANSLATE TITLE
            # ============================================

            try:

                telugu_title = GoogleTranslator(
                    source='auto',
                    target='te'
                ).translate(title)

            except Exception as e:

                print("Title Translation Error:", e)

                telugu_title = title


            # ============================================
            # TRANSLATE SUMMARY
            # ============================================

            try:

                telugu_summary = GoogleTranslator(
                    source='auto',
                    target='te'
                ).translate(clean_summary)

            except Exception as e:

                print("Summary Translation Error:", e)

                telugu_summary = clean_summary


            # ============================================
            # CREATE TELEGRAM MESSAGE
            # ============================================

            message = f"""
🚀 AI ప్రపంచ తాజా అప్డేట్

📰 వార్త:
{telugu_title}

📖 సంక్షిప్త వివరణ:
{telugu_summary}

🔗 పూర్తి వార్త:
{link}
"""


            # ============================================
            # DEBUG LOG
            # ============================================

            print("\nSending Telegram Message...")
            print(message)


            # ============================================
            # SEND TO TELEGRAM
            # ============================================

            send_telegram(message)


            # ============================================
            # SAVE TO DATABASE
            # ============================================

            cursor.execute(
                "INSERT INTO sent_news (link) VALUES (?)",
                (link,)
            )

            conn.commit()

            print("Saved To Database")


        except Exception as e:

            print("\nERROR:")
            print(e)


# ============================================
# FINISHED
# ============================================

print("\n================================")
print("ALL FEEDS COMPLETED")
print("================================")
