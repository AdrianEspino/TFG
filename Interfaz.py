import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
import requests
from io import BytesIO
import webbrowser
from Funcionalidades import scrape_website, search_arxiv, search_pubmed

class App(tk.Tk):
    def __init__(self, scrape_website_func, search_arxiv_func, search_pubmed_func):
        super().__init__()
        self.scrape_website = scrape_website_func
        self.search_arxiv = search_arxiv_func
        self.search_pubmed = search_pubmed_func
        
        self.title("Web Scraper")
        self.geometry("900x600")
        self.configure(bg="#f0f0f0")

        self.show_start_screen()

    def show_start_screen(self):
        start_frame = tk.Frame(self, bg="#f0f0f0")
        start_frame.pack(expand=True, fill="both")

        title_label = tk.Label(start_frame, text="Web Scraper", font=("Arial", 32, "bold"), bg="#f0f0f0", fg="#333")
        title_label.pack(pady=50)

        start_button = tk.Button(start_frame, text="Iniciar", font=("Arial", 20), bg="#0078D7", fg="white", command=self.show_main_screen)
        start_button.pack(pady=20)

    def show_main_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

        main_frame = tk.Frame(self, bg="#f0f0f0")
        main_frame.pack(expand=True, fill="both")

        sidebar = tk.Frame(main_frame, bg="#0078D7", width=200)
        sidebar.pack(fill="y", side="left")

        content_frame = tk.Frame(main_frame, bg="#f0f0f0")
        content_frame.pack(expand=True, fill="both", side="left")

        button_styles = {"font": ("Arial", 14), "bg": "#0078D7", "fg": "white", "activebackground": "#005bb5"}

        scrape_button = tk.Button(sidebar, text="Web Scraper", **button_styles, command=lambda: self.show_scrape_frame(content_frame))
        scrape_button.pack(pady=10, padx=10, fill="x")

        arxiv_button = tk.Button(sidebar, text="Arxiv", **button_styles, command=lambda: self.show_arxiv_frame(content_frame))
        arxiv_button.pack(pady=10, padx=10, fill="x")

        pubmed_button = tk.Button(sidebar, text="PubMed", **button_styles, command=lambda: self.show_pubmed_frame(content_frame))
        pubmed_button.pack(pady=10, padx=10, fill="x")

        self.show_scrape_frame(content_frame)

    def show_scrape_frame(self, parent):
        for widget in parent.winfo_children():
            widget.destroy()

        url_frame = tk.Frame(parent, bg="#f0f0f0", padx=10, pady=10)
        url_frame.pack(fill="x")

        tk.Label(url_frame, text="Enter URL:", bg="#f0f0f0", font=("Arial", 14)).pack(side="left", padx=5)
        self.url_entry = tk.Entry(url_frame, font=("Arial", 14), width=50)
        self.url_entry.pack(side="left", padx=5)
        tk.Button(url_frame, text="Scrape", font=("Arial", 14), bg="#0078D7", fg="white", command=self.fetch_data).pack(side="left", padx=5)

        self.result_text = ScrolledText(parent, wrap=tk.WORD, font=("Arial", 12), bg="#ffffff")
        self.result_text.pack(expand=True, fill="both", padx=10, pady=10)

    def show_arxiv_frame(self, parent):
        for widget in parent.winfo_children():
            widget.destroy()

        query_frame = tk.Frame(parent, bg="#f0f0f0", padx=10, pady=10)
        query_frame.pack(fill="x")

        tk.Label(query_frame, text="Enter Arxiv Query:", bg="#f0f0f0", font=("Arial", 14)).pack(side="left", padx=5)
        self.arxiv_query_entry = tk.Entry(query_frame, font=("Arial", 14), width=50)
        self.arxiv_query_entry.pack(side="left", padx=5)
        tk.Button(query_frame, text="Search", font=("Arial", 14), bg="#0078D7", fg="white", command=self.perform_search_arxiv).pack(side="left", padx=5)

        self.result_text = ScrolledText(parent, wrap=tk.WORD, font=("Arial", 12), bg="#ffffff")
        self.result_text.pack(expand=True, fill="both", padx=10, pady=10)

    def show_pubmed_frame(self, parent):
        for widget in parent.winfo_children():
            widget.destroy()

        query_frame = tk.Frame(parent, bg="#f0f0f0", padx=10, pady=10)
        query_frame.pack(fill="x")

        tk.Label(query_frame, text="Enter PubMed Query:", bg="#f0f0f0", font=("Arial", 14)).pack(side="left", padx=5)
        self.pubmed_query_entry = tk.Entry(query_frame, font=("Arial", 14), width=50)
        self.pubmed_query_entry.pack(side="left", padx=5)
        tk.Button(query_frame, text="Search", font=("Arial", 14), bg="#0078D7", fg="white", command=self.perform_search_pubmed).pack(side="left", padx=5)

        self.result_text = ScrolledText(parent, wrap=tk.WORD, font=("Arial", 12), bg="#ffffff")
        self.result_text.pack(expand=True, fill="both", padx=10, pady=10)

    def fetch_data(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showwarning("Input Error", "Please enter a URL")
            return

        data = self.scrape_website(url)
        self.display_data(data)

    def perform_search_arxiv(self):
        query = self.arxiv_query_entry.get()
        if not query:
            messagebox.showwarning("Input Error", "Please enter an Arxiv query")
            return

        data = self.search_arxiv(query)
        self.display_data(data)

    def perform_search_pubmed(self):
        query = self.pubmed_query_entry.get()
        if not query:
            messagebox.showwarning("Input Error", "Please enter a PubMed query")
            return

        data = self.search_pubmed(query)
        self.display_data(data)

    def display_data(self, data):
        self.result_text.delete(1.0, tk.END)

        if isinstance(data, str):
            self.result_text.insert(tk.END, data)
            return

        if 'title' in data:
            self.result_text.insert(tk.END, f"Title: {data['title']}\n\n")
            self.result_text.insert(tk.END, f"Content:\n{data['content']}\n\n")
            self.result_text.insert(tk.END, "Images:\n")
            for img_url in data['images']:
                self.result_text.insert(tk.END, img_url + "\n")
        else:
            for item in data:
                self.result_text.insert(tk.END, f"Title: {item['title']}\n")
                self.result_text.insert(tk.END, f"Authors: {item['authors']}\n")
                self.result_text.insert(tk.END, f"Summary: {item['summary']}\n")
                self.result_text.insert(tk.END, "Links:\n")
                for link in item['links']:
                    self.insert_link(self.result_text, link)
                self.result_text.insert(tk.END, "PDFs:\n")
                for pdf in item['pdfs']:
                    self.insert_link(self.result_text, pdf)
                self.result_text.insert(tk.END, "\n\n")

    def insert_link(self, text_widget, url):
        tag_name = "link" + str(hash(url))
        text_widget.tag_config(tag_name, foreground="blue", underline=True)
        text_widget.tag_bind(tag_name, "<Button-1>", lambda e: webbrowser.open_new(url))
        text_widget.insert(tk.END, url + "\n", tag_name)

    def display_image(self, img_url):
        try:
            response = requests.get(img_url)
            response.raise_for_status()
            img_data = response.content
            img = Image.open(BytesIO(img_data))
            img = img.resize((300, 300), Image.ANTIALIAS)
            img_tk = ImageTk.PhotoImage(img)

            image_window = tk.Toplevel(self)
            image_window.title("Image")
            image_label = tk.Label(image_window, image=img_tk)
            image_label.image = img_tk
            image_label.pack()
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Error fetching image from URL: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error displaying image: {e}")

if __name__ == "__main__":
    app = App(scrape_website, search_arxiv, search_pubmed)
    app.mainloop()
