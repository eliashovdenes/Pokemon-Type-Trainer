import streamlit as st
import random as randInt
import sqlite3


st.set_page_config(page_title="Pokemon type trainer!", page_icon=":monkey:", layout="wide")


hide_github_icon = """
    <style>
    #GithubIcon {visibility: hidden;}
    </style>
    """
st.markdown(hide_github_icon, unsafe_allow_html=True)


hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 







def fetch_pokemon(pokemon_id):
    conn = sqlite3.connect('pokemon.db')
    c = conn.cursor()
    c.execute('SELECT * FROM pokemon WHERE id = ?', (pokemon_id,))
    pokemon = c.fetchone()
    conn.close()
    return pokemon

# Function to initialize or reset the Pokémon shown
def new_pokemon():
    # random number from 1 to 10 (assuming you have at least 10 Pokémon in your database)
    random_number = randInt.randint(1, 1025)
    st.session_state['current_pokemon_id'] = random_number


if 'current_pokemon_id' not in st.session_state:
    new_pokemon()

pokemon = fetch_pokemon(st.session_state['current_pokemon_id'])


pokemon_name, generation, primary_type, secondary_type, image_url = pokemon[1:6]

# Prepare the correct answers for checking
correct_answers = {
    'generation': generation,
    'typing': primary_type,
    'secondary_typing': secondary_type
}
with st.container():
        st.title("Pokemon Type Trainer", anchor=False)
        st.write("Guess the pokemons generation and typing!")
        st.subheader("", divider=True)
        
#add a line
# st.markdown("""---""")






with st.container():
        one, two, three = st.columns(3)
        with one:
            
    
            
            st.subheader("""     Current Pokemon:""")
            #picture
            url = pokemon[5]
            st.image(url, width=300, caption=pokemon_name )

            hide_img_fs = '''
            <style>
            button[title="View fullscreen"]{
                visibility: hidden;}
            </style>
            '''

            st.markdown(hide_img_fs, unsafe_allow_html=True)


        with two:
            # Generation Dropdown
            generation_options = ['Choose One:', 'Gen 1/Kanto', 'Gen 2/Johto', 'Gen 3/Hoenn', 'Gen 4/Sinnoh', 'Gen 5/Unova', 'Gen 6/Kalos', 'Gen 7/Alola', 'Gen 8/Galar', 'Gen 9/Paldea']
            generation_disabled = st.session_state.get('generation_correct', False)
            selected_generation = st.selectbox(
                "Select the generation:",
                generation_options,
                index=0,
                disabled=generation_disabled
            )

            # Button to check the generation, only enabled if the correct answer hasn't been given yet
            if not generation_disabled:
                if st.button('Check Generation'):
                    if selected_generation == correct_answers['generation']:
                        st.session_state['generation_correct'] = True
                        generation_disabled = True
                        st.rerun()
                    else:
                        st.error("Incorrect. Try again.")

            else:
                st.success("Correct!")
    
            


        
        with three:
            left, right = st.columns(2)
            with left:
                # Typing Dropdown
                typing_options = ['Choose One:', 'Normal', 'Fire', 'Water', 'Electric', 'Grass', 'Ice', 'Fighting', 'Poison', 'Ground', 'Flying', 'Psychic', 'Bug', 'Rock', 'Ghost', 'Dragon', 'Dark', 'Steel', 'Fairy']

                
                typing_disabled = st.session_state.get('typing_correct', False)
                selected_typing = st.selectbox(
                    "Select the typing:",
                    typing_options,
                    index=0,
                    disabled=typing_disabled
                )

            with right:
                # Typing Dropdown
                typing_options2 = ['No secondary type', 'Normal', 'Fire', 'Water', 'Electric', 'Grass', 'Ice', 'Fighting', 'Poison', 'Ground', 'Flying', 'Psychic', 'Bug', 'Rock', 'Ghost', 'Dragon', 'Dark', 'Steel', 'Fairy']

                
                typing_disabled2 = st.session_state.get('typing_correct', False)
                selected_typing2 = st.selectbox(
                    "Select the secondary typing:",
                    typing_options2,
                    index=0,
                    disabled=typing_disabled2
                )


            # Button to check the typing, only enabled if the correct answer hasn't been given yet
            if not typing_disabled:
                if st.button('Check Typing'):
                    if selected_typing == correct_answers['typing'] and selected_typing2 == correct_answers['secondary_typing'] or selected_typing == correct_answers['secondary_typing'] and selected_typing2 == correct_answers['typing']:
                        st.session_state['typing_correct'] = True
                        typing_disabled = True
                        st.rerun()
                    else:
                        st.error("Incorrect. Try again.")

            else:
                st.success("Correct!")

            
            
            

with st.container():
     if st.session_state.get('generation_correct') and st.session_state.get('typing_correct'):
        st.write("You got all the answers correct!")

        if st.button("Next Pokemon"):
            new_pokemon()
            # Clear previous answers correctness
            st.session_state['generation_correct'] = False
            st.session_state['typing_correct'] = False
            st.rerun()  # This reruns the script to reflect the new state












            