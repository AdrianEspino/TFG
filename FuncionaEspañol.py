from turtle import title
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
    
    # Esta funcion toma una URL de cualquier web y devuelve un diccionario con el titulo,los parrafos, los enlaces y las imagenes encontrados en la web.
    # :param url: str - La URL de la página web a scrapear.
    # :return: dict - Un diccionario con los datos scrapeados.
    
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
      
    #Esta función obtiene la URL del usuario, verifica que no esté vacía y realiza un scraping de la página web. Muestra los datos extraídos en un widget de texto. 
    #:return: None
    
    # Obtener la URL desde el campo de entrada
    url = url_entry.get()
    
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
    #Inserta un link en un widget de texto de Tkinter.
    #:param widget: tk.Text - El widget de texto en el que se insertará el link.
    #:param url: str - La URL del link.
    #:param texto: str - El texto del link que se mostrará en el widget de texto.
    #:param index: int - El índice del link que se utiliza para crear un tag en el widget de texto.
    
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


# Función igual que la anterior pero con imágenes
def insertar_imagen(widget, url, texto, index):
    nombre_tag = f"image{index}"
    widget.insert(tk.END, f"{texto} - {url}\n\n", nombre_tag)
    widget.tag_bind(nombre_tag, "<Button-1>", lambda e, url=url: mostrar_imagen(url))
    widget.tag_config(nombre_tag, foreground="green", underline=True)
    widget.tag_bind(nombre_tag, "<Enter>", lambda e: widget.config(cursor="hand2"))
    widget.tag_bind(nombre_tag, "<Leave>", lambda e: widget.config(cursor=""))


def abrir_link(url):
    #Abre la URL proporcionada en el navegador web predeterminado.
    #:param url: str - La URL que se desea abrir.
    
    # Utiliza la función `open_new` de la libreria `webbrowser` para abrir la URL en una nueva ventana del navegador.
    webbrowser.open_new(url)


def mostrar_imagen(url):
    #Muestra una imagen en una nueva ventana emergente.
    #:param url: str - La URL de la imagen.
    
    # Crea una nueva ventana emergente para mostrar la imagen.
    ventana = tk.Toplevel(root)
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
    # Busca artículos en arXiv utilizando una consulta y devuelve una lista de resultados.
    # :param query: str - La consulta de búsqueda para encontrar artículos en arXiv.
    # :return: list - Una lista de diccionarios, cada uno representando un artículo con su título, resumen y enlace.
    
    # URL para la API de arXiv.
    url_arxiv = "http://export.arxiv.org/api/query?"
    #URL para hacer la busqueda
    url_busqueda = f"{url_arxiv}search_query=all:{query}&start=0"
    # Realiza una solicitud HTTP a la URL de búsqueda.
    respuesta = requests.get(url_busqueda)
    # Analiza la respuesta XML usando feedparser.
    feed = feedparser.parse(respuesta.content)
    # Inicializa una lista para almacenar los resultados de búsqueda.
    resultados = []
    # Itera sobre cada entrada en el feed creando un diccionario para almacenar información del artículo.
    for entry in feed.entries:
        resultado = {
            'titulo': entry.title,
            'resumen': entry.summary,
            'link': entry.link
        }
        resultados.append(resultado)
    return resultados


def scrapear_pubmed(query):
    # Busca artículos en pubmed utilizando una consulta y devuelve una lista de resultados.
    # :param query: str - La consulta de búsqueda para encontrar artículos en arXiv.
    # :return: list - Una lista de diccionarios, cada uno representando un artículo con su título, resumen y enlace.
    url_pubmed = "https://pubmed.ncbi.nlm.nih.gov/"
    url_busqueda = f"{url_pubmed}?term={query}"
    respuesta = requests.get(url_busqueda)
    soup = BeautifulSoup(respuesta.text, 'html.parser')
    articulos = soup.find_all('article', class_='full-docsum')
    resultados = []
    for articulo in articulos:
        titulo = articulo.find('a', class_='docsum-title').text.strip()
        link = urljoin(url_pubmed, articulo.find('a', class_='docsum-title')['href'])
        resumen = articulo.find('div', class_='full-view-snippet').text.strip() if articulo.find('div', class_='full-view-snippet') else "No hay resumen disponible"
        resultados.append({'titulo': titulo, 'resumen': resumen, 'link': link})
    return resultados


def fetch_arxiv_data():
    query = arxiv_entry.get()
    if not query:
        messagebox.showwarning("Input Error", "Please enter a search query")
        return

    results = scrapear_arxiv(query)
    arxiv_result_text.delete('1.0', tk.END)
    if not results:
        arxiv_result_text.insert(tk.END, "No results found for the query.")
    else:
        for result in results:
            arxiv_result_text.insert(tk.END, f"Titulo: {result['titulo']}\n\n")
            arxiv_result_text.insert(tk.END, f"Resumen: {result['resumen']}\n\n")
            insertar_link(arxiv_result_text, result['link'], result['link'], results.index(result))
            arxiv_result_text.insert(tk.END, "\n\n")


def fetch_pubmed_data():
    query = pubmed_entry.get()
    if not query:
        messagebox.showwarning("Input Error", "Please enter a search query")
        return

    results = scrapear_pubmed(query)
    pubmed_result_text.delete('1.0', tk.END)
    if not results:
        pubmed_result_text.insert(tk.END, "No results found for the query.")
    else:
        for result in results:
            pubmed_result_text.insert(tk.END, f"Titulo: {result['titulo']}\n\n")
            pubmed_result_text.insert(tk.END, f"Resumen: {result['resumen']}\n\n")
            insertar_link(pubmed_result_text, result['link'], result['link'], results.index(result))
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


#Interfaz de la aplicación
root = tk.Tk()
root.title("Web Scraper Application")
root.geometry("1000x600")
root.withdraw()

splash = tk.Toplevel()
splash.title("Welcome")
splash.geometry("500x300")

# Make the splash screen fullscreen
splash.attributes("-fullscreen", True)

splash_label = tk.Label(splash, text="Welcome to the Web Scraper!", font=("Helvetica", 18))
splash_label.pack(expand=True)

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
for option in ["Web Scraper", "Arxiv", "PubMed", "Editorial Board ACM", "Editorial Board TNNLS"]:
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
add_sidebar_button("Editorial Board ACM", "Editorial Board ACM")
add_sidebar_button("Editorial Board TNNLS", "Editorial Board TNNLS")

# Add content to the Web Scraper frame
url_frame = ttk.Frame(frames["Web Scraper"], padding="10")
url_frame.pack(side=tk.TOP, fill=tk.X)
ttk.Label(url_frame, text="Enter URL:").pack(side=tk.LEFT)
url_entry = ttk.Entry(url_frame, width=50)
url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
ttk.Button(url_frame, text="Scrape", command=mostrar_datos).pack(side=tk.LEFT)

widget = ScrolledText(frames["Web Scraper"], wrap=tk.WORD, width=100, height=30)
widget.pack(fill=tk.BOTH, expand=True)

# Add content to the Arxiv frame
arxiv_frame = ttk.Frame(frames["Arxiv"], padding="10")
arxiv_frame.pack(side=tk.TOP, fill=tk.X)
ttk.Label(arxiv_frame, text="Enter Arxiv Query:").pack(side=tk.LEFT)
arxiv_entry = ttk.Entry(arxiv_frame, width=50)
arxiv_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
ttk.Button(arxiv_frame, text="Search", command=fetch_arxiv_data).pack(side=tk.LEFT)

arxiv_result_text = ScrolledText(frames["Arxiv"], wrap=tk.WORD, width=100, height=30)
arxiv_result_text.pack(fill=tk.BOTH, expand=True)

# Add content to the PubMed frame
pubmed_frame = ttk.Frame(frames["PubMed"], padding="10")
pubmed_frame.pack(side=tk.TOP, fill=tk.X)
ttk.Label(pubmed_frame, text="Enter PubMed Query:").pack(side=tk.LEFT)
pubmed_entry = ttk.Entry(pubmed_frame, width=50)
pubmed_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
ttk.Button(pubmed_frame, text="Search", command=fetch_pubmed_data).pack(side=tk.LEFT)

pubmed_result_text = ScrolledText(frames["PubMed"], wrap=tk.WORD, width=100, height=30)
pubmed_result_text.pack(fill=tk.BOTH, expand=True)

# Add content to the Editorial Board frame
editorial_frame = ttk.Frame(frames["Editorial Board ACM"], padding="10")
editorial_frame.pack(side=tk.TOP, fill=tk.X)
ttk.Button(editorial_frame, text="Download Editorial Board CSV", command=fetch_editorial_board_data).pack(side=tk.LEFT)
ttk.Button(editorial_frame, text="Show Editorial Board Data", command=show_editorial_board_data).pack(side=tk.LEFT)
editorial_link = tk.Label(editorial_frame, text="https://dl.acm.org/journal/jetc/editorial-board", fg="blue", cursor="hand2")
editorial_link.pack(side=tk.LEFT)
editorial_link.bind("<Button-1>", lambda e: abrir_link("https://dl.acm.org/journal/jetc/editorial-board"))

editorial_result_text = ScrolledText(frames["Editorial Board ACM"], wrap=tk.WORD, width=100, height=30)
editorial_result_text.pack(fill=tk.BOTH, expand=True)

# Add content to the Editorial Board TNNLS frame
editorial_tnnls_frame = ttk.Frame(frames["Editorial Board TNNLS"], padding="10")
editorial_tnnls_frame.pack(side=tk.TOP, fill=tk.X)

ttk.Button(editorial_tnnls_frame, text="Download Editorial Board CSV", command=fetch_editorial_board_data_TNNLS).pack(side=tk.LEFT, padx=10)
ttk.Button(editorial_tnnls_frame, text="Show Editorial Board Data", command=show_editorial_board_data_TNNLS).pack(side=tk.LEFT, padx=10)
editorial_tnnls_link = tk.Label(editorial_tnnls_frame, text="https://cis.ieee.org/publications/t-neural-networks-and-learning-systems/tnnls-editor-and-associate-editors", fg="blue", cursor="hand2")
editorial_tnnls_link.pack(side=tk.LEFT, padx=10)
editorial_tnnls_link.bind("<Button-1>", lambda e: abrir_link("https://cis.ieee.org/publications/t-neural-networks-and-learning-systems/tnnls-editor-and-associate-editors"))

editorial_tnnls_result_text = ScrolledText(frames["Editorial Board TNNLS"], wrap=tk.WORD, width=100, height=30)
editorial_tnnls_result_text.pack(fill=tk.BOTH, expand=True)

# Initially show the Web Scraper frame
show_frame(frames["Web Scraper"])

root.mainloop()