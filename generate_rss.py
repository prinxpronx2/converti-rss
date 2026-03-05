import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

URL = "https://romamobilita.it/news-eventi/tutte-le-news-e-gli-eventi/"

def scrape_news():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    articles = []

    # cerca tutti i div con classe 'primo-piano'
    for item in soup.find_all("div", class_="primo-piano", limit=20):

        # titolo
        title_tag = item.find("h2", class_="elementor-heading-title")
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)

        # descrizione: prova theme-post-excerpt prima, poi shortcode
        desc_tag = item.find("div", class_="elementor-widget-theme-post-excerpt")
        if desc_tag:
            description = desc_tag.get_text(strip=True)
        else:
            shortcode_tag = item.find("div", class_="elementor-shortcode")
            description = shortcode_tag.get_text(strip=True) if shortcode_tag else "Leggi la notizia completa"

        # link
        link_tag = item.find("a", class_="elementor-button-link", href=True)
        if not link_tag:
            continue
        link = link_tag["href"]
        if not link.startswith("http"):
            link = "https://romamobilita.it" + link

        articles.append({
            "title": title,
            "link": link,
            "description": description,
            "pubdate": datetime.now(timezone.utc)
        })

    print(f"Articoli trovati: {len(articles)}")
    return articles

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
