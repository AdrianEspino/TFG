import tkinter as tk
from tkinter import messagebox
import requests
from bs4 import BeautifulSoup

def fetch_pubmed(query):
    url = f'https://pubmed.ncbi.nlm.nih.gov/?term={query}'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    results = []

    for item in soup.select('.docsum-content'):
        title = item.select_one('.docsum-title').text.strip()
        snippet = item.select_one('.full-view-snippet').text.strip() if item.select_one('.full-view-snippet') else ''
        link = 'https://pubmed.ncbi.nlm.nih.gov' + item.select_one('.docsum-title')['href']
        results.append({
            'title': title,
            'snippet': snippet,
            'link': link
        })

    return results

def fetch_arxiv(query):
    url = f'http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=10'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'xml')
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

def fetch_results(source, query):
    if source == 'PubMed':
        return fetch_pubmed(query)
    elif source == 'arXiv':
        return fetch_arxiv(query)
    else:
        return []

def display_results(results):
    result_window = tk.Toplevel(root)
    result_window.title("Results")
    for result in results:
        tk.Label(result_window, text=f"Title: {result['title']}", wraplength=600, justify='left').pack()
        tk.Label(result_window, text=f"Snippet: {result['snippet']}", wraplength=600, justify='left').pack()
        tk.Label(result_window, text=f"Link: {result['link']}", fg="blue", cursor="hand2").pack()
        tk.Label(result_window, text="\n").pack()

def on_search():
    query = query_entry.get()
    source = source_var.get()
    if not query:
        messagebox.showwarning("Input Error", "Please enter a search query")
        return

    results = fetch_results(source, query)
    if results:
        display_results(results)
    else:
        messagebox.showinfo("No Results", "No results found for the query")

root = tk.Tk()
root.title("Academic Scraper")

tk.Label(root, text="Search Query:").grid(row=0, column=0, padx=10, pady=10)
query_entry = tk.Entry(root, width=50)
query_entry.grid(row=0, column=1, padx=10, pady=10)

source_var = tk.StringVar(value='PubMed')
tk.Radiobutton(root, text="PubMed", variable=source_var, value='PubMed').grid(row=1, column=0, padx=10, pady=10)
tk.Radiobutton(root, text="arXiv", variable=source_var, value='arXiv').grid(row=1, column=1, padx=10, pady=10)

tk.Button(root, text="Search", command=on_search).grid(row=2, column=0, columnspan=2, pady=20)

root.mainloop()
