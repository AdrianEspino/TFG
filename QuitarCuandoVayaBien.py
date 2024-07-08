import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from urllib.parse import urljoin
from io import BytesIO
from PIL import Image, ImageTk
import webbrowser
import feedparser
import csv

# Funciones de scraping
def scrape_computer_journal(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        data = []
        for item in soup.select('div.editor-data'):
            editor = item.find('div', class_='editor-name').get_text(strip=True)
            affiliation = item.find('div', class_='editor-affiliation').get_text(strip=True)
            journal = 'Computer Journal'
            issn = '0018-9286'
            data.append([editor, affiliation, journal, issn, url])
        return data
    except requests.RequestException as e:
        return f"Error: {e}"

def scrape_jetc_editorial_board(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        data = []
        for item in soup.select('div.editor'):
            editor = item.find('h4').get_text(strip=True)
            affiliation = item.find('p').get_text(strip=True)
            journal = 'Journal on Emerging Technologies in Computing Systems (JETC)'
            issn = '1550-4832'
            data.append([editor, affiliation, journal, issn, url])
        return data
    except requests.RequestException as e:
        return f"Error: {e}"

def scrape_tnnls_editorial_board(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        data = []
        for item in soup.select('div.editor'):
            editor = item.find('h3').get_text(strip=True)
            affiliation = item.find('p').get_text(strip=True)
            journal = 'IEEE Transactions on Neural Networks and Learning Systems (TNNLS)'
            issn = '2162-237X'
            data.append([editor, affiliation, journal, issn, url])
        return data
    except requests.RequestException as e:
        return f"Error: {e}"

def export_data_to_csv(url, filename, data):
    if data is None:
        messagebox.showerror("Error", "No data to export.")
        return

    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Editor', 'Affiliation', 'Journal', 'ISSN', 'URL'])
        for row in data:
            writer.writerow(row)
    messagebox.showinfo("Success", f"Data exported to {filename}")

# Funciones de scraping general y búsqueda
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
            insert_link(result_text, link['url'], link['text'], index)
        result_text.insert(tk.END, "Images:\n")
        for index, image in enumerate(data['images']):
            insert_image(result_text, image['src'], image['alt'], index)

def insert_link(text_widget, url, text, index):
    tag_name = f"link{index}"
    text_widget.insert(tk.END, f"{text} - {url}\n", tag_name)
    text_widget.tag_bind(tag_name, "<Button-1>", lambda e, url=url: open_link(url))
    text_widget.tag_config(tag_name, foreground="blue", underline=True)
    text_widget.tag_bind(tag_name, "<Enter>", lambda e: text_widget.config(cursor="hand2"))
    text_widget.tag_bind(tag_name, "<Leave>", lambda e: text_widget.config(cursor=""))

def insert_image(text_widget, url, alt_text, index):
    tag_name = f"image{index}"
    text_widget.insert(tk.END, f"{alt_text} - {url}\n", tag_name)
    text_widget.tag_bind(tag_name, "<Button-1>", lambda e, url=url: show_image(url))
    text_widget.tag_config(tag_name, foreground="green", underline=True)
    text_widget.tag_bind(tag_name, "<Enter>", lambda e: text_widget.config(cursor="hand2"))
    text_widget.tag_bind(tag_name, "<Leave>", lambda e: text_widget.config(cursor=""))

def open_link(url):
    webbrowser.open_new(url)

def show_image(url):
    image_window = tk.Toplevel(root)
    image_window.title("Image Viewer")

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        img_data = response.content

        img = Image.open(BytesIO(img_data))
        img_tk = ImageTk.PhotoImage(img)

        image_label = tk.Label(image_window, image=img_tk)
        image_label.image = img_tk
        image_label.pack()
    except requests.RequestException as e:
        messagebox.showerror("Error", f"Error fetching image from URL: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"Error displaying image: {e}")

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

def fetch_arxiv_data():
    query = arxiv_entry.get()
    if not query:
        messagebox.showwarning("Input Error", "Please enter a search query")
        return

    results = search_arxiv(query)
    arxiv_result_text.delete('1.0', tk.END)
    if not results:
        arxiv_result_text.insert(tk.END, "No results found for the query.")
    else:
        for result in results:
            arxiv_result_text.insert(tk.END, f"Title: {result['title']}\n")
            arxiv_result_text.insert(tk.END, f"Summary: {result['summary']}\n")
            insert_link(arxiv_result_text, result['link'], result['link'], results.index(result))
            arxiv_result_text.insert(tk.END, "\n\n")

def fetch_pubmed_data():
    query = pubmed_entry.get()
    if not query:
        messagebox.showwarning("Input Error", "Please enter a search query")
        return

    results = search_pubmed(query)
    pubmed_result_text.delete('1.0', tk.END)
    if not results:
        pubmed_result_text.insert(tk.END, "No results found for the query.")
    else:
        for result in results:
            pubmed_result_text.insert(tk.END, f"Title: {result['title']}\n")
            pubmed_result_text.insert(tk.END, f"Summary: {result['summary']}\n")
            insert_link(pubmed_result_text, result['link'], result['link'], results.index(result))
            pubmed_result_text.insert(tk.END, "\n\n")

def show_frame(frame):
    frame.tkraise()

def start_application():
    splash.destroy()
    root.deiconify()
    root.state('zoomed')  # Open in fullscreen mode

# Setup the main application window
root = tk.Tk()
root.title("Web Scraper")
root.geometry("1000x600")

# Hide the main window initially
root.withdraw()

# Create a splash screen
splash = tk.Toplevel()
splash.title("Welcome")
splash.geometry("500x300")

# Make the splash screen fullscreen
splash.attributes("-fullscreen", True)

splash_label = tk.Label(splash, text="Welcome to the Web Scraper!", font=("Helvetica", 18))
splash_label.pack(expand=True)

start_button = tk.Button(splash, text="Start", command=start_application, font=("Helvetica", 14), bg="#3498DB", fg="white")
start_button.pack()

# Create a frame for the sidebar
sidebar = tk.Frame(root, bg="#3498DB", width=200, height=600, relief="sunken", borderwidth=2)
sidebar.pack(expand=False, fill="y", side="left", anchor="nw")

# Create a main content frame
main_content = tk.Frame(root, bg="white", width=800, height=600)
main_content.pack(expand=True, fill="both", side="right")

# Create frames for each section
frames = {}
for option in ["Web Scraper", "Arxiv", "PubMed", "Examples"]:
    frame = tk.Frame(main_content, bg="white")
    frame.place(relwidth=1, relheight=1)
    frames[option] = frame

# Function to add buttons to the sidebar
def add_sidebar_button(text, frame_name):
    button = tk.Button(sidebar, text=text, bg="#2980B9", fg="white", font=("Helvetica", 14), relief="flat",
                       command=lambda: show_frame(frames[frame_name]))
    button.pack(fill="x")

# Add buttons to the sidebar
add_sidebar_button("Web Scraper", "Web Scraper")
add_sidebar_button("Arxiv", "Arxiv")
add_sidebar_button("PubMed", "PubMed")
add_sidebar_button("Examples", "Examples")

# Add content to the Web Scraper frame
url_frame = ttk.Frame(frames["Web Scraper"], padding="10")
url_frame.pack(side=tk.TOP, fill=tk.X)
ttk.Label(url_frame, text="Enter URL:").pack(side=tk.LEFT)
url_entry = ttk.Entry(url_frame, width=50)
url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
ttk.Button(url_frame, text="Scrape", command=fetch_data).pack(side=tk.LEFT)
ttk.Button(url_frame, text="Export CSV", command=lambda: export_data_to_csv(url_entry.get(), "data.csv")).pack(side=tk.LEFT)

result_text = ScrolledText(frames["Web Scraper"], wrap=tk.WORD, width=100, height=30)
result_text.pack(fill=tk.BOTH, expand=True)

# Add content to the Arxiv frame
arxiv_frame = ttk.Frame(frames["Arxiv"], padding="10")
arxiv_frame.pack(side=tk.TOP, fill=tk.X)
ttk.Label(arxiv_frame, text="Enter Arxiv Query:").pack(side=tk.LEFT)
arxiv_entry = ttk.Entry(arxiv_frame, width=50)
arxiv_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
ttk.Button(arxiv_frame, text="Search", command=fetch_arxiv_data).pack(side=tk.LEFT)

arxiv_result_text = ScrolledText(frames["Arxiv"], wrap=tk.WORD, width=100, height=30)
arxiv_result_text.pack(fill=tk.BOTH, expand=True)

# Add content to the PubMed frame
pubmed_frame = ttk.Frame(frames["PubMed"], padding="10")
pubmed_frame.pack(side=tk.TOP, fill=tk.X)
ttk.Label(pubmed_frame, text="Enter PubMed Query:").pack(side=tk.LEFT)
pubmed_entry = ttk.Entry(pubmed_frame, width=50)
pubmed_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
ttk.Button(pubmed_frame, text="Search", command=fetch_pubmed_data).pack(side=tk.LEFT)

pubmed_result_text = ScrolledText(frames["PubMed"], wrap=tk.WORD, width=100, height=30)
pubmed_result_text.pack(fill=tk.BOTH, expand=True)

# Add content to the Examples frame
example_frame = ttk.Frame(frames["Examples"], padding="10")
example_frame.pack(side=tk.TOP, fill=tk.X)

example_links = [
    {"text": "Computer Journal", "url": "https://www.computer.org/csdl/journal/tp/about/107368", "filename": "computer_journal.csv", "scraper": scrape_computer_journal},
    {"text": "JETC Editorial Board", "url": "https://dl.acm.org/journal/jetc/editorial-board", "filename": "jetc_editorial_board.csv", "scraper": scrape_jetc_editorial_board},
    {"text": "TNNLS Editorial Board", "url": "https://cis.ieee.org/publications/t-neural-networks-and-learning-systems/tnnls-editor-and-associate-editors", "filename": "tnnls_editorial_board.csv", "scraper": scrape_tnnls_editorial_board},
]

def create_example_entry(parent, example):
    frame = ttk.Frame(parent)
    label = ttk.Label(frame, text=example["text"])
    label.pack(side=tk.LEFT)
    button = ttk.Button(frame, text="Export CSV", command=lambda: export_and_show_data(example))
    button.pack(side=tk.LEFT)
    frame.pack(fill=tk.X, pady=5)

def export_and_show_data(example):
    data = example["scraper"](example["url"])
    if isinstance(data, str):
        messagebox.showerror("Error", data)
    else:
        example_result_text.delete('1.0', tk.END)
        for row in data:
            example_result_text.insert(tk.END, f"Editor: {row[0]}, Affiliation: {row[1]}, Journal: {row[2]}, ISSN: {row[3]}, URL: {row[4]}\n")
        export_data_to_csv(example["url"], example["filename"], data)

example_result_text = ScrolledText(frames["Examples"], wrap=tk.WORD, width=100, height=30)
example_result_text.pack(fill=tk.BOTH, expand=True)

for example in example_links:
    create_example_entry(example_frame, example)

# Initially show the Web Scraper frame
show_frame(frames["Web Scraper"])

root.mainloop()
