import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
import re

BASE_URL = "https://romamobilita.it/news-eventi/comunicati/page/{}"
MAX_PAGES = 3

# Mappa dei mesi in italiano per convertire la data della pagina interna
MESI = {
    "gennaio": "01", "febbraio": "02", "marzo": "03", "aprile": "04",
    "maggio": "05", "giugno": "06", "luglio": "07", "agosto": "08",
    "settembre": "09", "ottobre": "10", "novembre": "11", "dicembre": "12"
}

def recupera_data_interna(url, session, headers):
    """Entra nella pagina del singolo comunicato e cerca la data reale."""
    try:
        r = session.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(r.content, "html.parser")
       
        # Roma Mobilità usa spesso classi specifiche per le date nei singoli articoli,
        # oppure possiamo cercarla nel testo. Cerchiamo un pattern tipo "25 maggio 2026"
        testo_pagina = soup.get_text().lower()
        match = re.search(r"(\d{1,2})\s+(gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)\s+(\d{4})", testo_pagina)
       
        if match:
            giorno = match.group(1).zfill(2)
            mese = MESI[match.group(2)]
            anno = match.group(3)
            data_str = f"{giorno}/{mese}/{anno}"
            return datetime.strptime(data_str, "%d/%m/%Y").replace(tzinfo=timezone.utc)
    except Exception as e:
        print(f"Errore nel recupero data per {url}: {e}")
   
    # Se fallisce il recupero, restituisce la data attuale come salvagente
    return datetime.now(timezone.utc)

def scrape_comunicati():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    articles = []
   
    # Usiamo Session per fare richieste multiple molto più velocemente
    session = requests.Session()

    # ciclo inverso: pagina 3 → 1
    for page in range(MAX_PAGES, 0, -1):
        if page == 1:
            url = "https://romamobilita.it/news-eventi/comunicati/"
        else:
            url = BASE_URL.format(page)

        print("Scarico indice:", url)
        r = session.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.content, "html.parser")
        items = soup.find_all("div", class_="comunicato")

        page_articles = []

        for item in items:
            titles = item.find_all("h2", class_="elementor-heading-title")
            if len(titles) < 2:
                continue
            title = titles[1].get_text(strip=True)

            link_tag = item.find("a", class_="elementor-button-link", href=True)
            if not link_tag:
                continue
            link = link_tag["href"]

            desc_tag = item.find("div", class_="elementor-widget-theme-post-content")
            description = desc_tag.get_text(strip=True) if desc_tag else "Leggi il comunicato"

            # Ora andiamo a prendere la data vera dentro l'articolo
            print(f"-> Recupero data reale per: {title[:30]}...")
            pubdate = recupera_data_interna(link, session, headers)

            page_articles.append({
                "title": title,
                "link": link,
                "description": description,
                "pubdate": pubdate
            })

        # inverti ordine della pagina
        page_articles.reverse()
        articles.extend(page_articles)

    # ordina globalmente decrescente per data
    articles.sort(key=lambda x: x['pubdate'], reverse=True)
    print("Comunicati trovati:", len(articles))
    return articles


def create_rss(articles):
    fg = FeedGenerator()
    fg.title("Roma Mobilità - Comunicati")
    fg.link(href="https://romamobilita.it")
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


if __name__ == "__main__":
    articles = scrape_comunicati()
    create_rss(articles)
