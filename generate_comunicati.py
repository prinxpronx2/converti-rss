import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

URL = "https://romamobilita.it/news-eventi/comunicati/"

def scrape_comunicati():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    articles = []

    # trova tutti i div con classe 'comunicato'
    for item in soup.find_all("div", class_="comunicato", limit=20):

        # titolo: il secondo h2
        h2_tags = item.find_all("h2", class_="elementor-heading-title")
        if len(h2_tags) < 2:
            continue
        title = h2_tags[1].get_text(strip=True)

        # descrizione
        desc_tag = item.find("div", class_="elementor-widget-theme-post-content")
        description = desc_tag.get_text(strip=True) if desc_tag else "Leggi il comunicato completo"

        # link "Leggi di più"
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

    print(f"Comunicati trovati: {len(articles)}")
    return articles

def create_rss_comunicati(articles):
    fg = FeedGenerator()
    fg.title("Roma Mobilità - Comunicati")
    fg.link(href="https://romamobilita.it", rel="alternate")
    fg.link(href="https://prinxpronx2.github.io/converti-rss/feed_comunic.xml", rel="self")
    fg.description("Comunicati ufficiali Roma Mobilità")
    fg.language("it")

    for article in articles:
        fe = fg.add_entry()
        fe.title(article["title"])
        fe.link(href=article["link"])
        fe.description(article["description"])
        fe.pubDate(article["pubdate"])

    fg.rss_file("feed_comunic.xml", pretty=True)
    print("RSS dei comunicati generato con", len(articles), "articoli")

if __name__ == "__main__":
    articles = scrape_comunicati()
    if articles:
        create_rss_comunicati(articles)
    else:
        print("Nessun comunicato trovato")
