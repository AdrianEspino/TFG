import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import webbrowser

class App(tk.Tk):
    def __init__(self, scraper, arxiv_search, pubmed_search):
        super().__init__()
        self.scraper = scraper
        self.arxiv_search = arxiv_search
        self.pubmed_search = pubmed_search
        self.title("Web Scraper")
        self.geometry("800x600")

        self.create_widgets()

    def create_widgets(self):
        self.menu_frame = ttk.Frame(self, padding="10")
        self.menu_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W, tk.E))

        ttk.Button(self.menu_frame, text="Web Scraper", command=self.show_scraper).grid(row=0, column=0, sticky=tk.W)
        ttk.Button(self.menu_frame, text="Arxiv", command=self.show_arxiv).grid(row=1, column=0, sticky=tk.W)
        ttk.Button(self.menu_frame, text="PubMed", command=self.show_pubmed).grid(row=2, column=0, sticky=tk.W)

        self.content_frame = ttk.Frame(self, padding="10")
        self.content_frame.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.W, tk.E))
        
        self.url_label = ttk.Label(self.content_frame, text="Enter URL:")
        self.url_entry = ttk.Entry(self.content_frame, width=50)
        self.scrape_button = ttk.Button(self.content_frame, text="Scrape", command=self.fetch_data)
        self.result_text = ScrolledText(self.content_frame, wrap=tk.WORD, width=80, height=20)

        self.query_label = ttk.Label(self.content_frame, text="Enter Query:")
        self.query_entry = ttk.Entry(self.content_frame, width=50)
        self.arxiv_button = ttk.Button(self.content_frame, text="Search Arxiv", command=self.search_arxiv)
        self.pubmed_button = ttk.Button(self.content_frame, text="Search PubMed", command=self.search_pubmed)
        
        self.show_scraper()

    def show_scraper(self):
        self.clear_content()
        self.url_label.grid(row=0, column=0, sticky=tk.W)
        self.url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        self.scrape_button.grid(row=0, column=2, sticky=tk.E)
        self.result_text.grid(row=1, column=0, columnspan=3, sticky=(tk.N, tk.S, tk.W, tk.E))

    def show_arxiv(self):
        self.clear_content()
        self.query_label.grid(row=0, column=0, sticky=tk.W)
        self.query_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        self.arxiv_button.grid(row=0, column=2, sticky=tk.E)
        self.result_text.grid(row=1, column=0, columnspan=3, sticky=(tk.N, tk.S, tk.W, tk.E))

    def show_pubmed(self):
        self.clear_content()
        self.query_label.grid(row=0, column=0, sticky=tk.W)
        self.query_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        self.pubmed_button.grid(row=0, column=2, sticky=tk.E)
        self.result_text.grid(row=1, column=0, columnspan=3, sticky=(tk.N, tk.S, tk.W, tk.E))

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.grid_forget()

    def fetch_data(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showwarning("Input Error", "Please enter a URL")
            return
        data = self.scraper(url)
        self.display_data(data)

    def search_arxiv(self):
        query = self.query_entry.get()
        if not query:
            messagebox.showwarning("Input Error", "Please enter a query")
            return
        data = self.arxiv_search(query)
        self.display_data(data)

    def search_pubmed(self):
        query = self.query_entry.get()
        if not query:
            messagebox.showwarning("Input Error", "Please enter a query")
            return
        data = self.pubmed_search(query)
        self.display_data(data)

    def display_data(self, data):
        self.result_text.delete('1.0', tk.END)
        if isinstance(data, str):
            self.result_text.insert(tk.END, data)
        else:
            self.result_text.insert(tk.END, f"Title: {data['title']}\n\n")
            self.result_text.insert(tk.END, "Paragraphs:\n")
            for para in data['paragraphs']:
                self.result_text.insert(tk.END, f"{para}\n\n")
            self.result_text.insert(tk.END, "Links:\n")
            for index, link in enumerate(data['links']):
                self.insert_link(self.result_text, link['url'], link['text'], index)
            self.result_text.insert(tk.END, "Images:\n")
            for index, image in enumerate(data['images']):
                self.insert_image(self.result_text, image['src'], image['alt'], index)

    def insert_link(self, text_widget, url, text, index):
        tag_name = f"link{index}"
        text_widget.insert(tk.END, f"{text} - {url}\n", tag_name)
        text_widget.tag_bind(tag_name, "<Button-1>", lambda e, url=url: self.open_link(url))
        text_widget.tag_config(tag_name, foreground="blue", underline=True)
        text_widget.tag_bind(tag_name, "<Enter>", lambda e: text_widget.config(cursor="hand2"))
        text_widget.tag_bind(tag_name, "<Leave>", lambda e: text_widget.config(cursor=""))

    def insert_image(self, text_widget, url, alt_text, index):
        tag_name = f"image{index}"
        text_widget.insert(tk.END, f"{alt_text} - {url}\n", tag_name)
        text_widget.tag_bind(tag_name, "<Button-1>", lambda e, url=url: self.show_image(url))
        text_widget.tag_config(tag_name, foreground="green", underline=True)
        text_widget.tag_bind(tag_name, "<Enter>", lambda e: text_widget.config(cursor="hand2"))
        text_widget.tag_bind(tag_name, "<Leave>", lambda e: text_widget.config(cursor=""))

    def open_link(self, url):
        webbrowser.open_new(url)

    def show_image(self, url):
        image_window = tk.Toplevel(self)
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
