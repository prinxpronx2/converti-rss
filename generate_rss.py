import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

BASE_URL = "https://romamobilita.it/news-eventi/tutte-le-news-e-gli-eventi/{}"
MAX_PAGES = 3

def scrape_news():
    headers = {"User-Agent": "Mozilla/5.0"}
    articles = []

    for page in range(1, MAX_PAGES + 1):
        if page == 1:
            url = "https://romamobilita.it/news-eventi/tutte-le-news-e-gli-eventi/"
        else:
            url = BASE_URL.format(page)

        print("Scarico:", url)
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.content, "html.parser")
        items = soup.find_all("div", class_="e-loop-item")

        for item in items:
            # titolo
            title_tag = item.find("h2", class_="elementor-heading-title")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)

            # link
            link_tag = item.find("a", href=True)
            if not link_tag:
                continue
            link = link_tag["href"]

            # descrizione
            desc_tag = item.find("div", class_="elementor-widget-theme-post-excerpt")
            description = desc_tag.get_text(strip=True) if desc_tag else "Leggi di più"

            # data reale
            date_tag = item.find("div", class_="elementor-widget-container")
            if date_tag:
                date_text = date_tag.get_text(strip=True)
                try:
                    pubdate = datetime.strptime(date_text, "%d/%m/%Y").replace(tzinfo=timezone.utc)
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
    print("Articoli trovati:", len(articles))
    return articles


def create_rss(articles):
    fg = FeedGenerator()
    fg.title("Roma Mobilità - News")
    fg.link(href="https://romamobilita.it")
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


if __name__ == "__main__":
    articles = scrape_news()
    create_rss(articles)
