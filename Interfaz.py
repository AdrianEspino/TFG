import requests
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from io import BytesIO
from PIL import Image, ImageTk
import webbrowser
import os
import sys
from Arxiv import *
from Pubmed import *
from Scraper import *
from Scraper_ACM import *
from Scraper_TNNLS import *
from Utils import *


def scraper_handler():
    mostrar_datos(entrada_url, widget, insertar_link, insertar_imagen)

def arxiv_handler():
    mostrar_arxiv(query_arxiv, widget_arxiv, insertar_link)
        
def pubmed_handler():
    mostrar_pubmed(query_pubmed, widget_pubmed, insertar_link)
            
def ACM_handler():
    mostrar_ACM(widget_ACM)

def TNNLS_handler():
    mostrar_TNNLS(widget_TNNLS)
    
        
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

# Cargar el logo
try:
    path_logo = resource_path("logo.png")
    logo_img = Image.open(path_logo)
except Exception as e:
    print(f"No se pudo cargar el logo: {e}")

# Establecer el color de fondo para la pantalla de inicio
color_fondo = "#87CEFA"
secundaria.configure(bg=color_fondo)

# Crear un frame para centrar el contenido
frame_central = tk.Frame(secundaria, bg=color_fondo)
frame_central.place(relx=0.5, rely=0.5, anchor="center")

# Cargar la imagen para la pantalla de inicio
logo_inicio = Image.open(path_logo)
logo_inicio = logo_inicio.resize((300, 300))
foto_inicio = ImageTk.PhotoImage(logo_inicio)

# Crear la pantalla de inicio
label_imagen_inicio = tk.Label(frame_central, image=foto_inicio, bg=color_fondo)
label_imagen_inicio.image = foto_inicio
label_imagen_inicio.pack(pady=(0, 10))

titulo_secundaria = tk.Label(frame_central, text="ScienceScraper", font=("Times New Roman", 30, "bold", "italic"),  bg=color_fondo)
titulo_secundaria.pack(pady=(10, 50))

boton_inicio = tk.Button(frame_central, text="Inicio", command=iniciar_aplicacion, bg='#121DB8', fg='white', font=("Times New Roman", 20))
boton_inicio.pack(pady=20)

# Crear un frame para la barra lateral
barra_lateral = tk.Frame(raiz, bg="#87CEFA", width=200, height=600, relief="sunken", borderwidth=2)
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
tk.Button(frame_url, text="Scrapear", command=scraper_handler, bg='#121DB8', fg='white', font=("Times New Roman", 10)).pack(side=tk.LEFT)

widget = ScrolledText(frames["Web Scraper"], wrap=tk.WORD, width=100, height=30)
widget.pack(fill=tk.BOTH, expand=True)

# Añadir contenido al frame de Arxiv
arxiv_frame = ttk.Frame(frames["Arxiv"], padding="10")
arxiv_frame.pack(side=tk.TOP, fill=tk.X)
ttk.Label(arxiv_frame, text="Inserte Consulta Arxiv:").pack(side=tk.LEFT)
query_arxiv = ttk.Entry(arxiv_frame, width=50)
query_arxiv.pack(side=tk.LEFT, fill=tk.X, expand=True)
tk.Button(arxiv_frame, text="Scrapear", command=arxiv_handler, bg='#121DB8', fg='white', font=("Times New Roman", 10)).pack(side=tk.LEFT)

widget_arxiv = ScrolledText(frames["Arxiv"], wrap=tk.WORD, width=100, height=30)
widget_arxiv.pack(fill=tk.BOTH, expand=True)

# Añadir contenido al frame de Pubmed
pubmed_frame = ttk.Frame(frames["PubMed"], padding="10")
pubmed_frame.pack(side=tk.TOP, fill=tk.X)
ttk.Label(pubmed_frame, text="Inserte Consulta Pubmed:").pack(side=tk.LEFT)
query_pubmed = ttk.Entry(pubmed_frame, width=50)
query_pubmed.pack(side=tk.LEFT, fill=tk.X, expand=True)
tk.Button(pubmed_frame, text="Scrapear", command=pubmed_handler, bg='#121DB8', fg='white', font=("Times New Roman", 10)).pack(side=tk.LEFT)

widget_pubmed = ScrolledText(frames["PubMed"], wrap=tk.WORD, width=100, height=30)
widget_pubmed.pack(fill=tk.BOTH, expand=True)

# Añadir contenido al frame de ACM
frame_ACM = ttk.Frame(frames["Editorial Board ACM"], padding="10")
frame_ACM.pack(side=tk.TOP, fill=tk.X)
tk.Button(frame_ACM, text="Descargar Editorial Board CSV", command=guardar_ACM_en_CSV, bg='#121DB8', fg='white', font=("Times New Roman", 14)).pack(side=tk.LEFT, padx=10)
tk.Button(frame_ACM, text="Ver Editorial Board", command=ACM_handler, bg='#121DB8', fg='white', font=("Times New Roman", 14)).pack(side=tk.LEFT, padx=10)
link_ACM = tk.Label(frame_ACM, text="https://dl.acm.org/journal/jetc/editorial-board", fg="blue", cursor="hand2")
link_ACM.pack(side=tk.LEFT)
link_ACM.bind("<Button-1>", lambda e: abrir_link("https://dl.acm.org/journal/jetc/editorial-board"))

widget_ACM = ScrolledText(frames["Editorial Board ACM"], wrap=tk.WORD, width=100, height=30)
widget_ACM.pack(fill=tk.BOTH, expand=True)

# Añadir contenido al frame de TNNLS
frame_TNNLS = ttk.Frame(frames["Editorial Board TNNLS"], padding="10")
frame_TNNLS.pack(side=tk.TOP, fill=tk.X)

tk.Button(frame_TNNLS, text="Descargar Editorial Board CSV", command=guardar_TNNLS_en_CSV, bg='#121DB8', fg='white', font=("Times New Roman", 14)).pack(side=tk.LEFT, padx=10)
tk.Button(frame_TNNLS, text="Ver Editorial Board", command=TNNLS_handler, bg='#121DB8', fg='white', font=("Times New Roman", 14)).pack(side=tk.LEFT, padx=10)
link_TNNLS = tk.Label(frame_TNNLS, text="https://cis.ieee.org/publications/t-neural-networks-and-learning-systems/tnnls-editor-and-associate-editors", fg="blue", cursor="hand2")
link_TNNLS.pack(side=tk.LEFT, padx=10)
link_TNNLS.bind("<Button-1>", lambda e: abrir_link("https://cis.ieee.org/publications/t-neural-networks-and-learning-systems/tnnls-editor-and-associate-editors"))

widget_TNNLS = ScrolledText(frames["Editorial Board TNNLS"], wrap=tk.WORD, width=100, height=30)
widget_TNNLS.pack(fill=tk.BOTH, expand=True)

# Mostrar el frame de Web Scraper al iniciar
mostrar_frame(frames["Web Scraper"])

# Cargar y añadir el logo a la barra lateral
logo = Image.open(path_logo)
logo = logo.resize((100, 100))
photo = ImageTk.PhotoImage(logo)

label_logo = tk.Label(barra_lateral, image=photo, bg="#87CEFA")
label_logo.image = photo
label_logo.pack(side="bottom", pady=20)

raiz.mainloop()