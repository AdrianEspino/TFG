import requests
from bs4 import BeautifulSoup
import csv

url = 'https://dl.acm.org/journal/jetc/editorial-board'

try:
    # Realizar la solicitud GET a la página
    response = requests.get(url)
    response.raise_for_status()  # Asegurarse de que la solicitud sea exitosa

    # Parsear el contenido HTML
    soup = BeautifulSoup(response.content, 'html.parser')

    # Obtener el nombre del journal
    journal_name = soup.find('h1', class_='title').text.strip() if soup.find('h1', class_='title') else 'Journal Name Not Found'

    # Lista para almacenar los datos
    data_list = []

    # Buscar todos los roles (h3) y los contenedores asociados
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

    # Escribir los datos en un archivo CSV
    with open('editorial_board_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Escribir el nombre del journal en la primera fila
        writer.writerow(['Journal Name'])
        writer.writerow([journal_name])
        # Escribir el encabezado
        writer.writerow(['Role', 'Name', 'Affiliation', 'Country'])
        # Escribir los demás datos
        writer.writerows(data_list)

    print(f"Se han guardado los datos en 'editorial_board_data.csv'.")

except requests.exceptions.RequestException as e:
    print(f"Error al realizar la solicitud: {e}")
except Exception as e:
    print(f"Error inesperado: {e}")
