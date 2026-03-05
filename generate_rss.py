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

        # cerca i titoli delle notizie
        for h2 in soup.find_all("h2")[:20]:

            title = h2.get_text(strip=True)
            parent = h2.parent

            # cerca il link dentro il blocco
            link_tag = parent.find("a", href=True)
            if not link_tag:
                continue

            link = link_tag["href"]

            if not link.startswith("http"):
                link = "https://romamobilita.it" + link

            # descrizione
            desc_tag = parent.find("p")
            desc = desc_tag.get_text(strip=True) if desc_tag else "Leggi di più"

            articles.append({
                "title": title,
                "link": link,
                "description": desc,
                "pubdate": datetime.now(timezone.utc)
            })

        print("Articoli trovati:", len(articles))
        return articles

    except Exception as e:
        print("Errore durante lo scraping:", e)
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

    printf(" RSS generato con {len(articles)} articoli")


if __name__ == "__main__":
    articles = scrape_news()

    if articles:
        create_rss_feed(articles)
    else:
        print(" Nessun articolo trovato!")
