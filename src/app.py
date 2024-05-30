import streamlit as st
import random 
import sqlite3
import pandas as pd
import hashlib
import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv
from psycopg2 import pool
from streamlit_cookies_manager import EncryptedCookieManager

# Set the page title and page icon
st.set_page_config(page_title="Pokemon type trainer!", page_icon="../pictures/logo2.png", layout="wide")







# Load environment variables from .env file (for local testing)
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
COOKIE_PASSWORD = os.getenv('COOKIE_PASSWORD')

# Initialize cookies manager
cookies = EncryptedCookieManager(
    prefix='pokemon_prep',
    password=COOKIE_PASSWORD
)



if not cookies.ready():
    st.stop()

if not DATABASE_URL:
    raise ValueError("No DATABASE_URL found in environment variables")

@st.cache_resource
def init_connection_pool():
    return pool.SimpleConnectionPool(1, 10, DATABASE_URL)

conn_pool = init_connection_pool()

def get_db_connection():
    return conn_pool.getconn()

def release_db_connection(conn):
    conn_pool.putconn(conn)

# Function to reset state variables when toggling "Guess the name"
def toggle_guess_name():
    st.session_state['correct_guess_made'] = False
    st.session_state['name_guess_bool'] = False

# Generator that produces the next char in the string
# def next_char(s):
#     for c in s:
#         yield c
#         time.sleep(0.05)

# Display the welcome message
# if st.session_state["welcome"] == True:
#     st.write_stream(next_char("Welcom to Pokemon Type Trainer!"))
#     time.sleep(1)
#     st.session_state["welcome"] = False
#     st.rerun()

#saving the highest streak to database
def update_highest_streak(user_id, new_streak):
    conn = get_db_connection()
    try:
        c = conn.cursor()
        c.execute('SELECT highest_streak FROM user_scores WHERE user_id = %s', (user_id,))
        result = c.fetchone()
        if result:
            highest_streak = result[0]
            if new_streak > highest_streak:
                c.execute('UPDATE user_scores SET highest_streak = %s WHERE user_id = %s', (new_streak, user_id))
        else:
            c.execute('INSERT INTO user_scores (user_id, highest_streak) VALUES (%s, %s)', (user_id, new_streak))
        conn.commit()
    finally:
        release_db_connection(conn)


def display_streak():
    st.subheader("Current Streak", anchor=False)
    st.write(f"🔥 Your current streak: {st.session_state['current_streak']}")
    st.write(f"🔥 Your highest streak: {st.session_state['highest_streak']}")
    if st.session_state['logged_in']:
        if st.session_state['logged_in']:
            current_user_id = st.session_state['user_id']
            update_highest_streak(current_user_id, st.session_state['highest_streak'])

    




# Funcion to set all the answers to the correct answers
def answer():
    st.session_state.generation_selection = generation
    st.session_state.typing_selection = primary_type
    st.session_state.typing_selection2 = secondary_type
    if st.session_state['guess_name']:
        st.session_state.select_name = pokemon_name

def answerGen():
    st.session_state.generation_selection = generation

for gen in range(1, 10):
    if f'gen{gen}' not in st.session_state:
        st.session_state[f'gen{gen}'] = True

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

@st.cache_data
def load_pokemon_names():
    conn = sqlite3.connect('pokemon.db')
    c = conn.cursor()
    c.execute('SELECT name FROM pokemon')
    names = [name[0] for name in c.fetchall()]
    conn.close()
    names.insert(0, "Write here/Choose One:")
    return names

listOfPokemonNames = load_pokemon_names()



def initialize_session_state():
    session_defaults = {
        'highest_streak': 0,
        'increased_high': False,
        'prev_streak': 0,
        'correct_guess_made': True,
        'current_streak': 0,
        'show_answer_pressed': False,
        'guess_name': False,
        'name_guess_bool': False
    }
    for key, value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()



    

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
    listOfActiveGens = [gen_id_ranges[gen] for gen in range(1, 10) if st.session_state[f'gen{gen}']]
    if not listOfActiveGens:
        listOfActiveGens = [(1, 1025)]
    randGen = random.choice(listOfActiveGens)
    random_id = random.randint(randGen[0], randGen[1])
    st.session_state['current_pokemon_id'] = random_id

if 'current_pokemon_id' not in st.session_state or not st.session_state.get('current_pokemon_id'):
    new_pokemon()

if 'current_pokemon_id' in st.session_state and st.session_state['current_pokemon_id']:
    pokemon = fetch_pokemon(st.session_state['current_pokemon_id'])

pokemon_name, generation, primary_type, secondary_type, image_url = pokemon[1:6]

correct_answers = {
    'generation': generation,
    'typing': primary_type,
    'secondary_typing': secondary_type
}

if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False


# Check if user is already logged in via cookies
if cookies.get('username'):
    st.session_state['logged_in'] = True
    conn = get_db_connection()
    try:
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = %s', (cookies.get('username'),))
        user = c.fetchone()
        if user:
            st.session_state['user_id'] = user[0]
    finally:
        release_db_connection(conn)

if st.session_state['logged_in']:
    st.caption("Logged in as " + cookies.get('username'))
    
    

tab1, tab2, leaderboard, tab3, tab4 = st.tabs(["Pokemon Type Trainer", "Streak", "Leaderboard", "Options", "About"])

with leaderboard:

    if not st.session_state['logged_in']:
        st.write("To see and use leaderboard you have to login")

    def load_banned_words(file_path):
        with open(file_path, 'r') as file:
            banned_words = [line.strip().lower() for line in file.readlines()]
        return banned_words

    if not st.session_state['logged_in']:
        banned_words = load_banned_words('./helper_files/bannedwords.txt')
        

    def contains_banned_word(username):
        username_lower = username.lower()
        return any(banned_word in username_lower for banned_word in banned_words)

    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    def check_password(stored_password_hash, provided_password):
        return stored_password_hash == hash_password(provided_password)

    def create_user(username, password):
        conn = get_db_connection()
        try:
            c = conn.cursor()
            c.execute('SELECT * FROM users WHERE username = %s', (username,))
            user = c.fetchone()
            if user or contains_banned_word(username):
                return False, "Username already taken"
            password_hash = hash_password(password)
            c.execute('INSERT INTO users (username, password_hash) VALUES (%s, %s)', (username, password_hash))
            conn.commit()
            return True, "User registered successfully!"
        finally:
            release_db_connection(conn)

    def login_user(username, password):
        conn = get_db_connection()
        try:
            c = conn.cursor()
            c.execute('SELECT * FROM users WHERE username = %s', (username,))
            user = c.fetchone()
            if user and check_password(user[2], password):
                cookies['username'] = username
                cookies.save()
                return user
            return None
        finally:
            release_db_connection(conn)
    

    
    # Registration Form
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    left, right = st.columns(2)

    with right:
        if not st.session_state['logged_in']:
            st.write("Not registered?")

        with st.expander("Register now"):

            if not st.session_state['logged_in']:
                # st.write("Register")
                username = st.text_input("Username", key='register_username')
                password = st.text_input("Password", type="password", key='register_password')
                if st.button("Register"):
                    if not username.strip() or not password.strip():
                        st.error("Username and password cannot be empty or just spaces.")

                    elif contains_banned_word(username):
                        st.error("Username already taken")
                
                    else:
                        success, message = create_user(username, password)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                        
                    

    with left:
        # Login Form
        if not st.session_state['logged_in']:
            st.write("Login")
            username = st.text_input("Username", key='login_username')
            password = st.text_input("Password", type="password", key='login_password')
            if st.button("Login"):
                user = login_user(username, password)
                if user:
                    st.session_state['logged_in'] = True
                    st.session_state['user_id'] = user[0]
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")



    

    if  st.session_state['logged_in']:
        # st.title("You are logged in!")

        # Fetch leaderboard data
        @st.cache_data(ttl=60)  # Cache for 60 seconds
        def fetch_leaderboard():
            conn = get_db_connection()
            try:
                c = conn.cursor()
                c.execute('''
                    SELECT u.username, s.highest_streak
                    FROM user_scores s
                    JOIN users u ON s.user_id = u.user_id
                    ORDER BY s.highest_streak DESC
                    LIMIT 10
                ''')
                leaderboard = c.fetchall()
                leaderboard_df = pd.DataFrame(leaderboard, columns=["Username", "Highest Streak"])
                leaderboard_df["Rank"] = leaderboard_df.index + 1
                leaderboard_df = leaderboard_df[["Rank", "Username", "Highest Streak"]]
                return leaderboard_df
            finally:
                release_db_connection(conn)

        # Display the leaderboard
        
        st.title("Leaderboard", anchor=False)
        leaderboard_df = fetch_leaderboard()
        hide_dataframe_hover_buttons = """
            <style>
            .stDataFrame div[data-testid="stDataFrameResizable"] {
                position: relative;
            }
            .stDataFrame div[data-testid="stElementToolbar"] {
                display: none !important;
            }
            </style>
        """
        st.markdown(hide_dataframe_hover_buttons, unsafe_allow_html=True)
        st.dataframe(
            leaderboard_df,
            column_config={
                "Rank": "Rank",
                "Username": "Username",
                "Highest Streak": st.column_config.NumberColumn("Highest Streak", format="%d 🔥"),
            },
            hide_index=True,
            
        
        )
        
        
       
       
        # left, right = st.columns([1,4])
        # with left:
        #     with st.expander("?"):
        #         st.write("Leaderboard updates take 1 min")
        st.divider()
        # Add a logout button
        if st.session_state['logged_in']:
            st.subheader("Account", anchor=False)
            st.write("User: ", cookies.get('username') )
            if st.button("Logout"):
                st.session_state['logged_in'] = False
                cookies['username'] = ''
                st.session_state['current_streak'] = 0
                st.session_state['highest_streak'] =0
                cookies.save()
                st.success("Logged out successfully!")
                st.rerun()

            

        





    

with tab3:
    left, right, third = st.columns([1, 1, 1])
    with left:
        st.subheader("Generation Selection", anchor=False)
        if "Enable all" not in st.session_state:
            st.session_state["Enable all"] = True
        if st.button("Enable all/Disable all", key="enable_all"):
            if st.session_state["Enable all"]:
                for gen in range(1, 10):
                    st.session_state[f'gen{gen}'] = False
                st.session_state["Enable all"] = False
            else:
                for gen in range(1, 10):
                    st.session_state[f'gen{gen}'] = True
                st.session_state["Enable all"] = True
        for gen in range(1, 10):
            st.checkbox(f"Gen {gen}", key=f'gen{gen}')
    with right:
        st.subheader("Extra Options", anchor=False)
        guess_name_toggle = st.checkbox("Guess the name", value=st.session_state['guess_name'], key="guess_name", on_change=toggle_guess_name)

    
    


# Fetch and display the current Pokémon if new pokemon is ran
if 'current_pokemon_id' in st.session_state:
    pokemon = fetch_pokemon(st.session_state['current_pokemon_id'])


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




        

# Maybe UI for later:
# st.toast("Welcome to the Pokemon Type Trainer! Guess the generation and typing of the Pokémon displayed.", icon="🔍")   
# st.code("Pokemon Type Trainer", language="python")
# st.download_button("Download the code", data="Pokemon Type Trainer", file_name="Pokemon_Type_Trainer.py", mime="text/python", key="download_button")
# st.info("Select the generation and typing of the Pokémon displayed. Click the 'Show Answers' button to get the answers. Click the 'Next Pokemon' button to get a new Pokémon. You can select the generations you want to guess from the sidebar. Good luck!")
# st.help()
# with st.popover("Hello"):
#     st.caption("Welcome to the Pokemon Type Trainer! Guess the generation and typing of the Pokémon displayed. Click the 'Show Answers' button to get the answers. Click the 'Next Pokemon' button to get a new Pokémon. You can select the generations you want to guess from the sidebar. Good luck!")
# st._bottom.caption("Made by [Elias Hovdenes](https://github.com/eliashovdenes/Pokemon-Type-Trainer)")
# st.link_button("GitHub","https://github.com/eliashovdenes/Pokemon-Type-Trainer", type="primary")        
# st.popover
# st.radio st.info



# Display the Pokémon image and the guessing options
    
with tab1:
    with st.container():
        one, two, three = st.columns([3, 2, 3])
        pokename = pokemon_name if not st.session_state['guess_name'] else ""
        with one:
            st.subheader("Current Pokemon:", anchor=False)
            st.image(image_url, width=300, caption=pokename)
            hide_img_fs = '<style>button[title="View fullscreen"]{visibility: hidden;}</style>'
            st.markdown(hide_img_fs, unsafe_allow_html=True)
        with two:
            listOfActiveGensNum = [gen for gen in range(1, 10) if st.session_state[f'gen{gen}']]
            if len(listOfActiveGensNum) == 1:
                checkGen = f'Gen {listOfActiveGensNum[0]}'
                if checkGen in generation:
                    st.session_state['generation_correct'] = True
                    answerGen()
            generation_options = ['Choose One:', 'Gen 1/Kanto', 'Gen 2/Johto', 'Gen 3/Hoenn', 'Gen 4/Sinnoh', 'Gen 5/Unova', 'Gen 6/Kalos', 'Gen 7/Alola', 'Gen 8/Galar', 'Gen 9/Paldea']
            if len(listOfActiveGensNum) != 9:
                generation_options = ['Choose One:'] + [generation_options[gen] for gen in listOfActiveGensNum]
            if 'generation_selection' not in st.session_state:
                st.session_state.generation_selection = 'Choose One:'
            if generation not in generation_options:
                generation_options.append(generation)
            generation_disabled = st.session_state.get('generation_correct', False)
            selected_generation = st.selectbox(
                "Select the generation:", generation_options, index=0, disabled=generation_disabled, key='generation_selection'
            )
            if not generation_disabled and st.button('Check Generation'):
                if selected_generation != 'Choose One:':
                    if selected_generation == correct_answers['generation']:
                        st.session_state['generation_correct'] = True
                        # Save typing selections before rerun
                        st.session_state.typing_selection = st.session_state.typing_selection
                        st.session_state.typing_selection2 = st.session_state.typing_selection2
                        st.rerun()
                    else:
                        st.error("Incorrect. Try again.")
                        st.session_state["current_streak"] = 0
                        st.session_state['correct_guess_made'] = False
                else:
                    st.error("Please select a generation.")
            elif generation_disabled:
                st.success("Correct!")
        with three:
            left, right = st.columns(2)
            typing_options = ['Choose One:', 'Normal', 'Fire', 'Water', 'Electric', 'Grass', 'Ice', 'Fighting', 'Poison', 'Ground', 'Flying', 'Psychic', 'Bug', 'Rock', 'Ghost', 'Dragon', 'Dark', 'Steel', 'Fairy']
            typing_options2 = ['No secondary type'] + typing_options[1:]
            if 'typing_selection' not in st.session_state:
                st.session_state.typing_selection = 'Choose One:'
            if 'typing_selection2' not in st.session_state:
                st.session_state.typing_selection2 = 'No secondary type'
            with left:
                typing_disabled = st.session_state.get('typing_correct', False)
                selected_typing = st.selectbox(
                    "Select the primary typing:", typing_options, index=0, disabled=typing_disabled, key='typing_selection'
                )
            with right:
                typing_disabled2 = st.session_state.get('typing_correct', False)
                selected_typing2 = st.selectbox(
                    "Select the secondary typing:", typing_options2, index=0, disabled=typing_disabled2, key='typing_selection2'
                )
            if not typing_disabled and st.button('Check Typing'):
                if selected_typing != 'Choose One:':
                    if (selected_typing == correct_answers['typing'] and selected_typing2 == correct_answers['secondary_typing']) or (selected_typing == correct_answers['secondary_typing'] and selected_typing2 == correct_answers['typing']):
                        st.session_state['typing_correct'] = True
                        st.rerun()
                    else:
                        st.error("Incorrect. Try again.")
                        st.session_state["current_streak"] = 0
                        st.session_state['correct_guess_made'] = False
                else:
                    st.error("Please select at least the primary typing.")
            elif typing_disabled:
                st.success("Correct!")
            if st.session_state['guess_name']:
                name_guess_disabled = st.session_state.get('name_guess_bool', False)
                name_guess = st.selectbox("Guess the name of the Pokémon:", listOfPokemonNames, index=0, key='select_name', disabled=name_guess_disabled)
                if not name_guess_disabled and st.button('Check Name'):
                    if name_guess.lower().strip() == pokemon_name.lower().strip():
                        st.success("Correct!")
                        st.session_state['name_guess_bool'] = True
                        st.rerun()
                    else:
                        st.error("Incorrect. Try again.")
                elif name_guess_disabled:
                    st.success("Correct!")

def reset():
    st.session_state.generation_selection = 'Choose One:'
    st.session_state.typing_selection = 'Choose One:'
    st.session_state.typing_selection2 = 'No secondary type'
    st.session_state.select_name = 'Write here/Choose One:'

with tab1:


    left, bin, right = st.columns([1,5,1])
    with left:
        with st.container():
                
                if st.session_state["guess_name"] == True:

                    if st.session_state.get('generation_correct') and st.session_state.get('typing_correct') and st.session_state.get('name_guess_bool'):
                        # print("I am here in the name guess true")
                        # If the user guessed correct on the first try, increase the streak
                        
                        if st.session_state.get("show_answer_pressed") == False and len(listOfActiveGensNum) == 9 and st.session_state['correct_guess_made'] == True:
                            st.session_state['current_streak'] += 1
                            st.toast("Streak increased! :tada: Current streak: " + str(st.session_state['current_streak']))
                            # If the current streak is higher than the highest streak, update the highest streak
                            if st.session_state['current_streak'] > st.session_state['highest_streak']:
                                st.session_state['highest_streak'] = st.session_state['current_streak']
                                st.session_state['increased_high'] = True
                                

                            
                        else:
                            # If the user guessed wrong, reset the streak and say that streak is lost
                            if st.session_state['prev_streak'] > 0:
                                st.toast("Streak lost! :fire: ")                   

                            elif st.session_state['current_streak'] > 0:
                                st.toast("Streak lost! :fire:")
                                # st.toast("You have disabled a generation!")

                            st.session_state['current_streak'] = 0
                            st.session_state['prev_streak'] = 0            
                        
                        st.session_state["answer_button"] = False

                        # If the user clicks the button, get a new Pokémon and reset the dropdowns
                        if st.button("Next Pokemon", on_click=reset):
                            st.session_state["answer_button"] = True
                            st.session_state['current_streak'] -= 1

                            if st.session_state["increased_high"] == True:
                                st.session_state['highest_streak'] = st.session_state['highest_streak']-1
                                st.session_state["increased_high"] = False
                                                        
                            
                            if st.session_state['current_streak'] < 0:
                                st.session_state['current_streak'] = 0

                            new_pokemon()
                            # Clear previous answers correctness
                            st.session_state['generation_correct'] = False
                            st.session_state['typing_correct'] = False
                            st.session_state['correct_guess_made'] = True
                            st.session_state['name_guess_bool'] = False
                            
                            st.rerun()  # This reruns the script to reflect the new state
                else:
                    if st.session_state.get('generation_correct') and st.session_state.get('typing_correct'):

                        # print("I am here in the name guess not active")
                        
                        # If the user guessed correct on the first try, increase the streak
                        # st.session_state['name_guess_bool'] = False
                        if st.session_state.get("show_answer_pressed") == False and len(listOfActiveGensNum) == 9 and st.session_state['correct_guess_made'] == True:
                            st.session_state['current_streak'] += 1
                            st.toast("Streak increased! :tada: Current streak: " + str(st.session_state['current_streak']))
                            # If the current streak is higher than the highest streak, update the highest streak
                            if st.session_state['current_streak'] > st.session_state['highest_streak']:
                                st.session_state['highest_streak'] = st.session_state['current_streak']
                                st.session_state['increased_high'] = True
                                


                        


                            
                        else:
                            # If the user guessed wrong, reset the streak and say that streak is lost
                            if st.session_state['prev_streak'] > 0:
                                st.toast("Streak lost! :fire: ")                   

                            elif st.session_state['current_streak'] > 0:
                                st.toast("Streak lost! :fire:")
                                # st.toast("You have disabled a generation!")

                            st.session_state['current_streak'] = 0
                            st.session_state['prev_streak'] = 0            
                        
                        st.session_state["answer_button"] = False

                        # If the user clicks the button, get a new Pokémon and reset the dropdowns
                        if st.button("Next Pokemon", on_click=reset):
                            st.session_state["answer_button"] = True
                            st.session_state['current_streak'] -= 1

                            if st.session_state["increased_high"] == True:
                                st.session_state['highest_streak'] = st.session_state['highest_streak']-1
                                st.session_state["increased_high"] = False

        
                                
                            
                            if st.session_state['current_streak'] < 0:
                                st.session_state['current_streak'] = 0

                            new_pokemon()
                            # Clear previous answers correctness
                            st.session_state['generation_correct'] = False
                            st.session_state['typing_correct'] = False
                            st.session_state['correct_guess_made'] = True
                            st.session_state['name_guess_bool'] = False
                            
                            st.rerun()  # This reruns the script to reflect the new state
            
    
    
    with right:
        # Display the answers
        with st.container():
            if st.session_state.get("answer_button", True):
                if st.button("Show me the answers", on_click=answer):
                    st.session_state["answer_button"] = False
                    typing_disabled = True
                    st.session_state['typing_correct'] = True
                    typing_disabled2 = True
                    st.session_state['generation_correct'] = True
                    st.session_state['name_guess_bool'] = True
                    name_guess_disabled = True
                    st.session_state['show_answer_pressed'] = True
                    if st.session_state['current_streak'] > 0:
                        st.session_state['prev_streak'] = st.session_state['current_streak']
                    st.session_state['current_streak'] = 0
                    st.rerun()

with tab2:
    display_streak()
    if len(listOfActiveGensNum) != 9:
        st.markdown(" Enable all generations to gain streak :exclamation:")


    
with tab4:
    left, center, right = st.columns([1, 1, 1])
    with left:
        with st.expander(f"**What is this?**"):
           
            st.write(f"**Welcome to the Pokemon Type Trainer!**")
            
            st.markdown("Guess the generation and typing of the random Pokémon displayed. Click the 'Show Answers' button to get the answers. When answers are correct you can click the 'Next Pokemon' button to get a new Pokémon.")
            st.write("")
            

            st.write(f"**Generation Selection**")
            
            st.markdown("You can select and deselect generations in Options. The generation selection will be applied when clicking the 'Next Pokemon' button. If no generation is selected, the generation will be chosen randomly from all generations.")
            st.write("")
            
           

            st.write(f"**Streak**")
            
            st.markdown("If you guess correct on the first try you will get a streak 🔥. The streak only applies when guessing on all the generations, it will reset if you guess wrong, click the 'Show me the answers' button or you change your options.")
            st.write("")
            

            st.write(f"**Extra Options**")

            st.markdown("You can also enable name guessing!")
            st.write("")
            



        with st.expander(f"**Inspiration**"):
            st.markdown("I made this site to train for sites such as [pokedoku.com](https://pokedoku.com). \n \n On pokedoku it is crucial to know the typing and generation of pokemon. That is why I wanted to make a site where you could guess the generation, typing and name of a pokemon. \n \n  Try it out :point_right: [pokedoku.com](https://pokedoku.com)")
        with st.expander(f"**Credits**"):
            st.markdown(":point_right: Made by [Elias Hovdenes](https://github.com/eliashovdenes/Pokemon-Type-Trainer)")






