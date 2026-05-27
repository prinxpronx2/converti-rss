import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
from urllib.parse import urljoin
import re

BASE = "https://romamobilita.it"
BASE_URL = "https://romamobilita.it/news-eventi/comunicati/page/{}"

# quante pagine leggere
MAX_PAGES = 3

# file feed finale
OUTPUT_FILE = "feed_comunic.xml"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_article_date(url):
    """
    Entra nel singolo articolo e cerca:
    'Aggiornato il: gg/mm/aaaa'
    """

    try:
        print(f"  Apro articolo: {url}")

        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")

        text = soup.get_text(" ", strip=True)

        # cerca la data dopo "Aggiornato il:"
        match = re.search(
            r"Aggiornato il:\s*(\d{2}/\d{2}/\d{4})",
            text,
            re.IGNORECASE
        )

        if match:
            date_str = match.group(1)

            print(f"    Data trovata: {date_str}")

            return datetime.strptime(
                date_str,
                "%d/%m/%Y"
            ).replace(tzinfo=timezone.utc)

    except Exception as e:
        print(f"Errore leggendo la data da {url}: {e}")

    # fallback
    print("    Nessuna data trovata, uso data attuale")

    return datetime.now(timezone.utc)


def scrape_comunicati():

    articles = []

    for page in range(1, MAX_PAGES + 1):

        if page == 1:
            url = f"{BASE}/news-eventi/comunicati/"
        else:
            url = BASE_URL.format(page)

        print(f"\nScarico pagina: {url}")

        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            r.raise_for_status()

        except Exception as e:
            print(f"Errore pagina {url}: {e}")
            continue

        soup = BeautifulSoup(r.text, "html.parser")

        comunicati = soup.find_all("div", class_="comunicato")

        print(f"Comunicati trovati: {len(comunicati)}")

        for item in comunicati:

            try:
                # titolo
                titles = item.find_all(
                    "h2",
                    class_="elementor-heading-title"
                )

                if len(titles) < 2:
                    continue

                title = titles[1].get_text(strip=True)

                # link
                link_tag = item.find(
                    "a",
                    class_="elementor-button-link",
                    href=True
                )

                if not link_tag:
                    continue

                link = urljoin(BASE, link_tag["href"])

                # descrizione
                desc_tag = item.find(
                    "div",
                    class_="elementor-widget-theme-post-content"
                )

                description = (
                    desc_tag.get_text(" ", strip=True)
                    if desc_tag
                    else "Leggi il comunicato"
                )

                # DATA REALE presa dall'articolo
                pubdate = get_article_date(link)

                articles.append({
                    "title": title,
                    "link": link,
                    "description": description,
                    "pubdate": pubdate
                })

            except Exception as e:
                print(f"Errore comunicato: {e}")

    # rimuove duplicati
    unique_articles = {}

    for article in articles:
        unique_articles[article["link"]] = article

    articles = list(unique_articles.values())

    # ordina per data DESC
    articles.sort(
        key=lambda x: x["pubdate"],
        reverse=True
    )

    print(f"\nTotale articoli finali: {len(articles)}")

    return articles


def create_rss(articles):

    fg = FeedGenerator()

    fg.title("Roma Mobilità - Comunicati")
    fg.link(href=BASE)
    fg.link(
        href="https://prinxpronx2.github.io/converti-rss/feed_comunic.xml",
        rel="self"
    )

    fg.description("Comunicati ufficiali Roma Mobilità")
    fg.language("it")

    for article in articles:

        fe = fg.add_entry()

        fe.id(article["link"])
        fe.title(article["title"])
        fe.link(href=article["link"])
        fe.description(article["description"])
        fe.pubDate(article["pubdate"])

    fg.rss_file(OUTPUT_FILE, pretty=True)

    print(f"\nFeed RSS creato: {OUTPUT_FILE}")


if __name__ == "__main__":

    articles = scrape_comunicati()

    create_rss(articles)
