import requests
from bs4 import BeautifulSoup
import feedparser
from urllib.parse import urljoin

def scrape_website(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.title.string if soup.title else 'No title found'
        paragraphs = [p.text for p in soup.find_all('p')]
        links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True)]
        images = [urljoin(url, img['src']) for img in soup.find_all('img', src=True)]

        return {
            'title': title,
            'paragraphs': paragraphs,
            'links': links,
            'images': images
        }
    except requests.RequestException as e:
        return f"Error: {e}"

def search_arxiv(query):
    url = f'http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=10'
    feed = feedparser.parse(url)
    results = []
    for entry in feed.entries:
        results.append({
            'title': entry.title,
            'summary': entry.summary,
            'link': entry.link
        })
    return results

def search_pubmed(query):
    url = f'https://pubmed.ncbi.nlm.nih.gov/rss/search/{query}/rss.xml'
    feed = feedparser.parse(url)
    results = []
    for entry in feed.entries:
        results.append({
            'title': entry.title,
            'summary': entry.summary,
            'link': entry.link
        })
    return results