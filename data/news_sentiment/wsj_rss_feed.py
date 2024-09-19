import feedparser

# WSJ RSS feed URL
rss_url = "https://feeds.a.dj.com/rss/RSSWSJD.xml"

# Parse the feed
feed = feedparser.parse(rss_url)

# Display the latest articles
for entry in feed.entries:
    print(f"Title: {entry.title}")
    print(f"Link: {entry.link}")
    print(f"Published: {entry.published}")
    print("\n")
