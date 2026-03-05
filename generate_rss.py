import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime

URL = "https://romamobilita.it/news-eventi/tutte-le-news-e-gli-eventi/"

def scrape_news():
    try:
        response = requests.get(URL, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        articles = []

        for h2 in soup.find_all('h2')[:20]:
            title = h2.get_text(strip=True)

            parent = h2.parent

            link_tag = parent.find('a', href=True)
            if not link_tag:
                continue

            link = link_tag['href']
            if not link.startswith('http'):
                link = 'https://romamobilita.it' + link

            desc_tag = parent.find('p')
            desc = desc_tag.get_text(strip=True) if desc_tag else "Leggi di più"

            articles.append({
                'title': title,
                'link': link,
                'description': desc,
                'pubdate': datetime.now()
            })

        print("Articoli trovati:", len(articles))
        return articles

    except Exception as e:
        print(f"Errore: {e}")
        return []

def create_rss_feed(articles):
    fg = FeedGenerator()
    fg.title('Roma Mobilità - News')
    fg.link(href='https://romamobilita.it', rel='alternate')
    fg.description('News da Roma Mobilità')
    fg.language('it')
    
    for article in articles:
        fe = fg.add_entry()
        fe.title(article['title'])
        fe.link(href=article['link'])
        fe.description(article['description'])
        fe.pubDate(article['pubdate'])
    
    fg.rss_file('feed.xml', pretty=True)
    print(f"✅ RSS generato con {len(articles)} articoli")

if __name__ == '__main__':
    articles = scrape_news()
    create_rss_feed(articles)
