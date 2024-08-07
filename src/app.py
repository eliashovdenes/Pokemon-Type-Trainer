import streamlit as st
import random 
import sqlite3
import pandas as pd
import hashlib
import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv
from streamlit_cookies_manager import EncryptedCookieManager
from datetime import datetime ,timedelta
import subprocess
import calendar

# Set the page title and page icon
st.set_page_config(page_title="Pokemon type trainer!", page_icon="../pictures/logo2.png", layout="wide")

# Initialize separate random generators
daily_rng = random.Random()
normal_rng = random

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
    if st.session_state["current_streak"]>0:
        st.toast("Streak lost! :fire:")

# Initialize daily challenge completion in cookies
if 'daily_challenge_date' not in cookies:
    cookies['daily_challenge_date'] = ''

if 'daily_challenge_score' not in cookies:
    cookies['daily_challenge_score'] = '0'

# Initialize session state if not already done
if 'daily_challenge_active' not in st.session_state:
    st.session_state['daily_challenge_active'] = False
if 'daily_challenge' not in st.session_state:
    st.session_state['daily_challenge'] = {
        'completed': False,
        'score': 0,
        'current_index': 0,
        'guesses': []
    }

@st.cache_data
def fetch_pokemon_by_name(pokemon_name):
    conn = sqlite3.connect('pokemon.db')
    c = conn.cursor()
    c.execute('SELECT * FROM pokemon WHERE name = ?', (pokemon_name,))
    pokemon = c.fetchone()
    conn.close()
    return pokemon

# Fetch today's date
today_date = datetime.now().strftime('%Y-%m-%d')

# Check if the user has already completed the daily challenge today
daily_challenge_completed_today = cookies.get('daily_challenge_date') == today_date

# Saving the highest streak to database
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
                subprocess.Popen(["python", "discord_bot_streak.py"])
        else:
            c.execute('INSERT INTO user_scores (user_id, highest_streak) VALUES (%s, %s)', (user_id, new_streak))
        conn.commit()
    finally:
        release_db_connection(conn)

# Function to save the daily score only if it doesn't already exist for the same day
def save_daily_score(user_id, score_date, daily_score):
    current_date = datetime.now().date()

    # Convert score_date to a datetime.date object if it's a string
    if isinstance(score_date, str):
        score_date = datetime.strptime(score_date, "%Y-%m-%d").date()
    
    if score_date == current_date:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        try:
            # Check if a score already exists for the user on the given date
            cur.execute("""
                SELECT 1 FROM user_daily_scores
                WHERE user_id = %s AND score_date = %s;
            """, (user_id, score_date))
            result = cur.fetchone()
            
            if result is None:
                # No existing score for this user and date, proceed to insert the new score
                cur.execute("""
                    INSERT INTO user_daily_scores (user_id, score_date, daily_score)
                    VALUES (%s, %s, %s);
                """, (user_id, score_date, daily_score))
                conn.commit()
                # Run the discord bot script
                subprocess.Popen(["python", "discord_bot_daily.py"])
                print("\n \n \n")
                print("running daily bot")
                print("\n \n \n")
            else:
                print(f"Score for user_id {user_id} on {score_date} already exists.")
        finally:
            cur.close()
            conn.close()
    else:
        print(f"Attempted to save a score for a different date: {score_date}. Current date is {current_date}.")
        

def wipe_daily_scores():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM user_daily_scores")
        conn.commit()
    finally:
        cur.close()
        conn.close()

def display_streak():
    st.write(f"🔥 Your current streak: {st.session_state['current_streak']}")
    st.write(f"🔥 Your highest streak: {st.session_state['highest_streak']}")
    if st.session_state['logged_in']:
            current_user_id = st.session_state['user_id']
            update_highest_streak(current_user_id, st.session_state['highest_streak'])

# Function to set all the answers to the correct answers
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

listOfActiveGensNum = [gen for gen in range(1, 10) if st.session_state[f'gen{gen}']]

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

    # Shuffle the names
    random.shuffle(names)
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
        'name_guess_bool': False,
        'non_random_mode': False,  # Add non-random mode to session state
        'pokemon_index': 0,         # Add a Pokémon index to session state
        'start_generation': None,   # Add a starting generation to session state
        'start_pokemon': '',        # Add a starting Pokémon name to session state
        'start_pokemon_id': None,   # Add a starting Pokémon ID to session state
        'available_pokemons': []    # Add available Pokémon list to session state
    }
    for key, value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

def get_daily_pokemon():
    today = datetime.now().date()
    daily_rng.seed(today.toordinal())
    daily_pokemon_ids = daily_rng.sample(range(1, 1026), 10)  # Assuming there are 1025 Pokémon
    return daily_pokemon_ids

def toggle_daily_challenge():
    st.session_state['daily_challenge_active'] = True
    st.session_state['daily_challenge'] = {
        'completed': False,
        'score': 0,
        'current_index': 0,
        'guesses': get_daily_pokemon(),
        'results': []  # Initialize results list
    }

# Ensure 'results' key is initialized if the daily challenge is already active
if 'daily_challenge' in st.session_state and 'results' not in st.session_state['daily_challenge']:
    st.session_state['daily_challenge']['results'] = []

# Function to fetch a Pokémon from the database
@st.cache_data
def fetch_pokemon(pokemon_id):
    conn = sqlite3.connect('pokemon.db')
    c = conn.cursor()
    c.execute('SELECT id, name, generation, primary_type, secondary_type, image_url FROM pokemon WHERE id = ?', (pokemon_id,))
    pokemon = c.fetchone()
    conn.close()
    return pokemon

@st.cache_data
def fetch_pokemon_by_generation(generation):
    conn = sqlite3.connect('pokemon.db')
    c = conn.cursor()
    gen_range = gen_id_ranges[generation]
    c.execute('SELECT id, name FROM pokemon WHERE id BETWEEN ? AND ?', gen_range)
    pokemons = [(row[0], row[1]) for row in c.fetchall()]
    conn.close()
    return pokemons

def fetch_pokemon_id_by_name(pokemon_name):
    conn = sqlite3.connect('pokemon.db')
    c = conn.cursor()
    c.execute('SELECT id FROM pokemon WHERE name = ?', (pokemon_name,))
    pokemon_id = c.fetchone()
    conn.close()
    return pokemon_id[0] if pokemon_id else None

def new_pokemon():
    st.session_state['show_answer_pressed'] = False
    listOfActiveGens = [gen_id_ranges[gen] for gen in range(1, 10) if st.session_state[f'gen{gen}']]
    if not listOfActiveGens:
        listOfActiveGens = [(1, 1025)]
    if st.session_state['non_random_mode']:
        if st.session_state['start_pokemon_id'] is not None:
            st.session_state['current_pokemon_id'] = st.session_state['start_pokemon_id'] + st.session_state['pokemon_index']
            
            numbers = [num for num, _ in st.session_state['available_pokemons'] if isinstance(num, int)]
            
            
            if st.session_state['current_pokemon_id'] not in numbers:
                print("Id not in gen")
                st.session_state['start_pokemon_id'] = st.session_state['available_pokemons'][0][0]
                st.session_state['pokemon_index'] = 0
                st.session_state['current_pokemon_id'] = st.session_state['start_pokemon_id'] + st.session_state['pokemon_index']

            st.session_state['pokemon_index'] += 1
        else:
            st.error("Please select a valid starting Pokémon.")
    else:
        randGen = normal_rng.choice(listOfActiveGens)
        random_id = normal_rng.randint(randGen[0], randGen[1])
        st.session_state['current_pokemon_id'] = random_id

if 'current_pokemon_id' not in st.session_state or not st.session_state.get('current_pokemon_id'):
    if st.session_state['daily_challenge_active']:
        st.session_state['current_pokemon_id'] = st.session_state['daily_challenge']['guesses'][0]
    else:
        new_pokemon()

if 'current_pokemon_id' in st.session_state:
    pokemon = fetch_pokemon(st.session_state['current_pokemon_id'])
    if not pokemon:
        st.error("Failed to fetch Pokémon data. Please check the Pokémon ID and database connection.")
        st.stop()

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
    try:
        daily_score = int(cookies.get('daily_challenge_score', '0'))
        print("Could get daily score from cookies")
    except ValueError:
        daily_score = 0
        print("Could not get daily score from cookies")

    st.caption(f"****Logged in as {cookies.get('username')}****")
else:
    st.caption("Login to use all features")

tab1, tab2, leaderboard, account, tab3, tab4 = st.tabs(["PokeTyper", "Streak", "Leaderboard", "Account", "Options", "About"])

with account:
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

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    left, right = st.columns(2)

    with right:
        if not st.session_state['logged_in']:
            st.write("Not registered?")

        with st.expander("Sign up now"):
            if not st.session_state['logged_in']:
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

with leaderboard:
    if not st.session_state['logged_in']:
        st.write("To view and participate in the leaderboard, please log in to your account. Go to the account page to log in or sign up.")

    if st.session_state['logged_in']:
        left, right, bin = st.columns([2,2,2])
        with left:
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
                        LIMIT 30
                    ''')
                    leaderboard = c.fetchall()
                    leaderboard_df = pd.DataFrame(leaderboard, columns=["Username", "Highest Streak"])
                    leaderboard_df["Rank"] = leaderboard_df.index + 1
                    leaderboard_df = leaderboard_df[["Rank", "Username", "Highest Streak"]]
                    return leaderboard_df
                finally:
                    release_db_connection(conn)

            st.subheader("Highest Streak", anchor=False)
            leaderboard_df = fetch_leaderboard()

            leaderboard_df["Highest Streak"] = leaderboard_df.apply(
                lambda row: f"{row['Highest Streak']} 🥇" if row['Rank'] == 1 else f"{row['Highest Streak']} 🔥", axis=1
            )

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
                    "Highest Streak": st.column_config.TextColumn("Highest Streak"),
                },
                hide_index=True,
            )

        with right:
            @st.cache_data(ttl=60)  # Cache for 60 seconds
            def fetch_daily_leaderboard():
                conn = get_db_connection()
                try:
                    c = conn.cursor()
                    c.execute('''
                        SELECT u.username, ds.daily_score
                        FROM user_daily_scores ds
                        JOIN users u ON ds.user_id = u.user_id
                        WHERE ds.score_date = CURRENT_DATE
                        ORDER BY ds.daily_score DESC
                        LIMIT 30
                    ''')
                    leaderboard = c.fetchall()
                    leaderboard_df = pd.DataFrame(leaderboard, columns=["Username", "Daily Score"])
                    leaderboard_df["Rank"] = leaderboard_df.index + 1
                    leaderboard_df = leaderboard_df[["Rank", "Username", "Daily Score"]]
                    return leaderboard_df
                finally:
                    release_db_connection(conn)

            st.subheader("Daily Score", anchor=False)
            daily_leaderboard_df = fetch_daily_leaderboard()

            daily_leaderboard_df["Daily Score"] = daily_leaderboard_df.apply(
                lambda row: f"{row['Daily Score']} 🥇" if row['Rank'] == 1 else f"{row['Daily Score']} 😎", axis=1
            )

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
                daily_leaderboard_df,
                column_config={
                    "Rank": "Rank",
                    "Username": "Username",
                    "Daily Score": st.column_config.TextColumn("Daily Score"),
                },
                hide_index=True,
            )


            @st.cache_data(ttl=60)  # Cache for 60 seconds
            def fetch_monthly_leaderboard():
                conn = get_db_connection()
                try:
                    c = conn.cursor()
                    # Get the first and last date of the current month
                    today = datetime.today()
                    first_day_of_month = today.replace(day=1).date()
                    last_day_of_month = datetime(today.year, today.month, calendar.monthrange(today.year, today.month)[1]).date()
                    
                    c.execute('''
                        SELECT u.username, SUM(ds.daily_score) AS total_score
                        FROM user_daily_scores ds
                        JOIN users u ON ds.user_id = u.user_id
                        WHERE ds.score_date BETWEEN %s AND %s
                        GROUP BY u.username
                        ORDER BY total_score DESC
                        LIMIT 30
                    ''', (first_day_of_month, last_day_of_month))
                    
                    leaderboard = c.fetchall()
                    leaderboard_df = pd.DataFrame(leaderboard, columns=["Username", "Total Score"])
                    leaderboard_df["Rank"] = leaderboard_df.index + 1
                    leaderboard_df = leaderboard_df[["Rank", "Username", "Total Score"]]
                    return leaderboard_df
                finally:
                    release_db_connection(conn)
        with bin:
            # Display monthly leaderboard
            st.subheader("This Month's Daily Total Scores", anchor=False)
            monthly_leaderboard_df = fetch_monthly_leaderboard()

            monthly_leaderboard_df["Total Score"] = monthly_leaderboard_df.apply(
                lambda row: f"{row['Total Score']} 🥇" if row['Rank'] == 1 else f"{row['Total Score']} 😎", axis=1
            )

            st.dataframe(
                monthly_leaderboard_df,
                column_config={
                    "Rank": "Rank",
                    "Username": "Username",
                    "Total Score": st.column_config.TextColumn("Total Score"),
                },
                hide_index=True,
            )



            

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

        st.subheader("Modes", anchor=False)

        st.checkbox("Non-Random Mode", value=st.session_state['non_random_mode'], key='non_random_mode')
        
        if st.session_state['non_random_mode']:
            # Set default generation if not selected
            st.write("You have to set a Start pokemon to use this feature")
            if 'start_generation' not in st.session_state or not st.session_state['start_generation']:
                st.session_state['start_generation'] = 'Gen 1/Kanto'
            
            selected_generation = st.selectbox("Select a Generation:", [f'Gen {gen}/' + region for gen, region in zip(range(1, 10), ["Kanto", "Johto", "Hoenn", "Sinnoh", "Unova", "Kalos", "Alola", "Galar", "Paldea"])], index=0, key='start_generation')
            selected_gen = int(selected_generation.split('/')[0].split()[1])
            st.session_state['available_pokemons'] = fetch_pokemon_by_generation(selected_gen)
            
            # Set default starting Pokémon if not selected
            if 'start_pokemon' not in st.session_state or not st.session_state['start_pokemon']:
                st.session_state['start_pokemon'] = st.session_state['available_pokemons'][0][1]

            
            
            pokemon_options = [f"{name} (#{pokedex_id})" for pokedex_id, name in st.session_state['available_pokemons']]
            st.write(f"Generation {selected_gen} starts at #{gen_id_ranges[selected_gen][0]} and ends at #{gen_id_ranges[selected_gen][1]}")
            st.session_state['start_pokemon'] = st.selectbox("Select a starting Pokémon:", pokemon_options, index=0, key='start_pokemon_name')
            if st.button("Set Start Pokémon"):
                start_pokemon_index = pokemon_options.index(st.session_state['start_pokemon'])
                start_pokemon_id = st.session_state['available_pokemons'][start_pokemon_index][0]
                if start_pokemon_id:
                    st.session_state['start_pokemon_id'] = start_pokemon_id
                    st.session_state['pokemon_index'] = 0
                    st.success(f"Starting Pokémon set to {st.session_state['start_pokemon']}")
                    new_pokemon()
                    st.rerun()
                else:
                    st.error("Failed to set the starting Pokémon. Please select a valid Pokémon.")

            
            

        

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

with tab1:

    if st.session_state['non_random_mode']:
        st.write(f"Generation {selected_gen} starts at #{gen_id_ranges[selected_gen][0]} and ends at #{gen_id_ranges[selected_gen][1]}")
    if st.session_state['logged_in']:
        
            daily_challenge_toggle = st.checkbox(
                "Enable Daily Challenge",
                value=st.session_state['daily_challenge_active'],
                key="daily_challenge_toggle",
                on_change=toggle_daily_challenge,
                disabled=st.session_state['daily_challenge_active']
            )
    else:
        st.write("You must be logged in to enable the daily challenge.")

    if st.session_state['daily_challenge_active']:
        daily_pokemon_ids = st.session_state['daily_challenge']['guesses']
        current_index = st.session_state['daily_challenge']['current_index']
        if current_index <= len(daily_pokemon_ids):
            if current_index == len(daily_pokemon_ids):
                num_pokemon = len(st.session_state['daily_challenge']['results'])
                cols = st.columns(1)

                for i in range(num_pokemon):
                    result = st.session_state['daily_challenge']['results'][i]
                    pokemon_name, user_gen, correct_gen, user_primary, correct_primary, user_secondary, correct_secondary, user_name = result
                    pokemon = fetch_pokemon_by_name(pokemon_name)
                    image_url = pokemon[5]  # Assuming image_url is at index 5

                    with cols[i % 1]:
                        left, right, third = st.columns(3)
                        with left:
                            st.image(image_url, caption=pokemon_name, width=100)
                            hide_img_fs = '<style>button[title="View fullscreen"]{visibility: hidden;}</style>'
                            st.markdown(hide_img_fs, unsafe_allow_html=True)

                        with right:
                            all_correct = all([
                                user_gen == correct_gen,
                                user_primary == correct_primary and user_secondary == correct_secondary or user_primary == correct_secondary and user_secondary == correct_primary,
                                user_name == pokemon_name
                            ])
                            if all_correct:
                                st.write("✅")
                            else:
                                st.write("❌")

                        with right:
                            if correct_secondary == "No secondary type" and user_secondary == "No secondary type":
                                correcttyping = correct_primary
                                usertyping = user_primary
                                results_df = pd.DataFrame({
                                    "Your Guess": [user_gen, usertyping, user_name],
                                    "Correct Answer": [correct_gen, correcttyping, pokemon_name],
                                    "Result": [
                                        "✅" if user_gen == correct_gen else "❌",
                                        "✅" if usertyping == correcttyping else "❌",
                                        "✅" if user_name == pokemon_name else "❌"
                                    ]
                                })
                            elif user_secondary == "No secondary type" and correct_secondary != "No secondary type":
                                correcttyping = f"{correct_primary}/{correct_secondary}"
                                usertyping = user_primary
                                results_df = pd.DataFrame({
                                    "Your Guess": [user_gen, usertyping, user_name],
                                    "Correct Answer": [correct_gen, correcttyping, pokemon_name],
                                    "Result": [
                                        "✅" if user_gen == correct_gen else "❌",
                                        "✅" if usertyping == correcttyping else "❌",
                                        "✅" if user_name == pokemon_name else "❌"
                                    ]
                                })
                            elif user_secondary != "No secondary type" and correct_secondary == "No secondary type":
                                correcttyping = correct_primary
                                usertyping = f"{user_primary}/{user_secondary}"
                                results_df = pd.DataFrame({
                                    "Your Guess": [user_gen, usertyping, user_name],
                                    "Correct Answer": [correct_gen, correcttyping, pokemon_name],
                                    "Result": [
                                        "✅" if user_gen == correct_gen else "❌",
                                        "✅" if usertyping == correcttyping else "❌",
                                        "✅" if user_name == pokemon_name else "❌"
                                    ]
                                })
                            elif user_secondary != "No secondary type" and correct_secondary != "No secondary type":
                                correcttyping = f"{correct_primary}/{correct_secondary}"
                                usertyping = f"{user_primary}/{user_secondary}"
                                userttypingmirror = f"{user_secondary}/{user_primary}"
                                results_df = pd.DataFrame({
                                    "Your Guess": [user_gen, usertyping, user_name],
                                    "Correct Answer": [correct_gen, correcttyping, pokemon_name],
                                    "Result": [
                                        "✅" if user_gen == correct_gen else "❌",
                                        "✅" if usertyping == correcttyping or userttypingmirror == correcttyping else "❌",
                                        "✅" if user_name.lower().strip() == pokemon_name.lower().strip() else "❌"
                                    ]
                                })
                            st.dataframe(results_df, hide_index=True, use_container_width=True)

                        st.divider()

                st.write(f"Score: {st.session_state['daily_challenge']['score']}/30")
                
                if not daily_challenge_completed_today:
                    save_daily_score(st.session_state['user_id'], today_date, st.session_state['daily_challenge']['score'])
                if st.button("Continue"):
                    st.session_state['daily_challenge']['current_index'] += 1
                    st.session_state['daily_challenge_active'] = False
                    new_pokemon()
                    st.rerun()
            else:
                pokemon_id = daily_pokemon_ids[current_index]
                pokemon = fetch_pokemon(pokemon_id)
                if pokemon:
                    pokemon_name, generation, primary_type, secondary_type, image_url = pokemon[1:6]
                    one, two, three = st.columns([3, 2, 3])
                    with one:
                        st.subheader("Current Pokemon:", anchor=False)
                        st.image(image_url, width=300, caption=f"")
                        hide_img_fs = '<style>button[title="View fullscreen"]{visibility: hidden;}</style>'
                        st.markdown(hide_img_fs, unsafe_allow_html=True)
                        st.write(f"{current_index + 1}/10")
                    with two:
                        selected_generation = st.selectbox(
                            "Select the generation:", 
                            ['Choose One:', 'Gen 1/Kanto', 'Gen 2/Johto', 'Gen 3/Hoenn', 'Gen 4/Sinnoh', 'Gen 5/Unova', 'Gen 6/Kalos', 'Gen 7/Alola', 'Gen 8/Galar', 'Gen 9/Paldea'], 
                            index=0, 
                            key='daily_guess_generation'
                        )
                    with three:
                        left, right = st.columns(2)
                        with left:
                            selected_typing = st.selectbox(
                                "Select the primary typing:", 
                                ['Choose One:', 'Normal', 'Fire', 'Water', 'Electric', 'Grass', 'Ice', 'Fighting', 'Poison', 'Ground', 'Flying', 'Psychic', 'Bug', 'Rock', 'Ghost', 'Dragon', 'Dark', 'Steel', 'Fairy'], 
                                index=0, 
                                key='daily_guess_typing'
                            )
                        with right:
                            selected_typing2 = st.selectbox(
                                "Select the secondary typing:", 
                                ['No secondary type', 'Normal', 'Fire', 'Water', 'Electric', 'Grass', 'Ice', 'Fighting', 'Poison', 'Ground', 'Flying', 'Psychic', 'Bug', 'Rock', 'Ghost', 'Dragon', 'Dark', 'Steel', 'Fairy'], 
                                index=0, 
                                key='daily_guess_typing2'
                            )
                    with three:
                        name_guess = st.selectbox("Guess the name of the Pokémon:",listOfPokemonNames, key='daily_name_guess')

                    if st.button(f"Submit guess for Pokemon {st.session_state['daily_challenge']['current_index'] + 1}"):
                        all_correct = all([
                            selected_generation == generation,
                            (selected_typing == primary_type and selected_typing2 == secondary_type) or (selected_typing == secondary_type and selected_typing2 == primary_type),
                            name_guess.lower().strip() == pokemon_name.lower().strip()
                        ])
                        if selected_generation == generation:
                            st.session_state['daily_challenge']['score'] += 1
                        if (selected_typing == primary_type and selected_typing2 == secondary_type) or (selected_typing == secondary_type and selected_typing2 == primary_type):
                            st.session_state['daily_challenge']['score'] += 1
                        if name_guess.lower().strip() == pokemon_name.lower().strip():
                            st.session_state['daily_challenge']['score'] += 1
                            
                        st.session_state['daily_challenge']['results'].append([
                            pokemon_name, selected_generation, generation, selected_typing, primary_type, selected_typing2, secondary_type, name_guess
                        ])

                        st.session_state['daily_challenge']['current_index'] += 1
                        if st.session_state['daily_challenge']['current_index'] < len(daily_pokemon_ids):
                            st.session_state['current_pokemon_id'] = daily_pokemon_ids[st.session_state['daily_challenge']['current_index']]
                        st.rerun()


        else:
            cookies['daily_challenge_date'] = today_date
            cookies['daily_challenge_score'] = str(st.session_state['daily_challenge']['score'])
            cookies.save()
            st.session_state['daily_challenge']['completed'] = True
            st.session_state['daily_challenge_active'] = False
            new_pokemon()
            st.rerun()

    if not st.session_state['daily_challenge_active']:
        one, two, three = st.columns([3, 2, 3])
        pokename = pokemon_name if not st.session_state['guess_name'] else ""
        with one:
            st.subheader("Current Pokemon:", anchor=False)
            if st.session_state['non_random_mode']:
                caption_text = f"{pokename} (#{st.session_state['current_pokemon_id']})"
            else:
                caption_text = pokename
            
            st.image(image_url, width=300, caption=caption_text)
            
            hide_img_fs = '<style>button[title="View fullscreen"]{visibility: hidden;}</style>'
            st.markdown(hide_img_fs, unsafe_allow_html=True)
        with two:
            if st.session_state['non_random_mode']:
                selected_gen_region = generation.split('/')  # Split the generation string into number and region
                if len(selected_gen_region) == 2:
                    selected_gen = ''.join(filter(str.isdigit, selected_gen_region[0]))  # Extract the generation number safely
                    region_name = selected_gen_region[1]
                    if selected_gen.isdigit():
                        selected_gen = int(selected_gen)
                        st.session_state['generation_selection'] = f'Gen {selected_gen}/{region_name}'
                        st.session_state['generation_correct'] = True 
                    else:
                        st.error("Invalid generation format")
                else:
                    st.error("Invalid generation format")

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
                        st.session_state.typing_selection = st.session_state.typing_selection
                        st.session_state.typing_selection2 = st.session_state.typing_selection2
                        st.rerun()
                    else:
                        st.error("Incorrect. Try again.")
                        if st.session_state["current_streak"] > 0:
                            st.toast("Streak lost! :fire: ")
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
                        if st.session_state["current_streak"] > 0:
                            st.toast("Streak lost! :fire: ")
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
    left, bin, right = st.columns([1, 5, 1])
    with left:
        with st.container():
            if st.session_state["guess_name"] == True:
                if st.session_state.get('generation_correct') and st.session_state.get('typing_correct') and st.session_state.get('name_guess_bool'):
                    st.session_state["answer_button"] = False
                    if not st.session_state["daily_challenge_active"]:
                        if st.button("Next Pokemon", on_click=reset):
                            st.session_state["answer_button"] = True
                            st.session_state['current_streak'] -= 1
                            if st.session_state["increased_high"] == True:
                                st.session_state['highest_streak'] = st.session_state['highest_streak'] - 1
                                st.session_state["increased_high"] = False
                            if st.session_state['current_streak'] < 0:
                                st.session_state['current_streak'] = 0
                            new_pokemon()
                            st.session_state['generation_correct'] = False
                            st.session_state['typing_correct'] = False
                            st.session_state['correct_guess_made'] = True
                            st.session_state['name_guess_bool'] = False
                            st.rerun()
            else:
                if st.session_state.get('generation_correct') and st.session_state.get('typing_correct'):
                    if st.session_state.get("show_answer_pressed") == False and len(listOfActiveGensNum) == 9 and st.session_state['correct_guess_made'] == True and not st.session_state['non_random_mode'] and not st.session_state['daily_challenge_active']:
                        st.session_state['current_streak'] += 1
                        st.toast("Streak increased! :tada: Current streak: " + str(st.session_state['current_streak']))
                        if st.session_state['current_streak'] > st.session_state['highest_streak']:
                            st.session_state['highest_streak'] = st.session_state['current_streak']
                            st.session_state['increased_high'] = True
                    else:
                        if st.session_state['prev_streak'] > 0:
                            st.toast("Streak lost! :fire: ")                   
                        elif st.session_state['current_streak'] > 0:
                            st.toast("Streak lost! :fire:")
                        st.session_state['current_streak'] = 0
                        st.session_state['prev_streak'] = 0            
                    st.session_state["answer_button"] = False
                    if not st.session_state["daily_challenge_active"]:
                        if st.button("Next Pokemon", on_click=reset):
                            st.session_state["answer_button"] = True
                            st.session_state['current_streak'] -= 1
                            if st.session_state["increased_high"] == True:
                                st.session_state['highest_streak'] = st.session_state['highest_streak'] - 1
                                st.session_state["increased_high"] = False
                            if st.session_state['current_streak'] < 0:
                                st.session_state['current_streak'] = 0
                            new_pokemon()
                    
                            st.session_state['generation_correct'] = False
                            st.session_state['typing_correct'] = False
                            st.session_state['correct_guess_made'] = True
                            st.session_state['name_guess_bool'] = False
                            st.rerun()
    
    with right:
        with st.container():
            if st.session_state.get("answer_button", True):
                if not st.session_state["daily_challenge_active"]:
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
    if not st.session_state["daily_challenge_active"]:
        if len(listOfActiveGensNum) != 9:
            st.markdown(" Enable all generations to gain streak :exclamation:")
        if st.session_state["guess_name"]:
            st.markdown(" Disable name guessing to gain streak :exclamation:")

        if st.session_state["non_random_mode"]:
            st.markdown("Disable non-random mode to gain streak :exclamation:")

with tab4:
    left, center, right = st.columns([1, 1, 1])
    with left:
        with st.expander(f"**What is this?**"):
            st.write(f"**Welcome to the PokeTyper!**")
            st.markdown("Select the generation and type (both primary and secondary) from the dropdown menus. Click on 'Check Generation' and 'Check Typing' to see if your guesses are correct. If you have enabled 'Guess the name' mode, you can also try to guess the name of the Pokémon.")
            st.write("")
            st.write(f"**Daily Challenge**")
            st.markdown("Log in to participate in the daily challenge. Each day, you get a set of 10 Pokémon to guess. Your scores for the daily challenge are saved and can be viewed on the leaderboard. Once you've completed the challenge, your score will be saved for that day.")
            st.write("")
            st.write(f"**Streaks**")
            st.markdown("You can build a streak by continuously guessing correctly on the first try. Your current streak and highest streak are displayed in the 'Streak' tab.")
            st.write("")
            st.write(f"**Leaderboards**")
            st.markdown("The 'Leaderboard' tab shows the highest streaks and daily scores of all users. Compete with others to see who knows the most about Pokémon!!")
            st.write("")

            st.write(f"**Account management**")
            st.markdown("In the 'Account' tab you can create an account, log in, and save your progress.")
            st.write("")

            st.write(f"**Non-Random Mode**")
            st.markdown("In the 'Options' tab, you can enable 'Non-Random Mode' to start with a specific Pokémon and proceed sequentially. Select the starting generation and the specific Pokémon to start from. This mode is helpful for structured learning through the Pokédex.")
            st.write("")

            st.write(f"**Options Customization**")
            st.markdown("In the 'Options' tab, enable or disable specific generations, toggle the non-random mode and toggle the guess the name option.")
            st.write("")
        with st.expander(f"**Inspiration**"):
            st.markdown("I made this site to train for sites such as Pokedoku. On Pokedoku, it is crucial to know the typing and generation of Pokémon. That is why I wanted to make a site where you could guess the generation, typing, and name of a Pokémon. Try it out: [Pokedoku](https://pokedoku.com)")
        with st.expander(f"**Credits**"):
            st.markdown("Made by [Elias Hovdenes](https://github.com/eliashovdenes/Pokemon-Type-Trainer)")
