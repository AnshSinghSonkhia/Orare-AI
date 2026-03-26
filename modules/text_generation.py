from GoogleNews import GoogleNews
from newspaper import Article
from urllib.parse import urlparse, urlunparse, quote_plus
import logging
import re
import feedparser

logging.basicConfig(level=logging.ERROR)

def clean_url(url):
    # (Currently unused, kept for future use)
    # Remove any tracking/query strings like &ved=... or ?utm=...
    url = re.split(r"[&?]", url)[0]

    # Parse and reconstruct the URL
    parsed = urlparse(url)
    cleaned = parsed._replace(
        path=parsed.path.lower().rstrip("/"),  # lowercase the path, remove trailing slash
        query='', fragment=''
    )
    return urlunparse(cleaned)

def fetch_latest_news_with_content(topic="India", count=3):
    print(f"\n🔍 Top {count} Latest News on: {topic}\n")

    topic = topic.strip()

    # googlenews = GoogleNews(lang='en', region='IN')
    # googlenews.search(topic)
    # news = googlenews.results(sort=True)[:count]

    try:
        googlenews = GoogleNews(lang='en', region='IN')
        googlenews.search(topic)
        news = googlenews.results(sort=True)[:count]
    except Exception as e:
        print(f"⚠️ GoogleNews failed: {e}")
        news = []

    final_combined_content = ""

    for item in news:
        title = item.get('title', 'No Title')
        raw_link = item.get('link', '')

        #clean_link = clean_url(raw_link)
        clean_link = raw_link  # Avoid breaking URLs

        print(f"📰 {title}")
        print(f"🔗 {clean_link}\n")

        try:
            article = Article(clean_link, language="en")
            article.download()
            article.parse()
            content = article.text.strip()

            if content:
                print("📝 Content fetched:\n")
                #print(content[:500] + "...\n")  # Show content preview
                final_combined_content += content + "\n\n"
            else:
                print("⚠️ Content not found.\n")

        except Exception as e:
            logging.error(f"❌ Error fetching article content: {e}")
            print("⚠️ Failed to extract article content.\n")

        print("=" * 100)

    # SMART FALLBACK TRIGGER (not just empty, but low content)
    if len(final_combined_content.strip()) < 200:  # If we have less than 200 chars of content, consider it a failure
        print("⚠️ Primary source failed. Switching to RSS...\n")
        return fetch_rss_news(topic, count)

    return final_combined_content.strip()

def clean_html(raw_html):
    """Remove HTML tags from RSS description"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', raw_html)

def fetch_rss_news(topic="India", count=3):
    print(f"\n📡 Falling back to RSS for: {topic}\n")

    topic = topic.strip()
    encoded_topic = quote_plus(topic)
    url = f"https://news.google.com/rss/search?q={encoded_topic}&hl=en-IN&gl=IN&ceid=IN:en"

    feed = feedparser.parse(url)

    final_content = ""

    for entry in feed.entries[:count]:
        # title = entry.title
        title = entry.title.strip()

        print(f"📰 {title}\n")

        # ✅ Clean summary (optional, but we won't use it for final output)
        summary = clean_html(entry.summary)
        summary = summary.replace('\xa0', ' ').replace('&nbsp;', ' ').strip()

        #print(f"📝 {summary[:200]}...\n")

        # ✅ Remove duplicate title from summary if present
        if summary.startswith(title):
            summary = summary[len(title):].strip()

        # ✅ FINAL OUTPUT (clean for TTS)

        # final_content += f"{title}. {summary}\n\n"
        final_content += f"{title}.\n\n"

    return final_content.strip()