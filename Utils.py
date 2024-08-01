import requests
import tkinter as tk
from tkinter import messagebox
from io import BytesIO
from PIL import Image, ImageTk
import webbrowser
import os
import sys

def resource_path(path_relativo):
    '''
    Obtiene la ruta del recurso para ser utilizado en el entorno de PyInstaller o en el entorno de desarrollo.
    :param relative_path: str - Ruta relativa del recurso.
    :return: str - Ruta absoluta del recurso.
    '''
    try:
        # PyInstaller guarda recursos en un directorio temporal llamado _MEIPASS
        path_base = sys._MEIPASS
    except AttributeError:
        # En el entorno de desarrollo, usa la ruta del script actual
        path_base = os.path.dirname(__file__)
    return os.path.join(path_base, path_relativo)

           
def insertar_link(widget, url, texto, index):
    '''
    Inserta un link en un widget de texto de Tkinter.
    :param widget: tk.Text - El widget de texto en el que se insertar  el link.
    :param url: str - La URL del link.
    :param texto: str - El texto del link que se mostrar  en el widget de texto.
    :param index: int - El  ndice del link que se utiliza para crear un tag en el widget de texto.
    '''
    
    # Crear un nombre para el tag del enlace usando el  ndice proporcionado
    nombre_tag = f"link{index}"
    
    # Insertar el texto del link en el widget de texto con el nombre del tag creado
    widget.insert(tk.END, f"{texto} - {url}\n\n", nombre_tag)
    
    # Configurar el comportamiento del link: al hacer clic, abrir la URL en el navegador predeterminado
    widget.tag_bind(nombre_tag, "<Button-1>", lambda e, url=url: abrir_link(url))
    
    # Configurar el estilo del enlace: color de texto azul y subrayado
    widget.tag_config(nombre_tag, foreground="blue", underline=True)
    
    # Cambiar el cursor a una mano cuando el mouse est  sobre el enlace
    widget.tag_bind(nombre_tag, "<Enter>", lambda e: widget.config(cursor="hand2"))
    
    # Restaurar el cursor a la flecha normal cuando el mouse sale del enlace
    widget.tag_bind(nombre_tag, "<Leave>", lambda e: widget.config(cursor=""))


def insertar_imagen(widget, url, texto, index):
    '''
    Inserta una imagen en un widget de texto de Tkinter.
    :param widget: tk.Text - El widget de texto en el que se insertar  la imagen.
    :param url: str - La URL de la imagen.
    :param texto: str - El texto de la imagen que se mostrar  en el widget de texto.
    :param index: int - El  ndice de la imagen que se utiliza para crear un tag en el widget de texto.
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
    
    # Utiliza la funci n `open_new` de la libreria `webbrowser` para abrir la URL en una nueva ventana del navegador.
    webbrowser.open_new(url)


def mostrar_imagen(url):
    '''
    Muestra una imagen en una nueva ventana emergente.
    :param url: str - La URL de la imagen
    :return: None
    '''
    
    # Crea una nueva ventana emergente para mostrar la imagen.
    ventana = tk.Toplevel()
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
