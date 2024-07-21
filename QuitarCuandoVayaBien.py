import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
from urllib.parse import urljoin
from io import BytesIO
from PIL import Image, ImageTk
import webbrowser
import feedparser
import csv
import os

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

def show_editorial_board_data():
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

        editorial_result_text.delete('1.0', tk.END)
        editorial_result_text.insert(tk.END, f"Journal Name: {journal_name}\n\n")
        for data in data_list:
            editorial_result_text.insert(tk.END, f"Role: {data[0]}\n")
            editorial_result_text.insert(tk.END, f"Name: {data[1]}\n")
            editorial_result_text.insert(tk.END, f"Affiliation: {data[2]}\n")
            editorial_result_text.insert(tk.END, f"Country: {data[3]}\n")
            editorial_result_text.insert(tk.END, "\n")

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
        
def show_editorial_board_data_TNNLS():
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

        editorial_tnnls_result_text.delete('1.0', tk.END)
        editorial_tnnls_result_text.insert(tk.END, f"Journal Name: {journal_name}\n\n")
        for data in data_list:
            editorial_tnnls_result_text.insert(tk.END, f"Role: {data[0]}\n")
            editorial_tnnls_result_text.insert(tk.END, f"Name: {data[1]}\n")
            editorial_tnnls_result_text.insert(tk.END, f"Affiliation: {data[2]}\n")
            editorial_tnnls_result_text.insert(tk.END, f"Country: {data[3]}\n")
            editorial_tnnls_result_text.insert(tk.END, f"Email: {data[4]}\n")
            editorial_tnnls_result_text.insert(tk.END, f"Website: {data[5]}\n")
            editorial_tnnls_result_text.insert(tk.END, "\n")

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to fetch the editorial board data. Error: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")

# Initialize root window
root = tk.Tk()
root.title("Web Scraper Application")
root.geometry("1000x600")
root.withdraw()

# Splash screen
splash = tk.Toplevel()
splash.title("Welcome")
splash.geometry("500x300")
splash.attributes("-fullscreen", True)

splash_label = tk.Label(splash, text="Welcome to the Web Scraper!", font=("Helvetica", 18))
splash_label.pack(expand=True)

def start_application():
    splash.destroy()
    root.deiconify()

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
for option in ["Web Scraper", "Arxiv", "PubMed", "Editorial Board", "Editorial Board TNNLS"]:
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
add_sidebar_button("Editorial Board", "Editorial Board")
add_sidebar_button("Editorial Board TNNLS", "Editorial Board TNNLS")

# Function to show a frame
def show_frame(frame):
    frame.tkraise()

# Add content to the Web Scraper frame
url_frame = ttk.Frame(frames["Web Scraper"], padding="10")
url_frame.pack(side=tk.TOP, fill=tk.X)
ttk.Label(url_frame, text="Enter URL:").pack(side=tk.LEFT)
url_entry = ttk.Entry(url_frame, width=50)
url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
ttk.Button(url_frame, text="Scrape", command=lambda: fetch_data(url_entry.get())).pack(side=tk.LEFT)

result_text = ScrolledText(frames["Web Scraper"], wrap=tk.WORD, width=100, height=30)
result_text.pack(fill=tk.BOTH, expand=True)

# Add content to the Arxiv frame
arxiv_frame = ttk.Frame(frames["Arxiv"], padding="10")
arxiv_frame.pack(side=tk.TOP, fill=tk.X)
ttk.Label(arxiv_frame, text="Enter Arxiv Query:").pack(side=tk.LEFT)
arxiv_entry = ttk.Entry(arxiv_frame, width=50)
arxiv_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
ttk.Button(arxiv_frame, text="Search", command=lambda: fetch_arxiv_data(arxiv_entry.get())).pack(side=tk.LEFT)

arxiv_result_text = ScrolledText(frames["Arxiv"], wrap=tk.WORD, width=100, height=30)
arxiv_result_text.pack(fill=tk.BOTH, expand=True)

# Add content to the PubMed frame
pubmed_frame = ttk.Frame(frames["PubMed"], padding="10")
pubmed_frame.pack(side=tk.TOP, fill=tk.X)
ttk.Label(pubmed_frame, text="Enter PubMed Query:").pack(side=tk.LEFT)
pubmed_entry = ttk.Entry(pubmed_frame, width=50)
pubmed_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
ttk.Button(pubmed_frame, text="Search", command=lambda: fetch_pubmed_data(pubmed_entry.get())).pack(side=tk.LEFT)

pubmed_result_text = ScrolledText(frames["PubMed"], wrap=tk.WORD, width=100, height=30)
pubmed_result_text.pack(fill=tk.BOTH, expand=True)

# Add content to the Editorial Board frame
editorial_frame = ttk.Frame(frames["Editorial Board"], padding="10")
editorial_frame.pack(side=tk.TOP, fill=tk.X)

ttk.Button(editorial_frame, text="Download Editorial Board CSV", command=fetch_editorial_board_data).pack(side=tk.LEFT, padx=10)
ttk.Button(editorial_frame, text="Show Editorial Board Data", command=show_editorial_board_data).pack(side=tk.LEFT, padx=10)
editorial_link = tk.Label(editorial_frame, text="https://dl.acm.org/journal/jetc/editorial-board", fg="blue", cursor="hand2")
editorial_link.pack(side=tk.LEFT, padx=10)
editorial_link.bind("<Button-1>", lambda e: open_link("https://dl.acm.org/journal/jetc/editorial-board"))

editorial_result_text = ScrolledText(frames["Editorial Board"], wrap=tk.WORD, width=100, height=30)
editorial_result_text.pack(fill=tk.BOTH, expand=True)

# Add content to the Editorial Board TNNLS frame
editorial_tnnls_frame = ttk.Frame(frames["Editorial Board TNNLS"], padding="10")
editorial_tnnls_frame.pack(side=tk.TOP, fill=tk.X)

ttk.Button(editorial_tnnls_frame, text="Download Editorial Board CSV", command=fetch_editorial_board_data_TNNLS).pack(side=tk.LEFT, padx=10)
ttk.Button(editorial_tnnls_frame, text="Show Editorial Board Data", command=show_editorial_board_data_TNNLS).pack(side=tk.LEFT, padx=10)
editorial_tnnls_link = tk.Label(editorial_tnnls_frame, text="https://cis.ieee.org/publications/t-neural-networks-and-learning-systems/tnnls-editor-and-associate-editors", fg="blue", cursor="hand2")
editorial_tnnls_link.pack(side=tk.LEFT, padx=10)
editorial_tnnls_link.bind("<Button-1>", lambda e: open_link("https://cis.ieee.org/publications/t-neural-networks-and-learning-systems/tnnls-editor-and-associate-editors"))

editorial_tnnls_result_text = ScrolledText(frames["Editorial Board TNNLS"], wrap=tk.WORD, width=100, height=30)
editorial_tnnls_result_text.pack(fill=tk.BOTH, expand=True)

# Initially show the Web Scraper frame
show_frame(frames["Web Scraper"])

root.mainloop()