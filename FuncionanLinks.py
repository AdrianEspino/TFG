import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import requests
from bs4 import BeautifulSoup
import webbrowser
from urllib.parse import urljoin

def scrape_website(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.title.string if soup.title else 'No title found'
        paragraphs = [p.text for p in soup.find_all('p')]
        links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True)]

        return {
            'title': title,
            'paragraphs': paragraphs,
            'links': links
        }
    except requests.RequestException as e:
        return f"Error: {e}"

def fetch_data():
    url = url_entry.get()
    if not url:
        messagebox.showwarning("Input Error", "Please enter a URL")
        return
    
    data = scrape_website(url)
    if isinstance(data, str):
        result_text.delete('1.0', tk.END)
        result_text.insert(tk.END, data)
    else:
        result_text.delete('1.0', tk.END)
        result_text.insert(tk.END, f"Title: {data['title']}\n\n")
        result_text.insert(tk.END, "Paragraphs:\n")
        for para in data['paragraphs']:
            result_text.insert(tk.END, f"{para}\n\n")
        result_text.insert(tk.END, "Links:\n")
        for index, link in enumerate(data['links']):
            insert_link(result_text, link, index)

def insert_link(text_widget, url, index):
    tag_name = f"link{index}"
    text_widget.insert(tk.END, url + "\n", tag_name)
    text_widget.tag_bind(tag_name, "<Button-1>", lambda e, url=url: open_link(url))
    text_widget.tag_config(tag_name, foreground="blue", underline=True)
    text_widget.tag_bind(tag_name, "<Enter>", lambda e: text_widget.config(cursor="hand2"))
    text_widget.tag_bind(tag_name, "<Leave>", lambda e: text_widget.config(cursor=""))

def open_link(url):
    webbrowser.open_new(url)

root = tk.Tk()
root.title("Web Scraper")

url_frame = ttk.Frame(root, padding="10")
url_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
ttk.Label(url_frame, text="Enter URL:").grid(row=0, column=0, sticky=tk.W)
url_entry = ttk.Entry(url_frame, width=50)
url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
ttk.Button(url_frame, text="Scrape", command=fetch_data).grid(row=0, column=2, sticky=tk.E)

result_frame = ttk.Frame(root, padding="10")
result_frame.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.W, tk.E))
ttk.Label(result_frame, text="Results:").grid(row=0, column=0, sticky=tk.W)
result_text = ScrolledText(result_frame, wrap=tk.WORD, width=80, height=20)
result_text.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.W, tk.E))

root.columnconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
result_frame.columnconfigure(0, weight=1)
result_frame.rowconfigure(1, weight=1)

root.mainloop()
