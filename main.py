import feedparser
import sqlite3
import requests
from datetime import datetime
from deep_translator import GoogleTranslator

BOT_TOKEN = "8796188861:AAGlWJFSSSG9mtUwPdzRan2aj5rHmmEBNR4"
CHAT_ID = "834122182"

# ============================================
# TRUSTED SOURCES
# ============================================

trusted_sources = {
    "openai.com": 9.7,
    "anthropic.com": 9.5,
    "deepmind.google": 9.6,
    "techcrunch.com": 8.9,
    "huggingface.co": 9.0,
    "github.com": 8.8,
    "theverge.com": 8.2,
    "arstechnica.com": 9.1,
    "reuters.com": 9.8,
    "wired.com": 8.7,
    "marktechpost.com": 7.8,
    "reddit.com": 5.5
}


# ============================================
# HYPE WORDS
# ============================================

hype_words = [
    "destroy",
    "shocking",
    "secret",
    "leak",
    "human extinction",
    "kills all jobs",
    "world ending",
    "agi achieved"
]


# ============================================
# CATEGORY KEYWORDS
# ============================================

categories = {
    "AI Models": [
        "gpt",
        "llm",
        "model",
        "claude",
        "gemini"
    ],

    "Cybersecurity": [
        "hack",
        "breach",
        "malware",
        "cybersecurity"
    ],

    "Robotics": [
        "robot",
        "humanoid",
        "automation"
    ],

    "Quantum Computing": [
        "quantum",
        "qubit"
    ],

    "Semiconductors": [
        "gpu",
        "nvidia",
        "chip",
        "semiconductor"
    ]
}


# ============================================
# DATABASE
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
# CLEAN HTML
# ============================================

def clean_html(raw_html):

    clean_text = re.sub('<.*?>', '', raw_html)

    clean_text = clean_text.replace("&nbsp;", " ")

    clean_text = clean_text.replace("&amp;", "&")

    return clean_text.strip()


# ============================================
# TELEGRAM SEND
# ============================================

def send_telegram(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    response = requests.post(url, data=data)

    print(response.text)


# ============================================
# DETECT CATEGORY
# ============================================

def detect_category(text):

    text = text.lower()

    for category, words in categories.items():

        for word in words:

            if word in text:

                return category

    return "General Technology"


# ============================================
# HYPE DETECTION
# ============================================

def detect_hype(text):

    text = text.lower()

    for word in hype_words:

        if word in text:

            return "HIGH"

    return "LOW"


# ============================================
# SOURCE SCORE
# ============================================

def get_source_score(link):

    for domain, score in trusted_sources.items():

        if domain in link:

            return score

    return 4.0


# ============================================
# VERIFICATION STATUS
# ============================================

def get_verification(score):

    if score >= 9:

        return "Official / Highly Trusted"

    elif score >= 7:

        return "Trusted Tech Source"

    else:

        return "Limited Verification"


# ============================================
# LOAD FEEDS
# ============================================

with open('feeds.txt', 'r') as file:

    feeds = file.readlines()


# ============================================
# MAIN LOOP
# ============================================

for feed_url in feeds:

    feed_url = feed_url.strip()

    print(f"\nChecking Feed: {feed_url}")

    feed = feedparser.parse(feed_url)

    for entry in feed.entries[:5]:

        try:

            title = entry.title
            link = entry.link

            print(f"\nFound: {title}")


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
            # SUMMARY
            # ============================================

            summary = ""

            if hasattr(entry, 'summary'):

                summary = entry.summary

            elif hasattr(entry, 'description'):

                summary = entry.description

            else:

                summary = "Summary unavailable."


            clean_summary = clean_html(summary)

            clean_summary = clean_summary[:700]


            # ============================================
            # TRANSLATION
            # ============================================

            try:

                telugu_title = GoogleTranslator(
                    source='auto',
                    target='te'
                ).translate(title)

            except:

                telugu_title = title


            try:

                telugu_summary = GoogleTranslator(
                    source='auto',
                    target='te'
                ).translate(clean_summary)

            except:

                telugu_summary = clean_summary


            # ============================================
            # CATEGORY
            # ============================================

            category = detect_category(title)


            # ============================================
            # HYPE
            # ============================================

            hype_risk = detect_hype(title)


            # ============================================
            # TRUST SCORE
            # ============================================

            trust_score = get_source_score(link)


            # ============================================
            # VERIFICATION
            # ============================================

            verification = get_verification(trust_score)


            # ============================================
            # PRIORITY
            # ============================================

            priority = ""

            if trust_score >= 9:

                priority = "🚨 అత్యవసర అంతర్జాతీయ AI వార్త"

            else:

                priority = "🌍 AI ప్రపంచ తాజా అప్డేట్"


            # ============================================
            # MESSAGE
            # ============================================

            message = f"""
🚨 అంతర్జాతీయ AI & టెక్ వార్త

🌍 సంస్థ / మూలం:
{link.split('/')[2]}

📂 విభాగం:
{category}

📰 ముఖ్య వార్త:
{telugu_title}

📖 పోస్ట్ సారాంశం:
{telugu_summary}

🧠 ఎందుకు ముఖ్యమంటే:
• ఈ వార్త global AI industry పై ప్రభావం చూపే అవకాశం ఉంది
• developers మరియు tech companies కి ఉపయోగకరంగా మారవచ్చు
• AI competition మరింత వేగవంతం కావచ్చు

🛡 ఫ్యాక్ట్ చెక్ స్థితి:
{verification}

⭐️ మూల విశ్వసనీయత:
{trust_score} / 10

⚠️ Hype Risk:
{hype_risk}

🔗 పూర్తి వార్త:
{link}
"""


            print(message)


            # ============================================
            # SEND TELEGRAM
            # ============================================

            send_telegram(message)


            # ============================================
            # SAVE DATABASE
            # ============================================

            cursor.execute(
                "INSERT INTO sent_news (link) VALUES (?)",
                (link,)
            )

            conn.commit()

            print("Saved")


        except Exception as e:

            print("ERROR:", e)


print("\nALL FEEDS COMPLETED")
