import sqlite3

# Connect to the database
conn = sqlite3.connect('pokemon.db')
cursor = conn.cursor()

# Select all Pokémon ids
cursor.execute("SELECT id FROM pokemon")
pokemon_list = cursor.fetchall()

# Function to create the new image URL based on the Pokémon id
def create_new_image_url(pokemon_id):
    return f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{pokemon_id}.png"

# Update each Pokémon's image_url
for pokemon in pokemon_list:
    pokemon_id = pokemon[0]
    new_url = create_new_image_url(pokemon_id)
    cursor.execute("UPDATE pokemon SET image_url=? WHERE id=?", (new_url, pokemon_id))

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Done")
