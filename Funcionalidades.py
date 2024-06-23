import requests
from bs4 import BeautifulSoup
import feedparser
import urllib.parse

def scrape_website(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.title.string if soup.title else 'No title found'
        paragraphs = [p.get_text() for p in soup.find_all('p')]
        images = [img['src'] for img in soup.find_all('img', src=True)]

        return {
            'title': title,
            'content': '\n\n'.join(paragraphs),
            'images': images
        }
    except Exception as e:
        return str(e)

def search_arxiv(query):
    url = f'http://export.arxiv.org/api/query?search_query={query}&start=0&max_results=5'
    feed = feedparser.parse(url)
    results = []
    for entry in feed.entries:
        item = {
            'title': entry.title,
            'authors': ', '.join(author.name for author in entry.authors),
            'summary': entry.summary,
            'links': [link.href for link in entry.links if link.rel != 'alternate'],
            'pdfs': [link.href for link in entry.links if link.type == 'application/pdf']
        }
        results.append(item)
    return results

def search_pubmed(query):
    encoded_query = urllib.parse.quote(query)
    url = f'https://pubmed.ncbi.nlm.nih.gov/rss/search/{encoded_query}/rss.xml'
    feed = feedparser.parse(url)
    results = []
    for entry in feed.entries:
        item = {
            'title': entry.title,
            'authors': ', '.join(entry.author) if 'author' in entry else 'No authors listed',
            'summary': entry.summary,
            'links': [link.href for link in entry.links if link.rel != 'alternate'],
            'pdfs': [link.href for link in entry.links if link.type == 'application/pdf']
        }
        results.append(item)
    return results
