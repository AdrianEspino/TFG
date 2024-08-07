import requests
from bs4 import BeautifulSoup
from tkinter import messagebox
from urllib.parse import urljoin
import tkinter as tk

def scrapear_pubmed(query):
    '''
    Busca artículos en pubmed utilizando una consulta y devuelve una lista de resultados.
    :param query: str - La consulta de búsqueda para encontrar artículos en pubmed.
    :return: list - Una lista de diccionarios, cada uno representando un artículo con su título, resumen y enlace.
    '''
    
    #URLs de pubmed y la de consulta del usuario
    url_pubmed = "https://pubmed.ncbi.nlm.nih.gov/"
    url_busqueda = f"{url_pubmed}?term={query}"
    #Solicitud HTTP y análisis de respuesta con BeautifulSoup
    respuesta = requests.get(url_busqueda)
    soup = BeautifulSoup(respuesta.text, 'html.parser')
    articulos = soup.find_all('article', class_='full-docsum')
    #Iteración sobre los artículos encontrados y creación de diccionario
    resultados = []
    for articulo in articulos:
        titulo = articulo.find('a', class_='docsum-title').text.strip()
        autores = articulo.find('span', class_='docsum-authors full-authors').text.strip() if articulo.find('span', class_='docsum-authors full-authors') else "No hay autores disponibles"
        link = urljoin(url_pubmed, articulo.find('a', class_='docsum-title')['href'])
        resumen = articulo.find('div', class_='full-view-snippet').text.strip() if articulo.find('div', class_='full-view-snippet') else "No hay resumen disponible"
        resultados.append({'titulo': titulo, 'autores': autores, 'resumen': resumen, 'link': link})
    return resultados

def mostrar_pubmed(query_pubmed,widget_pubmed,insertar_link):
    '''
    Esta función recoge la query insertada por el usuario y scrapea sobre ella en pubmed, mostrando los resultados en un widget de texto
    :param: None
    :return: None
    '''
    
    # Obtiene la query insertada por el usuario y verifica que no está vacía
    query = query_pubmed.get()
    if not query:
        messagebox.showwarning("Input Error", "Por favor, introduzca una consulta valida")
        return

    # Scrapea en pubmed con la query insertada y verifica que haya resultados
    results = scrapear_pubmed(query)
    widget_pubmed.delete('1.0', tk.END)
    if not results:
        widget_pubmed.insert(tk.END, "No se han encontrado resultados para esta consulta.")
    # Introduce los datos obtenidos en el widget de texto
    else:
        for result in results:
            widget_pubmed.insert(tk.END, f"Titulo: {result['titulo']}\n\n")
            widget_pubmed.insert(tk.END, f"Autores: {result['autores']}\n\n")
            widget_pubmed.insert(tk.END, f"Resumen: {result['resumen']}\n\n")
            insertar_link(widget_pubmed, result['link'], result['link'], results.index(result))
            widget_pubmed.insert(tk.END, "\n\n")
