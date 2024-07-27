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


def mostrar_datos():
    '''  
    Esta función obtiene la URL del usuario, verifica que no esté vacía y realiza un scraping de la página web. Muestra los datos extraídos en un widget de texto.
    :param: None
    :return: None
    '''
    
    # Obtener la URL desde el campo de entrada
    url = entrada_url.get()
    
    # Comprobar si la URL está vacía
    if not url:
        # Mostrar una advertencia si la URL está vacía
        messagebox.showwarning("Input Error", "Por favor, inserte una URL valida")
        return
    
    # Llamar a la función scrapear_web para obtener los datos de la URL
    data = scrapear_web(url)
    
    # Verificar si el resultado de scrapear_web es un mensaje de error, es decir, un string
    if isinstance(data, str):
        # Borrar el contenido del widget de texto
        widget.delete('1.0', tk.END)
        # Insertar el mensaje de error en el widget de texto
        widget.insert(tk.END, data)
    else:
        # Borrar el contenido del widget de texto
        widget.delete('1.0', tk.END)
        # Insertar el título de la página en el widget de texto
        widget.insert(tk.END, f"Titulo: {data['titulo']}\n\n")
        
        # Insertar los párrafos de la página en el widget de texto
        widget.insert(tk.END, "Parrafos:\n")
        for p in data['parrafos']:
            widget.insert(tk.END, f"{p}\n\n")
        
        # Insertar los enlaces de la página en el widget de texto
        widget.insert(tk.END, "Links:\n")
        for index, link in enumerate(data['links']):
            insertar_link(widget, link['url'], link['text'], index)
        
        # Insertar las imágenes de la página en el widget de texto
        widget.insert(tk.END, "Imagenes:\n")
        for index, image in enumerate(data['imagenes']):
            insertar_imagen(widget, image['src'], image['alt'], index)


           
def insertar_link(widget, url, texto, index):
    '''
    Inserta un link en un widget de texto de Tkinter.
    :param widget: tk.Text - El widget de texto en el que se insertará el link.
    :param url: str - La URL del link.
    :param texto: str - El texto del link que se mostrará en el widget de texto.
    :param index: int - El índice del link que se utiliza para crear un tag en el widget de texto.
    '''
    
    # Crear un nombre para el tag del enlace usando el índice proporcionado
    nombre_tag = f"link{index}"
    
    # Insertar el texto del link en el widget de texto con el nombre del tag creado
    widget.insert(tk.END, f"{texto} - {url}\n\n", nombre_tag)
    
    # Configurar el comportamiento del link: al hacer clic, abrir la URL en el navegador predeterminado
    widget.tag_bind(nombre_tag, "<Button-1>", lambda e, url=url: abrir_link(url))
    
    # Configurar el estilo del enlace: color de texto azul y subrayado
    widget.tag_config(nombre_tag, foreground="blue", underline=True)
    
    # Cambiar el cursor a una mano cuando el mouse está sobre el enlace
    widget.tag_bind(nombre_tag, "<Enter>", lambda e: widget.config(cursor="hand2"))
    
    # Restaurar el cursor a la flecha normal cuando el mouse sale del enlace
    widget.tag_bind(nombre_tag, "<Leave>", lambda e: widget.config(cursor=""))


def insertar_imagen(widget, url, texto, index):
    '''
    Inserta una imagen en un widget de texto de Tkinter.
    :param widget: tk.Text - El widget de texto en el que se insertará la imagen.
    :param url: str - La URL de la imagen.
    :param texto: str - El texto de la imagen que se mostrará en el widget de texto.
    :param index: int - El índice de la imagen que se utiliza para crear un tag en el widget de texto.
    '''
    nombre_tag = f"image{index}"
    widget.insert(tk.END, f"{texto} - {url}\n\n", nombre_tag)
    widget.tag_bind(nombre_tag, "<Button-1>", lambda e, url=url: mostrar_imagen(url))
    widget.tag_config(nombre_tag, foreground="green", underline=True)
    widget.tag_bind(nombre_tag, "<Enter>", lambda e: widget.config(cursor="hand2"))
    widget.tag_bind(nombre_tag, "<Leave>", lambda e: widget.config(cursor=""))


def abrir_link(url):
    '''
    Abre la URL proporcionada en el navegador web predeterminado.
    :param url: str - La URL que se desea abrir
    :return: None
    '''
    
    # Utiliza la función `open_new` de la libreria `webbrowser` para abrir la URL en una nueva ventana del navegador.
    webbrowser.open_new(url)


def mostrar_imagen(url):
    '''
    Muestra una imagen en una nueva ventana emergente.
    :param url: str - La URL de la imagen
    :return: None
    '''
    
    # Crea una nueva ventana emergente para mostrar la imagen.
    ventana = tk.Toplevel(raiz)
    ventana.title("Imagen")

    try:
        # Realiza una solicitud HTTP para obtener los datos de la imagen.
        respuesta = requests.get(url, stream=True)
        # Verifica si la solicitud fue exitosa.
        respuesta.raise_for_status()
        # Obtiene los datos de la imagen en formato binario.
        img_data = respuesta.content
        
        # Abre la imagen desde los datos binarios.
        img = Image.open(BytesIO(img_data))
        # Convierte la imagen a un formato que Tkinter pueda mostrar.
        img_tk = ImageTk.PhotoImage(img)
        
        # Crea un widget de etiqueta en la nueva ventana y asigna la imagen a la etiqueta.
        img_label = tk.Label(ventana, image=img_tk)
        # Guarda una referencia a la imagen en el widget para evitar que sea recolectada por el recolector de basura.
        img_label.image = img_tk
        # Empaqueta el widget en la ventana emergente.
        img_label.pack()
    except requests.RequestException as e:
        # Muestra un mensaje de error si ocurre un problema al buscar la imagen.
        messagebox.showerror("Error", f"Error al buscar la imagen: {e}")
    except Exception as e:
        # Muestra un mensaje de error si ocurre un problema al mostrar la imagen.
        messagebox.showerror("Error", f"Error al mostrar la imagen: {e}")



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


def mostrar_arxiv():
    '''
    Esta función recoge la query insertada por el usuario y scrapea sobre ella en arxiv, mostrando los resultados en un widget de texto
    :param: None
    :return: None
    '''
    
    # Obtiene la query insertada por el usuario y verifica que no está vacía
    query = query_arxiv.get()
    if not query:
        messagebox.showwarning("Input Error", "Por favor, introduzca una consulta valida")
        return

    # Scrapea en arxiv con la query insertada y verifica que haya resultados
    resultados = scrapear_arxiv(query)
    widget_arxiv.delete('1.0', tk.END)
    if not resultados:
        widget.insert(tk.END, "No se han encontrado resultados para esta consulta.")
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


def mostrar_pubmed():
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

    # Scrapea en arxiv con la query insertada y verifica que haya resultados
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

def mostrar_ACM():
    '''
    Esta función muestra los resultados del scrapeo de ACM en un widget de texto.
    :param: None
    :return: None
    '''
    
    # Scrapea la página web de ACM y muestra los resultados en el widget de texto
    url = 'https://dl.acm.org/journal/jetc/editorial-board'
    try:
        journal_name, datos = scrapear_ACM(url)

        # Insertar los datos en el widget de texto
        widget_ACM.delete('1.0', tk.END)
        widget_ACM.insert(tk.END, f"Journal Name: {journal_name}\n\n")
        for data in datos:
            widget_ACM.insert(tk.END, f"Rol: {data[0]}\n")
            widget_ACM.insert(tk.END, f"Nombre: {data[1]}\n")
            widget_ACM.insert(tk.END, f"Afiliación: {data[2]}\n")
            widget_ACM.insert(tk.END, f"País: {data[3]}\n")
            widget_ACM.insert(tk.END, "\n")

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


def mostrar_TNNLS():
    '''
    Función que muestra los datos scrapeados de TNNLS en el widget de texto.
    :param: None
    :return: None
    '''
    
    # URL de la página web de TNNLS y scrapeo de datos
    url = 'https://cis.ieee.org/publications/t-neural-networks-and-learning-systems/tnnls-editor-and-associate-editors'
    
    try:
        journal_name, datos = scrapear_TNNLS(url)

    # Mostrar los datos scrapeados en el widget de texto  
        widget_TNNLS.delete('1.0', tk.END)
        widget_TNNLS.insert(tk.END, f"Journal Name: {journal_name}\n\n")
        for dato in datos:
            widget_TNNLS.insert(tk.END, f"Rol: {dato[0]}\n")
            widget_TNNLS.insert(tk.END, f"Nombre: {dato[1]}\n")
            widget_TNNLS.insert(tk.END, f"Afiliación: {dato[2]}\n")
            widget_TNNLS.insert(tk.END, f"País: {dato[3]}\n")
            widget_TNNLS.insert(tk.END, f"Email: {dato[4]}\n")
            widget_TNNLS.insert(tk.END, f"Web: {dato[5]}\n")
            widget_TNNLS.insert(tk.END, "\n")

    except Exception as e:
        messagebox.showerror("Error", str(e))
    
        
#Interfaz de la aplicación
def mostrar_frame(frame):
    '''
    Esta función muestra el frame que queramos, al elevarlo al primer plano
    :param frame: tk.Frame - Marco a mostrar
    :return: None
    '''
    frame.tkraise()


def iniciar_aplicacion():
    '''
    Inicia la aplicación despues de la pantalla de inicio, cerrando esta y mostrando la principal que estaba oculta en pantalla completa
    :return:None
    '''
    secundaria.destroy()
    raiz.deiconify()
    raiz.state('zoomed')

# Crear ventanas principal y secundaria        
raiz = tk.Tk()
raiz.title("Web Scraper")
raiz.geometry("1000x600")
raiz.withdraw()

secundaria = tk.Toplevel()
secundaria.title("Welcome")
secundaria.geometry("500x300")

secundaria.attributes("-fullscreen", True)

# Crear la pantalla de inicio
titulo_secundaria = tk.Label(secundaria, text="Welcome to the Web Scraper!", font=("Times New Roman", 18))
titulo_secundaria.pack(expand=True)

boton_inicio = tk.Button(secundaria, text="Inicio", command=iniciar_aplicacion, font=("Times New Roman", 14), bg="#3498DB", fg="white")
boton_inicio.pack()

# Crear un frame para la barra lateral
barra_lateral = tk.Frame(raiz, bg="#3498DB", width=200, height=600, relief="sunken", borderwidth=2)
barra_lateral.pack(expand=False, fill="y", side="left", anchor="nw")

# Crear un frame principal
principal = tk.Frame(raiz, bg="white", width=800, height=600)
principal.pack(expand=True, fill="both", side="right")

# Crear frames para cada sección
frames = {}
for opcion in ["Web Scraper", "Arxiv", "PubMed", "Editorial Board ACM", "Editorial Board TNNLS"]:
    frame = tk.Frame(principal, bg="white")
    frame.place(relwidth=1, relheight=1)
    frames[opcion] = frame

def añadir_a_barra_lateral(texto, nombre_frame):
    '''
    Esta función añade un botón a la barra lateral que al ser pulsado muestra el frame correspondiente
    :param texto: str - Texto del botón
    :param nombre_frame: str - Nombre del frame a mostrar
    :return: None
    '''
    boton = tk.Button(barra_lateral, text=texto, bg="#2980B9", fg="white", font=("Helvetica", 14), relief="flat",
                       command=lambda: mostrar_frame(frames[nombre_frame]))
    boton.pack(fill="x")

# Añadir botones a la barra lateral
añadir_a_barra_lateral("Web Scraper", "Web Scraper")
añadir_a_barra_lateral("Arxiv", "Arxiv")
añadir_a_barra_lateral("PubMed", "PubMed")
añadir_a_barra_lateral("Editorial Board ACM", "Editorial Board ACM")
añadir_a_barra_lateral("Editorial Board TNNLS", "Editorial Board TNNLS")

# Añadir contenido al frame de Web Scraper
frame_url = ttk.Frame(frames["Web Scraper"], padding="10")
frame_url.pack(side=tk.TOP, fill=tk.X)
ttk.Label(frame_url, text="Inserte URL:").pack(side=tk.LEFT)
entrada_url = ttk.Entry(frame_url, width=50)
entrada_url.pack(side=tk.LEFT, fill=tk.X, expand=True)
tk.Button(frame_url, text="Scrapear", command=mostrar_datos, bg='#3498DB', fg='white').pack(side=tk.LEFT)

widget = ScrolledText(frames["Web Scraper"], wrap=tk.WORD, width=100, height=30)
widget.pack(fill=tk.BOTH, expand=True)

# Añadir contenido al frame de Arxiv
arxiv_frame = ttk.Frame(frames["Arxiv"], padding="10")
arxiv_frame.pack(side=tk.TOP, fill=tk.X)
ttk.Label(arxiv_frame, text="Inserte Consulta Arxiv:").pack(side=tk.LEFT)
query_arxiv = ttk.Entry(arxiv_frame, width=50)
query_arxiv.pack(side=tk.LEFT, fill=tk.X, expand=True)
ttk.Button(arxiv_frame, text="Scrapear", command=mostrar_arxiv).pack(side=tk.LEFT)

widget_arxiv = ScrolledText(frames["Arxiv"], wrap=tk.WORD, width=100, height=30)
widget_arxiv.pack(fill=tk.BOTH, expand=True)

# Añadir contenido al frame de Pubmed
pubmed_frame = ttk.Frame(frames["PubMed"], padding="10")
pubmed_frame.pack(side=tk.TOP, fill=tk.X)
ttk.Label(pubmed_frame, text="Inserte Consulta Pubmed:").pack(side=tk.LEFT)
query_pubmed = ttk.Entry(pubmed_frame, width=50)
query_pubmed.pack(side=tk.LEFT, fill=tk.X, expand=True)
ttk.Button(pubmed_frame, text="Scrapear", command=mostrar_pubmed).pack(side=tk.LEFT)

widget_pubmed = ScrolledText(frames["PubMed"], wrap=tk.WORD, width=100, height=30)
widget_pubmed.pack(fill=tk.BOTH, expand=True)

# Añadir contenido al frame de ACM
frame_ACM = ttk.Frame(frames["Editorial Board ACM"], padding="10")
frame_ACM.pack(side=tk.TOP, fill=tk.X)
ttk.Button(frame_ACM, text="Descargar Editorial Board CSV", command=guardar_ACM_en_CSV).pack(side=tk.LEFT)
ttk.Button(frame_ACM, text="Ver Editorial Board", command=mostrar_ACM).pack(side=tk.LEFT)
link_ACM = tk.Label(frame_ACM, text="https://dl.acm.org/journal/jetc/editorial-board", fg="blue", cursor="hand2")
link_ACM.pack(side=tk.LEFT)
link_ACM.bind("<Button-1>", lambda e: abrir_link("https://dl.acm.org/journal/jetc/editorial-board"))

widget_ACM = ScrolledText(frames["Editorial Board ACM"], wrap=tk.WORD, width=100, height=30)
widget_ACM.pack(fill=tk.BOTH, expand=True)

# Añadir contenido al frame de TNNLS
frame_TNNLS = ttk.Frame(frames["Editorial Board TNNLS"], padding="10")
frame_TNNLS.pack(side=tk.TOP, fill=tk.X)

ttk.Button(frame_TNNLS, text="Descargar Editorial Board CSV", command=guardar_TNNLS_en_CSV).pack(side=tk.LEFT, padx=10)
ttk.Button(frame_TNNLS, text="Ver Editorial Board", command=mostrar_TNNLS).pack(side=tk.LEFT, padx=10)
link_TNNLS = tk.Label(frame_TNNLS, text="https://cis.ieee.org/publications/t-neural-networks-and-learning-systems/tnnls-editor-and-associate-editors", fg="blue", cursor="hand2")
link_TNNLS.pack(side=tk.LEFT, padx=10)
link_TNNLS.bind("<Button-1>", lambda e: abrir_link("https://cis.ieee.org/publications/t-neural-networks-and-learning-systems/tnnls-editor-and-associate-editors"))

widget_TNNLS = ScrolledText(frames["Editorial Board TNNLS"], wrap=tk.WORD, width=100, height=30)
widget_TNNLS.pack(fill=tk.BOTH, expand=True)

# Mostrar el frame de Web Scraper al iniciar
mostrar_frame(frames["Web Scraper"])

raiz.mainloop()