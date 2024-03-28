import streamlit as st

st.set_page_config(page_title="Pokemon practice!", page_icon=":monkey:", layout="wide")


pokemon_name = "Snorlax"

all_correct = False

correct_answers = {
    'generation': 'Gen 1/Kanto',  
    'typing': "Normal",   
    'secondary_typing':"No secondary type"        
}

with st.container():
    left, center, right = st.columns(3)
    with center:
            st.title("Pokemon Practice", anchor=False)
            st.write("Guess the pokemons typing and generation!")

            #name of the weapon
            # nameOfWeapon = "Weapon Name: " + pokemon_name
            # st.subheader(nameOfWeapon, anchor=False)

with st.container():
        one, two, three = st.columns(3)
        with one:
            st.subheader("Current Pokemon:", anchor=False)
            #picture
            url = "snorlax.png"
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
            generation_options = ['Choose One:', 'Gen 1/Kanto', 'Gen 2/Johto', 'Gen 3/Hoenn', 'Gen 4/Sinnoh', 'Gen 5/Unova', 'Gen 6/Kalos', 'Gen 7/Alola', 'Gen 8/Galar']
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

        st.button("Next Pokemon")





            