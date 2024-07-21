import requests
from bs4 import BeautifulSoup
import csv

url = 'https://cis.ieee.org/publications/t-neural-networks-and-learning-systems/tnnls-editor-and-associate-editors'

try:
    # Realizar la solicitud GET a la p�gina
    response = requests.get(url)
    response.raise_for_status()  # Asegurarse de que la solicitud sea exitosa

    # Parsear el contenido HTML
    soup = BeautifulSoup(response.content, 'html.parser')

    # Obtener el nombre del journal
    journal_name = soup.find('h1').text.strip() if soup.find('h1') else 'Journal Name Not Found'

    # Lista para almacenar los datos
    data_list = []

    # Obtener el primer miembro especial
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

    # Buscar todos los roles (strong dentro de h2) y los contenedores asociados
    roles = soup.find_all('h2')
    for role in roles:
        if role == first_member:
            continue  # Saltar el primer miembro especial ya procesado
        role_text = role.find('strong').text.strip() if role.find('strong') else ''
        next_sibling = role.find_next()
        elements = []
        while next_sibling and next_sibling.name != 'h2':
            if next_sibling.name == 'p':
                elements.append(next_sibling)
            elif next_sibling.name == 'table':
                tbody = next_sibling.find('tbody')
                if tbody:
                    tr_elements = tbody.find_all('tr')[1:]  # Omitir el primer tr
                    for tr in tr_elements:
                        td_elements = tr.find_all('td')
                        if len(td_elements) >= 3:
                            name = td_elements[0].text.strip()
                            affiliation = td_elements[1].text.strip()
                            country = td_elements[2].text.strip()
                            data_list.append([role_text, name, affiliation, country, '', ''])
            next_sibling = next_sibling.find_next()

        if elements:
            for element in elements[:-1]:  # Omitir el �ltimo elemento
                spans = element.find_all('span')
                if len(spans) >= 4:
                    name = spans[0].text.strip()
                    affiliation1 = spans[1].text.strip()
                    affiliation2 = spans[2].text.strip()
                    country = spans[3].text.strip()
                    affiliation = f"{affiliation1}, {affiliation2}"
                    data_list.append([role_text, name, affiliation, country, '', ''])

    # Procesar los miembros con clase indvlistname y sus correspondientes roles en roletitle
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

    # Escribir los datos en un archivo CSV
    with open('tnnls_editorial_board_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Escribir el nombre del journal en la primera fila
        writer.writerow(['Journal Name'])
        writer.writerow([journal_name])
        # Escribir el encabezado
        writer.writerow(['Role', 'Name', 'Affiliation', 'Country', 'Email', 'Website'])
        # Escribir los dem�s datos
        writer.writerows(data_list)

    print(f"Se han guardado los datos en 'tnnls_editorial_board_data.csv'.")

except requests.exceptions.RequestException as e:
    print(f"Error al realizar la solicitud: {e}")
except Exception as e:
    print(f"Error inesperado: {e}")
