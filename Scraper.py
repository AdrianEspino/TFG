import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import tkinter as tk
from tkinter import messagebox

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
    
def mostrar_datos(entrada_url,widget,insertar_link,insertar_imagen):
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