import sqlite3
import requests
from bs4 import BeautifulSoup

# Database setup
def setup_database():
    conn = sqlite3.connect('pokemon.db')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS pokemon (
        id INTEGER PRIMARY KEY,
        name TEXT,
        generation TEXT,
        primary_type TEXT,
        secondary_type TEXT,
        image_url TEXT
    )
    ''')
    conn.commit()
    conn.close()

def insert_pokemon(name, generation, primary_type, secondary_type, image_url):
    conn = sqlite3.connect('pokemon.db')
    c = conn.cursor()
    c.execute('''
    INSERT INTO pokemon (name, generation, primary_type, secondary_type, image_url)
    VALUES (?, ?, ?, ?, ?)
    ''', (name, generation, primary_type, secondary_type, image_url))
    conn.commit()
    conn.close()

setup_database()

url = 'https://pokemondb.net/pokedex/national'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Generations of the pokemon
generation_limits = [151, 251, 386, 493, 649, 721, 809, 905, 1025]
generations = ["Gen 1/Kanto", "Gen 2/Johto", "Gen 3/Hoenn", "Gen 4/Sinnoh", "Gen 5/Unova", "Gen 6/Kalos", "Gen 7/Alola", "Gen 8/Galar", "Gen 9/Paldea"]

all_pokemon = soup.find_all('div', class_='infocard')[0:1025]

for pokemon in all_pokemon:
    name_element = pokemon.find('a', class_='ent-name')
    name = name_element.text if name_element else None

    types_elements = pokemon.find_all('a', class_='itype')
    types = [a.text for a in types_elements] if types_elements else None

    if len(types) == 1:
        types.append("No secondary type")  # No secondary type

    primary_type = types[0]
    secondary_type = types[1] if len(types) > 1 else None

    img_element = pokemon.find('img')
    img_url = img_element['src'] if img_element and 'src' in img_element.attrs else None

    number_element = pokemon.find('small')
    number = number_element.text if number_element else None

    number = int(number[1:])
    # Determine the generation
    generation = None
    for limit, gen_name in zip(generation_limits, generations):
        if number <= limit:
            generation = gen_name
            break

    if name and generation and primary_type and img_url:
        insert_pokemon(name, generation, primary_type, secondary_type, img_url)

print("All Pokémon have been inserted into the database.")
