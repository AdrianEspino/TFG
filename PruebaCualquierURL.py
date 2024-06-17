import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import scrolledtext, messagebox
from urllib.parse import urljoin
from io import BytesIO
from PIL import Image, ImageTk
import webbrowser

def fetch_url_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text, url
    except requests.RequestException as e:
        messagebox.showerror("Error", f"Error fetching data from URL: {e}")
        return None, None

def extract_information(html_content, base_url):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Title
    title = soup.title.string if soup.title else "No title found"
    
    # Paragraphs
    paragraphs = [p.get_text() for p in soup.find_all('p')]
    
    # Headers
    headers = [h.get_text() for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
    
    # Links
    links = [{'text': a.get_text(), 'url': urljoin(base_url, a['href'])} for a in soup.find_all('a', href=True)]
    
    # Images
    images = [{'alt': img.get('alt', ''), 'src': urljoin(base_url, img['src'])} for img in soup.find_all('img', src=True)]
    
    # Tables
    tables = []
    for table in soup.find_all('table'):
        rows = []
        for row in table.find_all('tr'):
            cells = [cell.get_text() for cell in row.find_all(['td', 'th'])]
            rows.append(cells)
        tables.append(rows)
    
    return {
        "title": title,
        "paragraphs": paragraphs,
        "headers": headers,
        "links": links,
        "images": images,
        "tables": tables
    }

def display_url_info(info):
    result_window = tk.Toplevel(root)
    result_window.title("URL Information")
    
    text_widget = scrolledtext.ScrolledText(result_window, wrap=tk.WORD, width=100, height=40)
    text_widget.pack(expand=True, fill='both')

    text_widget.insert(tk.END, f"Title: {info['title']}\n\n")
    
    text_widget.insert(tk.END, "Headers:\n")
    for header in info['headers']:
        text_widget.insert(tk.END, f"{header}\n")
    
    text_widget.insert(tk.END, "\nParagraphs:\n")
    for paragraph in info['paragraphs']:
        text_widget.insert(tk.END, f"{paragraph}\n")

    text_widget.insert(tk.END, "\nLinks:\n")
    for link in info['links']:
        link_text = f"{link['text']} - {link['url']}\n"
        start = text_widget.index(tk.END)
        text_widget.insert(tk.END, link_text)
        end = text_widget.index(tk.END)
        # Use a unique tag for each link to ensure the event binds correctly
        tag_name = f"link-{link['url']}"
        text_widget.tag_add(tag_name, start, end)
        text_widget.tag_bind(tag_name, '<Button-1>', lambda e, url=link['url']: open_link(url))
        text_widget.tag_bind(tag_name, '<Enter>', lambda e: text_widget.config(cursor="hand2"))
        text_widget.tag_bind(tag_name, '<Leave>', lambda e: text_widget.config(cursor=""))

    text_widget.insert(tk.END, "\nImages:\n")
    for image in info['images']:
        image_text = f"{image['alt']} - {image['src']}\n"
        start = text_widget.index(tk.END)
        text_widget.insert(tk.END, image_text)
        end = text_widget.index(tk.END)
        # Use a unique tag for each image to ensure the event binds correctly
        tag_name = f"image-{image['src']}"
        text_widget.tag_add(tag_name, start, end)
        text_widget.tag_bind(tag_name, '<Button-1>', lambda e, url=image['src']: show_image(url))
        text_widget.tag_bind(tag_name, '<Enter>', lambda e: text_widget.config(cursor="hand2"))
        text_widget.tag_bind(tag_name, '<Leave>', lambda e: text_widget.config(cursor=""))

    text_widget.insert(tk.END, "\nTables:\n")
    for table in info['tables']:
        for row in table:
            text_widget.insert(tk.END, "\t".join(row) + "\n")
        text_widget.insert(tk.END, "\n")
    
    text_widget.configure(state='disabled')

def open_link(url):
    webbrowser.open(url)

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

def on_fetch_url():
    url = url_entry.get()
    if not url.startswith("http://") and not url.startswith("https://"):
        messagebox.showerror("Error", "Please enter a valid URL starting with http:// or https://")
        return
    
    html_content, base_url = fetch_url_content(url)
    if html_content:
        info = extract_information(html_content, base_url)
        display_url_info(info)

# Setup the main application window
root = tk.Tk()
root.title("Web Scraper")

# URL entry
url_label = tk.Label(root, text="Enter URL:")
url_label.pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

# Fetch button
fetch_button = tk.Button(root, text="Fetch URL Information", command=on_fetch_url)
fetch_button.pack(pady=20)

root.mainloop()