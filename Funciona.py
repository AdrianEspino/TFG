import tkinter as tk
from tkinter import messagebox, ttk
import requests
from bs4 import BeautifulSoup
import webbrowser

# Funci�n para obtener resultados de PubMed
def fetch_pubmed(query):
    try:
        url = f'https://pubmed.ncbi.nlm.nih.gov/?term={query}'
        response = requests.get(url)
        response.raise_for_status()
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
    except requests.RequestException as e:
        messagebox.showerror("Error", f"Error fetching data from PubMed: {e}")
        return []

# Funci�n para obtener resultados de arXiv
def fetch_arxiv(query):
    try:
        url = f'http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=10'
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'xml')

        # Depuraci�n: imprimir el contenido de la respuesta
        print(soup.prettify())

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
        messagebox.showerror("Error", f"Error fetching data from arXiv: {e}")
        return []

# Funci�n para obtener resultados dependiendo de la fuente
def fetch_results(source, query):
    if source == 'PubMed':
        return fetch_pubmed(query)
    elif source == 'arXiv':
        return fetch_arxiv(query)
    else:
        return []

# Funci�n para mostrar los resultados
def display_results(results):
    result_window = tk.Toplevel(root)
    result_window.title("Results")

    canvas = tk.Canvas(result_window)
    scrollbar = ttk.Scrollbar(result_window, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    for result in results:
        frame = ttk.Frame(scrollable_frame, padding="10")
        frame.pack(fill="x")

        title_text = tk.Text(frame, wrap='word', height=2)
        title_text.insert(tk.END, f"Title: {result['title']}")
        title_text.config(state=tk.DISABLED)
        title_text.pack(fill="x")

        if 'snippet' in result:
            snippet_text = tk.Text(frame, wrap='word', height=2)
            snippet_text.insert(tk.END, f"Snippet: {result['snippet']}")
            snippet_text.config(state=tk.DISABLED)
            snippet_text.pack(fill="x")

        if 'summary' in result:
            summary_text = tk.Text(frame, wrap='word', height=3)
            summary_text.insert(tk.END, f"Summary: {result['summary']}")
            summary_text.config(state=tk.DISABLED)
            summary_text.pack(fill="x")

        link_label = tk.Label(frame, text=f"Link: {result['link']}", fg="blue", cursor="hand2")
        link_label.pack(anchor='w')
        link_label.bind("<Button-1>", lambda e, url=result['link']: webbrowser.open_new(url))

        spacer = tk.Label(frame, text="\n")
        spacer.pack()

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

# Funci�n para manejar el evento de b�squeda
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

# Configuraci�n de la interfaz de usuario
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