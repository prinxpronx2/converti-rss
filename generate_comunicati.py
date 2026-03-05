import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

BASE_URL = "https://romamobilita.it/news-eventi/comunicati/page/{}"
MAX_PAGES = 3


def scrape_comunicati():

    headers = {"User-Agent": "Mozilla/5.0"}
    articles = []

    for page in range(1, MAX_PAGES + 1):

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

            link_tag = item.find("a", class_="elementor-button-link")
            if not link_tag:
                continue

            link = link_tag["href"]

            desc_tag = item.find("div", class_="elementor-widget-theme-post-content")
            description = desc_tag.get_text(strip=True) if desc_tag else "Leggi il comunicato"

            articles.append({
                "title": title,
                "link": link,
                "description": description,
                "pubdate": datetime.now(timezone.utc)
            })

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


def reverse_rss_feed():

    print("Inverto ordine articoli nel feed...")

    tree = ET.parse("feed_comunic.xml")
    root = tree.getroot()

    channel = root.find("channel")
    items = channel.findall("item")

    for item in items:
        channel.remove(item)

    for item in reversed(items):
        channel.append(item)

    tree.write("feed_comunic.xml", encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    articles = scrape_comunicati()
    create_rss(articles)

    # inversione finale
    reverse_rss_feed()

    print("Feed generato e invertito correttamente.")
