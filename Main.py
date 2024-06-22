from Interfaz import App
from Funcionalidades import scrape_website, search_arxiv, search_pubmed

if __name__ == "__main__":
    app = App(scrape_website, search_arxiv, search_pubmed)
    app.mainloop()