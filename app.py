import streamlit as st
import random 
import sqlite3



# Set the page title and page icon
st.set_page_config(page_title="Pokemon type trainer!", page_icon="logo2.png", layout="wide")



def display_streak():
    """Displays the current streak in the sidebar."""
    st.sidebar.write("## Current Streak")
    st.sidebar.write(f"🔥 Your current streak: {st.session_state['current_streak']}")
    st.sidebar.write(f"🔥 Your highest streak: {st.session_state['highest_streak']}")

    
if 'highest_streak' not in st.session_state:
    st.session_state['highest_streak'] = 0


if 'increased_high' not in st.session_state:
    st.session_state["increased_high"] = False



def answer():
    st.session_state.generation_selection = generation
    st.session_state.typing_selection = primary_type
    st.session_state.typing_selection2 = secondary_type

def answerGen():
    st.session_state.generation_selection = generation
    

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




# Initialize state for each generation toggle if not already done
for gen in range(1, 10):  # Generations 1 to 9
    if f'gen{gen}' not in st.session_state:
        st.session_state[f'gen{gen}'] = True  # Default all to False

# Generation ID ranges in your database (Example ranges, adjust according to your dataset)
gen_id_ranges = {
    1: (1, 151),
    2: (152, 251),
    3: (252, 386),
    4: (387, 493),
    5: (494, 649),
    6: (650, 721),
    7: (722, 809),
    8: (810, 905),
    9: (906, 1025),  
}


if 'prev_streak' not in st.session_state:
    st.session_state['prev_streak'] = 0

if 'correct_guess_made' not in st.session_state:
    st.session_state['correct_guess_made'] = True

if 'current_streak' not in st.session_state:
    st.session_state['current_streak'] = 0  # Tracks the number of correct guesses in a row

if 'show_answer_pressed' not in st.session_state:
    st.session_state['show_answer_pressed'] = False 

# Function to fetch a Pokémon from the database
def fetch_pokemon(pokemon_id):
    conn = sqlite3.connect('pokemon.db')
    c = conn.cursor()
    c.execute('SELECT * FROM pokemon WHERE id = ?', (pokemon_id,))
    pokemon = c.fetchone()
    conn.close()
    return pokemon

def new_pokemon():
    st.session_state['show_answer_pressed'] = False
    
    # Filter for active generations based on checkboxes and ensure the key exists in gen_id_ranges
    listOfActiveGens = []

    for gen in range(1, 10):
        if st.session_state[f'gen{gen}']:
            if gen in gen_id_ranges:
                listOfActiveGens.append(gen_id_ranges[gen])
            else:
                print(f"Generation {gen} not found in gen_id_ranges. Please add it to the dictionary.")

    # print(listOfActiveGens)  # Deb
    # if not listOfActiveGens:
    #     st.warning("Please select at least one generation.")
    #     return

    if not listOfActiveGens:
        listOfActiveGens = [(1, 1025)]
    
    randGen = random.choice(listOfActiveGens)
    random_id = random.randint(randGen[0], randGen[1])
    st.session_state['current_pokemon_id'] = random_id
    # print(random_id)  # Debug print

#Choose a random pokemon if not chosen
if 'current_pokemon_id' not in st.session_state or not st.session_state.get('current_pokemon_id'):
    new_pokemon()

# Fetch the current Pokémon
if 'current_pokemon_id' in st.session_state and st.session_state['current_pokemon_id']:
    pokemon = fetch_pokemon(st.session_state['current_pokemon_id'])


# Unpack the Pokémon data
pokemon_name, generation, primary_type, secondary_type, image_url = pokemon[1:6]

# Prepare the correct answers for checking
correct_answers = {
    'generation': generation,
    'typing': primary_type,
    'secondary_typing': secondary_type
}

with st.sidebar:
    
    
    # display_streak()

    

    st.title("Generation Selection")
    st.checkbox("Gen 1/Kanto", key='gen1')
    st.checkbox("Gen 2/Johto", key='gen2')
    st.checkbox("Gen 3/Hoenn", key='gen3')
    st.checkbox("Gen 4/Sinnoh", key='gen4')
    st.checkbox("Gen 5/Unova", key='gen5')
    st.checkbox("Gen 6/Kalos", key='gen6')
    st.checkbox("Gen 7/Alola", key='gen7')
    st.checkbox("Gen 8/Galar", key='gen8')
    st.checkbox("Gen 9/Paldea", key='gen9')

    st.write("")
    
    
    

    


    

# Fetch and display the current Pokémon
if 'current_pokemon_id' in st.session_state:
    pokemon = fetch_pokemon(st.session_state['current_pokemon_id'])

# Title information
with st.container():
        st.title("Pokemon Type Trainer", anchor=False)

        left , right = st.columns([5, 5])
        with left:
            st.caption("Welcome to the Pokemon Type Trainer! Guess the generation and typing of the Pokémon displayed. Click the 'Show Answers' button to get the answers. Click the 'Next Pokemon' button to get a new Pokémon. You can select the generations you want to guess from the sidebar. Good luck!")
            
        st.subheader("", divider=True)
        

# st.toast("Welcome to the Pokemon Type Trainer! Guess the generation and typing of the Pokémon displayed.", icon="🔍")
        
# st.code("Pokemon Type Trainer", language="python")

# st.download_button("Download the code", data="Pokemon Type Trainer", file_name="Pokemon_Type_Trainer.py", mime="text/python", key="download_button")



# st.info("Select the generation and typing of the Pokémon displayed. Click the 'Show Answers' button to get the answers. Click the 'Next Pokemon' button to get a new Pokémon. You can select the generations you want to guess from the sidebar. Good luck!")

# st.help()s

# with st.popover("Hello"):
#     st.caption("Welcome to the Pokemon Type Trainer! Guess the generation and typing of the Pokémon displayed. Click the 'Show Answers' button to get the answers. Click the 'Next Pokemon' button to get a new Pokémon. You can select the generations you want to guess from the sidebar. Good luck!")
        

 


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

            listOfActiveGensNum = []

            for gen in range(1, 10):
                if st.session_state[f'gen{gen}']:
                    if gen in gen_id_ranges:
                        listOfActiveGensNum.append(gen)
                    else:
                        print(f"Generation {gen} not found in gen_id_ranges. Please add it to the dictionary.")

            # print(listOfActiveGensNum)  # Debug print


            # if len of active generations is 1, set the correct generation to the only generation selected and if the user has clicked the next pokemon button
            
            if len(listOfActiveGensNum) == 1:
                #extract number from generation string
                checkGen = f'Gen {listOfActiveGensNum[0]}'
                
                
                if checkGen in generation:
                    # print("Only one generation selected")
                    # set the correct generation to the only generation selected
                    st.session_state['generation_correct'] = True
                    answerGen()

            #All options
            generation_options = ['Choose One:', 'Gen 1/Kanto', 'Gen 2/Johto', 'Gen 3/Hoenn', 'Gen 4/Sinnoh', 'Gen 5/Unova', 'Gen 6/Kalos', 'Gen 7/Alola', 'Gen 8/Galar', 'Gen 9/Paldea']

            #Only keep the active gens
            if len(listOfActiveGensNum) != 9:
                newGeneration_options = [generation_options[0]]
                for elem in listOfActiveGensNum:
                    newGeneration_options.append(generation_options[elem])

                generation_options = newGeneration_options

            
            
            print(generation_options)

            if 'generation_selection' not in st.session_state:
                st.session_state.generation_selection = 'Choose One:'


            if generation not in generation_options:
                generation_options.append(generation)

            # Generation Dropdown
            # generation_options = ['Choose One:', 'Gen 1/Kanto', 'Gen 2/Johto', 'Gen 3/Hoenn', 'Gen 4/Sinnoh', 'Gen 5/Unova', 'Gen 6/Kalos', 'Gen 7/Alola', 'Gen 8/Galar', 'Gen 9/Paldea']
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
                        if st.session_state['current_streak'] > 0:
                            st.toast("Streak lost! :fire:")
                        st.session_state["current_streak"] = 0
                        st.session_state['correct_guess_made'] = False
                        # st.rerun()
                        

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
                    "Select the primary typing:",
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
                        if st.session_state['current_streak'] > 0:
                            st.toast("Streak lost! :fire: ")
                        st.session_state["current_streak"] = 0
                        st.session_state['correct_guess_made'] = False
                        # st.rerun()

            else:
                st.success("Correct!")

            

            
            
# function to reset the values in the dropdowns 
def reset():
    st.session_state.generation_selection = 'Choose One:'
    st.session_state.typing_selection = 'Choose One:'
    st.session_state.typing_selection2 = 'No secondary type'








# Display the success message and button to get a new Pokémon
with st.container():
        if st.session_state.get('generation_correct') and st.session_state.get('typing_correct'):
            if st.session_state.get("show_answer_pressed") == False and len(listOfActiveGensNum) == 9 and st.session_state['correct_guess_made'] == True:
                # st.write("You got all the answers correct!")
                st.session_state['current_streak'] += 1
                if st.session_state['current_streak'] > st.session_state['highest_streak']:
                    st.session_state['highest_streak'] = st.session_state['current_streak']
                    st.session_state['increased_high'] = True
                
                # st.session_state['highest_streak']

                
                
                # if st.session_state['current_streak'] > st.session_state["highest_streak"]:
                #     st.session_state["highest_streak"] = st.session_state['current_streak']

                

            else:
                if st.session_state['prev_streak'] > 0:
                    st.toast("Streak lost! :fire: ") 
                    print("Hello2")

                elif st.session_state['current_streak'] > 0:
                    st.toast("Streak lost! :fire: ")
                    st.toast("You have disabled a generation!")
                    print("Hello1")

                

                print("Prev streak: ", st.session_state['prev_streak'])
                print("Current streak", st.session_state['current_streak'])
                print("I come herre")

                st.session_state['current_streak'] = 0
                st.session_state['prev_streak'] = 0
                
                
                
                
            # st.write("Streak:", st.session_state['current_streak'])
            print(st.session_state['current_streak'])
            st.session_state["answer_button"] = False
            # st.write("You got all the answers correct!")

            
            if st.button("Next Pokemon", on_click=reset):
                st.session_state["answer_button"] = True
                st.session_state['current_streak'] -= 1
                if st.session_state["increased_high"] == True:
                    st.session_state['highest_streak'] = st.session_state['highest_streak']-1
                    st.session_state["increased_high"] = False
                
                # st.session_state['highest_streak']-1


                


                if st.session_state['current_streak'] < 0:
                    st.session_state['current_streak'] = 0

                # if st.session_state['highest_streak'] < 0:
                #     st.session_state['highest_streak'] = 0

                

                
                
                new_pokemon()
                # Clear previous answers correctness
                st.session_state['generation_correct'] = False
                st.session_state['typing_correct'] = False
                st.session_state['correct_guess_made'] = True
                
                st.rerun()  # This reruns the script to reflect the new state

    




# Display the answers
with st.container():
    if st.session_state.get("answer_button", True):
        if st.button("Show me the answers", on_click=answer):
                        st.session_state["answer_button"] = False
                        typing_disabled = True
                        st.session_state['typing_correct'] = True
                        typing_disabled2 = True
                        st.session_state['generation_correct'] = True

                        # Set the state to show the answers
                        st.session_state['show_answer_pressed'] = True
                        # Reset the streak
                        if st.session_state['current_streak'] > 0:
                            st.session_state['prev_streak'] = st.session_state['current_streak']

                        

                        st.session_state['current_streak'] = 0

                        st.rerun()


# st._bottom.caption("Made by [Elias Hovdenes](https://github.com/eliashovdenes/Pokemon-Type-Trainer)")
# st.link_button("GitHub","https://github.com/eliashovdenes/Pokemon-Type-Trainer", type="primary")


display_streak()





    
with st.sidebar:

    if len(listOfActiveGensNum) != 9:
        st.caption("Enable all generations to gain streak")

    st.write("")
   

    with st.expander(" :grey_question:"):
            
    
        st.caption("The generation selection will be applied when clicking the 'Next Pokemon' button. If no generation is selected, the generation will be chosen randomly from all generations. \n \n If you guess correct on the first try you will get a streak :fire:. The streak only applies when guessing on all the generations, it will reset if you guess wrong, click the 'Show me the answers' button or you deselect a generation. \n \n The correct answers will be shown after clicking the 'Show Answers' button. \n \n Good luck!")
    with st.expander("Credits"):
        st.caption(":point_right: Made by [Elias Hovdenes](https://github.com/eliashovdenes) :point_left:")
    









        
    
    
    
    















            