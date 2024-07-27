import requests
from bs4 import BeautifulSoup
from tkinter import messagebox, filedialog
from urllib.parse import urljoin
import feedparser
import csv
import os

def scrapear_web(url):
    '''
    Esta funcion toma una URL de cualquier web y devuelve un diccionario con el titulo,los parrafos, los enlaces y las imagenes encontrados en la web.
    :param url: str - La URL de la página web a scrapear.
    :return: dict - Un diccionario con los datos scrapeados.
    '''
    try:
        # Realizar la solicitud HTTP con un tiempo de espera
        respuesta = requests.get(url, timeout=10)
        respuesta.raise_for_status()  # Lanza una excepción si la respuesta no es exitosa

        # Analizar el contenido HTML de la respuesta
        soup = BeautifulSoup(respuesta.text, 'html.parser')

        # Extraer el título de la página
        titulo = soup.title.string if soup.title else 'No se ha encontrado titulo'

        # Extraer todos los párrafos
        parrafos = [p.text for p in soup.find_all('p')]

        # Extraer todos los enlaces con texto y URL completa
        links = [{'text': a.get_text(), 'url': urljoin(url, a['href'])} for a in soup.find_all('a', href=True)]

        # Extraer todas las imágenes con alt y URL completa
        imagenes = [{'alt': img.get('alt', ''), 'src': urljoin(url, img['src'])} for img in soup.find_all('img', src=True)]

        return {
            'titulo': titulo,
            'parrafos': parrafos,
            'links': links,
            'imagenes': imagenes
        }
    
    except requests.ConnectionError:
        return "Error: No se pudo conectar con el servidor."
    except requests.Timeout:
        return "Error: La solicitud ha tardado demasiado en completarse."
    except requests.RequestException as e:
        return f"Error: {e}"

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


def scrapear_pubmed(query):
    '''
    Busca artículos en pubmed utilizando una consulta y devuelve una lista de resultados.
    :param query: str - La consulta de búsqueda para encontrar artículos en arXiv.
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

def scrapear_ACM(url):
    '''
    Esta función scrapea la página web de ACM para obtener la lista de miembros del editorial board.
    :param url: str - La URL de la página web de ACM.
    :return:
    '''
    
    #Solicitud HTTP y análisis de respuesta con BeautifulSoup
    try:
        respuesta = requests.get(url)
        respuesta.raise_for_status()
        soup = BeautifulSoup(respuesta.content, 'html.parser')
        
        # Extracción de la información de los miembros del editorial board
        journal_name = soup.find('h1', class_='title').text.strip() if soup.find('h1', class_='title') else 'Nombre de la revista no encontrado'
        datos = []
        roles = soup.find_all('h3', class_='section__title')
        for rol in roles:
            texto_rol = rol.text.strip()
            siguiente_hijo = rol.find_next()
            while siguiente_hijo and siguiente_hijo.name != 'h3':
                if 'item-meta__info' in siguiente_hijo.get('class', []):
                    nombre = siguiente_hijo.find('h4').text.strip() if siguiente_hijo.find('h4') else ''
                    afiliacion = siguiente_hijo.find('p').text.strip() if siguiente_hijo.find('p') else ''
                    pais = siguiente_hijo.find('span').text.strip() if siguiente_hijo.find('span') else ''
                    datos.append([texto_rol, nombre, afiliacion, pais])
                siguiente_hijo = siguiente_hijo.find_next()
        return journal_name, datos
    except requests.exceptions.RequestException as e:
        raise Exception(f"Fallo al scrapear los datos del editorial board. Error: {e}")

def guardar_ACM_en_CSV():
    '''
    Esta función scrapea la página web de ACM y guarda sus datos en un CSV.
    :param: None
    :return: tuple - Contiene el nombre de la revista y una lista de miembros del editorial board.
    '''

    # URL de ACM y scrapeo de datos
    url = 'https://dl.acm.org/journal/jetc/editorial-board'
    try:
        journal_name, datos = scrapear_ACM(url)
        
        # Guarda los datos scrapeados en un CSV, cuyo PATH se pide al usuario
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if path:
            with open(path, 'w', newline='', encoding='utf-8-sig') as csvfile:  # Añadir -sig para incluir el BOM
                writer = csv.writer(csvfile)
                writer.writerow(['Journal Name'])
                writer.writerow([journal_name])
                writer.writerow(['Rol', 'Nombre', 'Afiliación', 'País'])
                writer.writerows(datos)

            messagebox.showinfo("Éxito", f"Los datos del editorial board han sido guardados en: '{os.path.basename(path)}'.")

    except Exception as e:
        messagebox.showerror("Error", str(e))
        

def scrapear_TNNLS(url):
    '''
    Esta función scrapea la página web de TNNLS para obtener la lista de miembros del editorial board.
    :param url: str - La URL de la página web de TNNLS.
    :return: tuple - Contiene el nombre de la revista y una lista de miembros del editorial board.
    '''
    
    #Solicitud HTTP y análisis de respuesta con BeautifulSoup
    try:
        respuesta = requests.get(url)
        respuesta.raise_for_status()
        soup = BeautifulSoup(respuesta.content, 'html.parser')

    # Extracción de título y primer miembro  
        journal_name = soup.find('h1').text.strip() if soup.find('h1') else 'Journal Name no encontrado'
        datos = []

        primer_miembro = soup.find('h2', style=True)
        if primer_miembro:
            texto_rol = primer_miembro.text.strip()
            tag = primer_miembro.find_next('p', style=True)
            if tag:
                strong_tag = tag.find('strong')
                nombre = strong_tag.text.strip() if strong_tag else ''
                br_tags = tag.find_all('br')
                if len(br_tags) >= 4:
                    afiliacion1 = br_tags[0].next_sibling.strip() if br_tags[0].next_sibling else ''
                    afiliacion2 = br_tags[1].next_sibling.strip() if br_tags[1].next_sibling else ''
                    pais = br_tags[2].next_sibling.strip() if br_tags[2].next_sibling else ''
                    email = br_tags[3].next_sibling.strip() if br_tags[3].next_sibling else ''
                    afiliacion = f"{afiliacion1}, {afiliacion2}"
                    datos.append([texto_rol, nombre, afiliacion, pais, email, ''])
        
        # Extracción de siguientes miembros            
        roles = soup.find_all('h2')
        for rol in roles:
            if rol == primer_miembro:
                continue
            texto_rol = rol.find('strong').text.strip() if rol.find('strong') else ''
            siguiente_hijo = rol.find_next()
            elementos = []
            while siguiente_hijo and siguiente_hijo.name != 'h2':
                if siguiente_hijo.name == 'p':
                    elementos.append(siguiente_hijo)
                elif siguiente_hijo.name == 'table':
                    tbody = siguiente_hijo.find('tbody')
                    if tbody:
                        elementos_tr = tbody.find_all('tr')[1:]
                        for tr in elementos_tr:
                            elementos_td = tr.find_all('td')
                            if len(elementos_td) >= 3:
                                nombre = elementos_td[0].text.strip()
                                afiliacion = elementos_td[1].text.strip()
                                pais = elementos_td[2].text.strip()
                                datos.append([texto_rol, nombre, afiliacion, pais, '', ''])
                siguiente_hijo = siguiente_hijo.find_next()

            if elementos:
                for elemento in elementos[:-1]:
                    spans = elemento.find_all('span')
                    if len(spans) >= 4:
                        nombre = spans[0].text.strip()
                        afiliacion1 = spans[1].text.strip()
                        afiliacion2 = spans[2].text.strip()
                        pais = spans[3].text.strip()
                        afiliacion = f"{afiliacion1}, {afiliacion2}"
                        datos.append([texto_rol, nombre, afiliacion, pais, '', ''])

        # Extracción de los últimos miembros del editorial board               
        roles = soup.find_all('h3', class_='roletitle')
        for rol in roles:
            texto_rol = rol.text.strip()
            siguiente_hijo = rol.find_next()
            while siguiente_hijo and siguiente_hijo.name != 'h3':
                if siguiente_hijo.name == 'div' and 'indvlistname' in siguiente_hijo.get('class', []):
                    nombre = siguiente_hijo.text.strip()
                    div_afiliacion = siguiente_hijo.find_next('div', class_='indvlistaffil')
                    if div_afiliacion:
                        partes_afiliacion = div_afiliacion.text.strip().split(',')
                        afiliacion = ', '.join(part.strip() for part in partes_afiliacion)
                    else:
                        afiliacion = ''
                    div_pais = siguiente_hijo.find_next('div', class_='indvfulllistaddr')
                    pais = div_pais.text.strip() if div_pais else ''
                    div_email = siguiente_hijo.find_next('div', class_='indvlistemail')
                    email = div_email.text.strip() if div_email else ''
                    div_web = siguiente_hijo.find_next('div', class_='indvlistwebsite')
                    web = div_web.text.strip() if div_web else ''
                    datos.append([texto_rol, nombre, afiliacion, pais, email, web])
                siguiente_hijo = siguiente_hijo.find_next()

        return journal_name, datos

    except requests.exceptions.RequestException as e:
        raise Exception(f"Fallo al scrapear los datos del editorial board. Error: {e}")
    except Exception as e:
        raise Exception(f"Error inesperado: {e}")


def guardar_TNNLS_en_CSV():
    '''
    Esta función scrapea la página web de TNNLS y guarda sus datos en un CSV.
    :param: None
    :return: None
    '''
    
    # URL de la página web de TNNLS y scrapeo de datos
    url = 'https://cis.ieee.org/publications/t-neural-networks-and-learning-systems/tnnls-editor-and-associate-editors'
    try:
        journal_name, datos = scrapear_TNNLS(url)
        
        # Guarda los datos scrapeados en un CSV, cuyo PATH se pide al usuario
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if path:
            with open(path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Journal Name'])
                writer.writerow([journal_name])
                writer.writerow(['Rol', 'Nombre', 'Afiliación', 'Pais', 'Email', 'Web'])
                writer.writerows(datos)

            messagebox.showinfo("Éxito", f"Los datos del editorial board han sido guardados en: '{os.path.basename(path)}'.")

    except Exception as e:
        messagebox.showerror("Error", str(e))