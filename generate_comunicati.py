import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
import re

BASE_URL = "https://romamobilita.it/news-eventi/comunicati/page/{}"
MAX_PAGES = 3

def scrape_comunicati():
    headers = {"User-Agent": "Mozilla/5.0"}
    articles = []

    # ciclo inverso: pagina 3 → 2 → 1
    for page in range(MAX_PAGES, 0, -1):
        if page == 1:
            url = "https://romamobilita.it/news-eventi/comunicati/"
        else:
            url = BASE_URL.format(page)

        print("Scarico:", url)
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.content, "html.parser")
        items = soup.find_all("div", class_="comunicato")

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

            # data reale: prova a cercare pattern DD/MM/YYYY
            date_match = re.search(r"(\d{2}/\d{2}/\d{4})", item.get_text())
            if date_match:
                try:
                    pubdate = datetime.strptime(date_match.group(1), "%d/%m/%Y").replace(tzinfo=timezone.utc)
                except:
                    pubdate = datetime.now(timezone.utc)
            else:
                pubdate = datetime.now(timezone.utc)

            articles.append({
                "title": title,
                "link": link,
                "description": description,
                "pubdate": pubdate
            })

    # ordina dal più recente al più vecchio
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
