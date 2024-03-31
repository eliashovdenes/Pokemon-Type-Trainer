import streamlit as st
import random as randInt
import sqlite3
import streamlit_shadcn_ui as ui

# Set the page title and page icon
st.set_page_config(page_title="Pokemon type trainer!", page_icon="logo2.png", layout="wide")


# Hide various Streamlit stuff
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
            header {visibility: hidden;}
            [data-testid="stActionButtonLabel"] {visibility: hidden;}
            [data-testid="manage-app-button"] {visibility: hidden;}
            .styles_terminalButton__JBj5T {visibility: hidden;}
            .viewerBadge_container__r5tak styles_viewerBadge__CvC9N {visibility: hidden;}
            .viewerBadge_link__qRIco {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 









# Function to fetch a Pokémon from the database
def fetch_pokemon(pokemon_id):
    conn = sqlite3.connect('pokemon.db')
    c = conn.cursor()
    c.execute('SELECT * FROM pokemon WHERE id = ?', (pokemon_id,))
    pokemon = c.fetchone()
    conn.close()
    return pokemon

# Function to pick a random Pokémon
def new_pokemon():
    # random number from 1 to 1025 
    random_number = randInt.randint(1, 1025)
    st.session_state['current_pokemon_id'] = random_number


if 'current_pokemon_id' not in st.session_state:
    new_pokemon()

# Fetch the current Pokémon
pokemon = fetch_pokemon(st.session_state['current_pokemon_id'])


# Unpack the Pokémon data
pokemon_name, generation, primary_type, secondary_type, image_url = pokemon[1:6]

# Prepare the correct answers for checking
correct_answers = {
    'generation': generation,
    'typing': primary_type,
    'secondary_typing': secondary_type
}

# Title information
with st.container():
        st.title("Pokemon Type Trainer", anchor=False)
        st.write("Guess the pokemons generation and typing!")
        st.subheader("", divider=True)
        


with st.container():
        # Display the current Pokémon, generation guessing, and typing guessing
        one, two, three = st.columns(3)
        # Display the current Pokémon
        with one:
            st.subheader("""Current Pokemon:""", anchor=False)
            
            st.image(image_url, width=300, caption=pokemon_name)

            hide_img_fs = '''
            <style>
            button[title="View fullscreen"]{
                visibility: hidden;}
            </style>
            '''

            st.markdown(hide_img_fs, unsafe_allow_html=True)


        # Display the generation guessing
        with two:
            # Generation Dropdown
            generation_options = ['Choose One:', 'Gen 1/Kanto', 'Gen 2/Johto', 'Gen 3/Hoenn', 'Gen 4/Sinnoh', 'Gen 5/Unova', 'Gen 6/Kalos', 'Gen 7/Alola', 'Gen 8/Galar', 'Gen 9/Paldea']
            generation_disabled = st.session_state.get('generation_correct', False)
            selected_generation = st.selectbox(
                "Select the generation:",
                generation_options,
                index=0,
                disabled=generation_disabled,
                key='generation_selection'
                
            )

            # Button to check the generation, only visible if the correct answer hasn't been given yet
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
    
            


        # Display the typing guessing
        with three:
            left, right = st.columns(2)
            # Display the typing guessing for the primary typing
            with left:
                # Typing Dropdown
                typing_options = ['Choose One:', 'Normal', 'Fire', 'Water', 'Electric', 'Grass', 'Ice', 'Fighting', 'Poison', 'Ground', 'Flying', 'Psychic', 'Bug', 'Rock', 'Ghost', 'Dragon', 'Dark', 'Steel', 'Fairy']

                
                typing_disabled = st.session_state.get('typing_correct', False)
                selected_typing = st.selectbox(
                    "Select the typing:",
                    typing_options,
                    index=0,
                    disabled=typing_disabled,
                    key='typing_selection'
                )

            # Display the typing guessing for the secondary typing
            with right:
                # Typing Dropdown
                typing_options2 = ['No secondary type', 'Normal', 'Fire', 'Water', 'Electric', 'Grass', 'Ice', 'Fighting', 'Poison', 'Ground', 'Flying', 'Psychic', 'Bug', 'Rock', 'Ghost', 'Dragon', 'Dark', 'Steel', 'Fairy']

                
                typing_disabled2 = st.session_state.get('typing_correct', False)
                selected_typing2 = st.selectbox(
                    "Select the secondary typing:",
                    typing_options2,
                    index=0,
                    disabled=typing_disabled2,
                    key='typing_selection2'
                )

                


            # Button to check the typing, only visible if the correct answer hasn't been given yet
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

            

            
            
# function to reset the values in the dropdowns 
def reset():
    st.session_state.generation_selection = 'Choose One:'
    st.session_state.typing_selection = 'Choose One:'
    st.session_state.typing_selection2 = 'No secondary type'


def answer():
    st.session_state.generation_selection = generation
    st.session_state.typing_selection = primary_type
    st.session_state.typing_selection2 = secondary_type





# Display the success message and button to get a new Pokémon
with st.container():

        if st.session_state.get('generation_correct') and st.session_state.get('typing_correct'):
            st.write("You got all the answers correct!")

            if st.button("Next Pokemon", on_click=reset):
                new_pokemon()
                # Clear previous answers correctness
                st.session_state['generation_correct'] = False
                st.session_state['typing_correct'] = False
                st.session_state["answer_button"] = True
                st.rerun()  # This reruns the script to reflect the new state



with st.container():
    if st.session_state.get("answer_button", True):
        if st.button("Show me the answers", on_click=answer):
                        typing_disabled = True
                        st.session_state['typing_correct'] = True
                        typing_disabled2 = True
                        st.session_state['generation_correct'] = True

                        st.session_state["answer_button"] = False
                        st.rerun()








        
    
    
    
    















            