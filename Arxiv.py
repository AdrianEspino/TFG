import requests
from bs4 import BeautifulSoup

def fetch_arxiv(query):
    try:
        base_url = 'http://export.arxiv.org/api/query'
        params = {
            'search_query': f'all:{query}',
            'start': 0,
            'max_results': 10
        }
        response = requests.get(base_url, params=params)
        response.raise_for_status()

        print("URL Requested:", response.url)  # Imprime la URL completa solicitada

        soup = BeautifulSoup(response.content, 'xml')

        # Imprime la respuesta completa para depuración
        print("Response Content:\n", soup.prettify())

        entries = soup.find_all('entry')
        results = []

        for entry in entries:
            title = entry.title.text
            summary = entry.summary.text
            link = entry.id.text
            published = entry.published.text
            authors = [author.find('name').text for author in entry.find_all('author')]

            results.append({
                'title': title,
                'summary': summary,
                'link': link,
                'published': published,
                'authors': ', '.join(authors)
            })

        return results
    except requests.RequestException as e:
        print(f"Error fetching data from arXiv: {e}")
        return []

# Ejemplo de uso para buscar "machine learning" en arXiv
results = fetch_arxiv("machine learning")
print("Results:", results)
