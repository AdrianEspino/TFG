import requests
from bs4 import BeautifulSoup
from tkinter import messagebox, filedialog
import tkinter as tk
import csv
import os    

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
        
def mostrar_TNNLS(widget_TNNLS):
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