import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from urllib.parse import urljoin
from io import BytesIO
from PIL import Image, ImageTk
import webbrowser

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

def show_frame(frame):
    frame.tkraise()

# Setup the main application window
root = tk.Tk()
root.title("Scientific Articles Scraper")
root.geometry("1000x600")

# Create a frame for the sidebar
sidebar = tk.Frame(root, bg="#2C3E50", width=200, height=600, relief="sunken", borderwidth=2)
sidebar.pack(expand=False, fill="y", side="left", anchor="nw")

# Create a main content frame
main_content = tk.Frame(root, bg="white", width=800, height=600)
main_content.pack(expand=True, fill="both", side="right")

# Create frames for each section
frames = {}
for option in ["Web Scraper", "Arxiv", "PubMed"]:
    frame = tk.Frame(main_content, bg="white")
    frame.place(relwidth=1, relheight=1)
    frames[option] = frame

# Function to add buttons to the sidebar
def add_sidebar_button(text, frame_name):
    button = tk.Button(sidebar, text=text, bg="#34495E", fg="white", font=("Helvetica", 14), relief="flat",
                       command=lambda: show_frame(frames[frame_name]))
    button.pack(fill="x")

# Add buttons to the sidebar
add_sidebar_button("Web Scraper", "Web Scraper")
add_sidebar_button("Arxiv", "Arxiv")
add_sidebar_button("PubMed", "PubMed")

# Add content to the Web Scraper frame
url_frame = ttk.Frame(frames["Web Scraper"], padding="10")
url_frame.pack(side=tk.TOP, fill=tk.X)
ttk.Label(url_frame, text="Enter URL:").pack(side=tk.LEFT)
url_entry = ttk.Entry(url_frame, width=50)
url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
ttk.Button(url_frame, text="Scrape", command=fetch_data).pack(side=tk.LEFT)

result_text = ScrolledText(frames["Web Scraper"], wrap=tk.WORD, width=100, height=30)
result_text.pack(fill=tk.BOTH, expand=True)

# Initially show the Web Scraper frame
show_frame(frames["Web Scraper"])

root.mainloop()