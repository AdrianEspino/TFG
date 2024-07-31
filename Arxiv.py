import requests
import feedparser
from tkinter import messagebox
import tkinter as tk

def scrapear_arxiv(query):
    '''
    Busca artículos en arXiv utilizando una consulta y devuelve una lista de resultados.
    :param query: str - La consulta de búsqueda para encontrar artículos en arXiv.
    :return: list - Una lista de diccionarios, cada uno representando un artículo con su título, resumen y enlace.
    '''
    # URL para la API de arXiv.
    url_arxiv = "http://export.arxiv.org/api/query?"
    #URL para hacer la busqueda
    url_busqueda = f"{url_arxiv}search_query=all:{query}&start=0"
    # Realiza una solicitud HTTP a la URL de búsqueda y analiza la respuesta con feedparser
    respuesta = requests.get(url_busqueda)
    feed = feedparser.parse(respuesta.content)
    # Inicializa una lista para almacenar los resultados de búsqueda.
    resultados = []
    # Itera sobre cada entrada en el feed creando un diccionario para almacenar información del artículo.
    for entry in feed.entries:
        autores = ', '.join(author.name for author in entry.authors) if 'authors' in entry else 'No hay autores disponibles'
        fecha_publicacion = entry.published if 'published' in entry else 'No hay fecha de publicación disponible'
        categorias = ', '.join(tag.term for tag in entry.tags) if 'tags' in entry else 'No hay categorías disponibles'
        comentarios = entry.arxiv_comment if 'arxiv_comment' in entry else 'No hay comentarios disponibles'
        referencia_journal = entry.arxiv_journal_ref if 'arxiv_journal_ref' in entry else 'No hay referencia a journal disponible'
        resultado = {
            'titulo': entry.title,
            'resumen': entry.summary,
            'link': entry.link,
            'autores': autores,
            'fecha_publicacion': fecha_publicacion,
            'categorias': categorias,
            'comentarios': comentarios,
            'referencia_journal': referencia_journal
        }
        resultados.append(resultado)
    return resultados

def mostrar_arxiv(query_arxiv,widget_arxiv,insertar_link):
    # Obtiene la query insertada por el usuario y verifica que no está vacía
    query = query_arxiv.get()
    if not query:
        messagebox.showwarning("Input Error", "Por favor, introduzca una consulta valida")
        return

    # Scrapea en arxiv con la query insertada y verifica que haya resultados
    resultados = scrapear_arxiv(query)
    widget_arxiv.delete('1.0', tk.END)
    if not resultados:
        widget_arxiv.insert(tk.END, "No se han encontrado resultados para esta consulta.")
    # Introduce los datos obtenidos en el widget de texto
    else:
        for resultado in resultados:
            widget_arxiv.insert(tk.END, f"Titulo: {resultado['titulo']}\n\n")
            widget_arxiv.insert(tk.END, f"Autores: {resultado['autores']}\n\n")
            widget_arxiv.insert(tk.END, f"Resumen: {resultado['resumen']}\n\n")
            widget_arxiv.insert(tk.END, f"Fecha de publicacion: {resultado['fecha_publicacion']}\n\n")
            widget_arxiv.insert(tk.END, f"Categorias: {resultado['categorias']}\n\n")
            widget_arxiv.insert(tk.END, f"Comentarios: {resultado['comentarios']}\n\n")
            widget_arxiv.insert(tk.END, f"Referencia Journal: {resultado['referencia_journal']}\n\n")
            insertar_link(widget_arxiv, resultado['link'], resultado['link'], resultados.index(resultado))
            widget_arxiv.insert(tk.END, "\n\n")