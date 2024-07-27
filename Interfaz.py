from turtle import width
import requests
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from io import BytesIO
from PIL import Image, ImageTk
import webbrowser
from Funciones import *

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
ttk.Label(frame_url, text="Inserte URL:", font=("Times New Roman", 10)).pack(side=tk.LEFT)
entrada_url = ttk.Entry(frame_url, width=50)
entrada_url.pack(side=tk.LEFT, fill=tk.X, expand=True)
tk.Button(frame_url, text="Scrapear", command=mostrar_datos, bg='#121DB8', fg='white', font=("Times New Roman", 10)).pack(side=tk.LEFT)

widget = ScrolledText(frames["Web Scraper"], wrap=tk.WORD, width=100, height=30)
widget.pack(fill=tk.BOTH, expand=True)

# Añadir contenido al frame de Arxiv
arxiv_frame = ttk.Frame(frames["Arxiv"], padding="10")
arxiv_frame.pack(side=tk.TOP, fill=tk.X)
ttk.Label(arxiv_frame, text="Inserte Consulta Arxiv:").pack(side=tk.LEFT)
query_arxiv = ttk.Entry(arxiv_frame, width=50)
query_arxiv.pack(side=tk.LEFT, fill=tk.X, expand=True)
tk.Button(arxiv_frame, text="Scrapear", command=mostrar_arxiv, bg='#3498DB', fg='black').pack(side=tk.LEFT)

widget_arxiv = ScrolledText(frames["Arxiv"], wrap=tk.WORD, width=100, height=30)
widget_arxiv.pack(fill=tk.BOTH, expand=True)

# Añadir contenido al frame de Pubmed
pubmed_frame = ttk.Frame(frames["PubMed"], padding="10")
pubmed_frame.pack(side=tk.TOP, fill=tk.X)
ttk.Label(pubmed_frame, text="Inserte Consulta Pubmed:").pack(side=tk.LEFT)
query_pubmed = ttk.Entry(pubmed_frame, width=50)
query_pubmed.pack(side=tk.LEFT, fill=tk.X, expand=True)
tk.Button(pubmed_frame, text="Scrapear", command=mostrar_pubmed, bg='#3498DB', fg='black').pack(side=tk.LEFT)

widget_pubmed = ScrolledText(frames["PubMed"], wrap=tk.WORD, width=100, height=30)
widget_pubmed.pack(fill=tk.BOTH, expand=True)

# Añadir contenido al frame de ACM
frame_ACM = ttk.Frame(frames["Editorial Board ACM"], padding="10")
frame_ACM.pack(side=tk.TOP, fill=tk.X)
tk.Button(frame_ACM, text="Descargar Editorial Board CSV", command=guardar_ACM_en_CSV, bg='#3498DB', fg='black').pack(side=tk.LEFT)
tk.Button(frame_ACM, text="Ver Editorial Board", command=mostrar_ACM, bg='#3498DB', fg='black').pack(side=tk.LEFT)
link_ACM = tk.Label(frame_ACM, text="https://dl.acm.org/journal/jetc/editorial-board", fg="blue", cursor="hand2")
link_ACM.pack(side=tk.LEFT)
link_ACM.bind("<Button-1>", lambda e: abrir_link("https://dl.acm.org/journal/jetc/editorial-board"))

widget_ACM = ScrolledText(frames["Editorial Board ACM"], wrap=tk.WORD, width=100, height=30)
widget_ACM.pack(fill=tk.BOTH, expand=True)

# Añadir contenido al frame de TNNLS
frame_TNNLS = ttk.Frame(frames["Editorial Board TNNLS"], padding="10")
frame_TNNLS.pack(side=tk.TOP, fill=tk.X)

tk.Button(frame_TNNLS, text="Descargar Editorial Board CSV", command=guardar_TNNLS_en_CSV, bg='#121DB8', fg='white', font=("Times New Roman", 14)).pack(side=tk.LEFT, padx=10)
tk.Button(frame_TNNLS, text="Ver Editorial Board", command=mostrar_TNNLS, bg='#121DB8', fg='white', font=("Times New Roman", 14)).pack(side=tk.LEFT, padx=10)
link_TNNLS = tk.Label(frame_TNNLS, text="https://cis.ieee.org/publications/t-neural-networks-and-learning-systems/tnnls-editor-and-associate-editors", fg="blue", cursor="hand2")
link_TNNLS.pack(side=tk.LEFT, padx=10)
link_TNNLS.bind("<Button-1>", lambda e: abrir_link("https://cis.ieee.org/publications/t-neural-networks-and-learning-systems/tnnls-editor-and-associate-editors"))

widget_TNNLS = ScrolledText(frames["Editorial Board TNNLS"], wrap=tk.WORD, width=100, height=30)
widget_TNNLS.pack(fill=tk.BOTH, expand=True)

# Mostrar el frame de Web Scraper al iniciar
mostrar_frame(frames["Web Scraper"])

raiz.mainloop()