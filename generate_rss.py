import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

URL = "https://romamobilita.it/news-eventi/tutte-le-news-e-gli-eventi/"

def scrape_news():
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        articles = []
        seen_links = set()

        for a in soup.find_all("a", href=True):

            href = a["href"]

            if "/it/node/" not in href:
                continue

            if not href.startswith("http"):
                href = "https://romamobilita.it" + href

            if href in seen_links:
                continue

            title = a.get_text(strip=True)

            if len(title) < 10:
                continue

            seen_links.add(href)

            articles.append({
                "title": title,
                "link": href,
                "description": "Leggi la notizia completa",
                "pubdate": datetime.now(timezone.utc)
            })

            if len(articles) >= 20:
                break

        print("Articoli trovati:", len(articles))
        return articles

    except Exception as e:
        print("Errore scraping:", e)
        return []


def create_rss_feed(articles):

    fg = FeedGenerator()

    fg.title("Roma Mobilità - News")
    fg.link(href="https://romamobilita.it", rel="alternate")
    fg.link(href="https://prinxpronx2.github.io/converti-rss/feed.xml", rel="self")
    fg.description("News da Roma Mobilità")
    fg.language("it")

    for article in articles:
        fe = fg.add_entry()
        fe.title(article["title"])
        fe.link(href=article["link"])
        fe.description(article["description"])
        fe.pubDate(article["pubdate"])

    fg.rss_file("feed.xml", pretty=True)

    print("RSS generato con", len(articles), "articoli")


if __name__ == "__main__":
    articles = scrape_news()

    if articles:
        create_rss_feed(articles)
    else:
        print("Nessun articolo trovato")
