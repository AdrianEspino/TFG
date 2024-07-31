import requests
from bs4 import BeautifulSoup
from tkinter import messagebox, filedialog
import tkinter as tk
import csv
import os

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
        
def mostrar_ACM(widget_ACM):
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