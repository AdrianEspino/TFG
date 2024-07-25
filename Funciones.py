import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import feedparser
import csv
import os
from tkinter import filedialog, messagebox

def scrape_website(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.title.string if soup.title else 'No title found'
        paragraphs = [p.text for p in soup.find_all('p')]
        links = [{'text': a.get_text(), 'url': urljoin(url, a['href'])} for a in soup.find_all('a', href=True)]
        images = [{'alt': img.get('alt', ''), 'src': urljoin(url, img['src'])} for img in soup.find_all('img', src=True)]

        return {
            'title': title,
            'paragraphs': paragraphs,
            'links': links,
            'images': images
        }
    except requests.RequestException as e:
        return f"Error: {e}"

def search_arxiv(query):
    base_url = "http://export.arxiv.org/api/query?"
    search_url = f"{base_url}search_query=all:{query}&start=0&max_results=10"
    response = requests.get(search_url)
    feed = feedparser.parse(response.content)
    results = []
    for entry in feed.entries:
        result = {
            'title': entry.title,
            'summary': entry.summary,
            'link': entry.link
        }
        results.append(result)
    return results


def search_pubmed(query):
    base_url = "https://pubmed.ncbi.nlm.nih.gov/"
    search_url = f"{base_url}?term={query}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article', class_='full-docsum')
    results = []
    for article in articles:
        title = article.find('a', class_='docsum-title').text.strip()
        link = urljoin(base_url, article.find('a', class_='docsum-title')['href'])
        summary = article.find('div', class_='full-view-snippet').text.strip() if article.find('div', class_='full-view-snippet') else "No summary available"
        results.append({'title': title, 'summary': summary, 'link': link})
    return results

def fetch_editorial_board_data():
    url = 'https://dl.acm.org/journal/jetc/editorial-board'

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        journal_name = soup.find('h1', class_='title').text.strip() if soup.find('h1', class_='title') else 'Journal Name Not Found'
        data_list = []
        roles = soup.find_all('h3', class_='section__title')
        for role in roles:
            role_text = role.text.strip()
            next_sibling = role.find_next()
            while next_sibling and next_sibling.name != 'h3':
                if 'item-meta__info' in next_sibling.get('class', []):
                    name = next_sibling.find('h4').text.strip() if next_sibling.find('h4') else ''
                    affiliation = next_sibling.find('p').text.strip() if next_sibling.find('p') else ''
                    country = next_sibling.find('span').text.strip() if next_sibling.find('span') else ''
                    data_list.append([role_text, name, affiliation, country])
                next_sibling = next_sibling.find_next()

        # Save the CSV file
        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if save_path:
            with open(save_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Journal Name'])
                writer.writerow([journal_name])
                writer.writerow(['Role', 'Name', 'Affiliation', 'Country'])
                writer.writerows(data_list)

            messagebox.showinfo("Success", f"The editorial board data has been saved to '{os.path.basename(save_path)}'.")

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to fetch the editorial board data. Error: {e}")

def fetch_editorial_board_data_TNNLS():
    url = 'https://cis.ieee.org/publications/t-neural-networks-and-learning-systems/tnnls-editor-and-associate-editors'

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        journal_name = soup.find('h1').text.strip() if soup.find('h1') else 'Journal Name Not Found'
        data_list = []

        first_member = soup.find('h2', style=True)
        if first_member:
            role_text = first_member.text.strip()
            p_tag = first_member.find_next('p', style=True)
            if p_tag:
                strong_tag = p_tag.find('strong')
                name = strong_tag.text.strip() if strong_tag else ''
                br_tags = p_tag.find_all('br')
                if len(br_tags) >= 4:
                    affiliation1 = br_tags[0].next_sibling.strip() if br_tags[0].next_sibling else ''
                    affiliation2 = br_tags[1].next_sibling.strip() if br_tags[1].next_sibling else ''
                    country = br_tags[2].next_sibling.strip() if br_tags[2].next_sibling else ''
                    email = br_tags[3].next_sibling.strip() if br_tags[3].next_sibling else ''
                    affiliation = f"{affiliation1}, {affiliation2}"
                    data_list.append([role_text, name, affiliation, country, email, ''])

        roles = soup.find_all('h2')
        for role in roles:
            if role == first_member:
                continue
            role_text = role.find('strong').text.strip() if role.find('strong') else ''
            next_sibling = role.find_next()
            elements = []
            while next_sibling and next_sibling.name != 'h2':
                if next_sibling.name == 'p':
                    elements.append(next_sibling)
                elif next_sibling.name == 'table':
                    tbody = next_sibling.find('tbody')
                    if tbody:
                        tr_elements = tbody.find_all('tr')[1:]
                        for tr in tr_elements:
                            td_elements = tr.find_all('td')
                            if len(td_elements) >= 3:
                                name = td_elements[0].text.strip()
                                affiliation = td_elements[1].text.strip()
                                country = td_elements[2].text.strip()
                                data_list.append([role_text, name, affiliation, country, '', ''])
                next_sibling = next_sibling.find_next()

            if elements:
                for element in elements[:-1]:
                    spans = element.find_all('span')
                    if len(spans) >= 4:
                        name = spans[0].text.strip()
                        affiliation1 = spans[1].text.strip()
                        affiliation2 = spans[2].text.strip()
                        country = spans[3].text.strip()
                        affiliation = f"{affiliation1}, {affiliation2}"
                        data_list.append([role_text, name, affiliation, country, '', ''])

        roles = soup.find_all('h3', class_='roletitle')
        for role in roles:
            role_text = role.text.strip()
            next_sibling = role.find_next()
            while next_sibling and next_sibling.name != 'h3':
                if next_sibling.name == 'div' and 'indvlistname' in next_sibling.get('class', []):
                    name = next_sibling.text.strip()
                    affiliation_div = next_sibling.find_next('div', class_='indvlistaffil')
                    if affiliation_div:
                        affiliation_parts = affiliation_div.text.strip().split(',')
                        affiliation = ', '.join(part.strip() for part in affiliation_parts)
                    else:
                        affiliation = ''
                    country_div = next_sibling.find_next('div', class_='indvfulllistaddr')
                    country = country_div.text.strip() if country_div else ''
                    email_div = next_sibling.find_next('div', class_='indvlistemail')
                    email = email_div.text.strip() if email_div else ''
                    website_div = next_sibling.find_next('div', class_='indvlistwebsite')
                    website = website_div.text.strip() if website_div else ''
                    data_list.append([role_text, name, affiliation, country, email, website])
                next_sibling = next_sibling.find_next()

        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if save_path:
            with open(save_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Journal Name'])
                writer.writerow([journal_name])
                writer.writerow(['Role', 'Name', 'Affiliation', 'Country', 'Email', 'Website'])
                writer.writerows(data_list)

            messagebox.showinfo("Success", f"The editorial board data has been saved to '{os.path.basename(save_path)}'.")

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to fetch the editorial board data. Error: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")
