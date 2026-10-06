import streamlit as st
import random

WORDS = [
    "FAIRY",
    "RINSE",
    "CLEAN",
    "SCRUB",
    "DROPS"
]

if "target" not in st.session_state:
    st.session_state.target = random.choice(WORDS)

st.title("Port Sunlight Wordle")

guess = st.text_input(
    "Enter a 5 letter word"
).upper()

if st.button("Guess"):

    if len(guess) != 5:
        st.error("Must be 5 letters")

    else:

        result = ""

        for i in range(5):

            if guess[i] == st.session_state.target[i]:
                result += "🟩"

            elif guess[i] in st.session_state.target:
                result += "🟨"

            else:
                result += "⬜"

        st.write(result)

        if guess == st.session_state.target:
            st.success("You got it!")
