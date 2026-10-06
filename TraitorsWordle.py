import hashlib
import time
from datetime import date
from pathlib import Path

import streamlit as st


# -----------------------------
# PAGE SETUP
# -----------------------------

st.set_page_config(
    page_title="Port Sunlight Traitors Wordle",
    page_icon="🟩",
    layout="centered"
)


# -----------------------------
# WORD SETTINGS
# -----------------------------

WORDS = [
    "FAIRY",
    "RINSE",
    "CLEAN",
    "SCRUB",
    "DROPS",
    "PLATE",
    "GLASS",
    "SINKS",
    "RACKS",
    "SHINE",
    "SOAKS",
    "RINSE",
    "SOILS",
    "STAIN",
    "SPOTS",
    "SHINE",
    "DROPS",
    "CYCLE",
    "STEAM",
    "CLEAR",
    ]

MAX_GUESSES = 6


# Find valid_words.txt in the same folder as this Python file
word_file = Path(__file__).parent / "valid_words.txt"

with open(word_file, "r", encoding="utf-8") as f:
    VALID_WORDS = {
        line.strip().upper()
        for line in f
        if len(line.strip()) == 5
        and line.strip().isalpha()
    }

# Make sure possible answers are always accepted
VALID_WORDS.update(WORDS)


# -----------------------------
# GAME FUNCTIONS
# -----------------------------

def get_daily_word():

    today = date.today().isoformat()

    digest = hashlib.sha256(
        today.encode("utf-8")
    ).hexdigest()

    index = int(digest, 16) % len(WORDS)

    return WORDS[index]


def get_puzzle_number():

    launch_date = date(2026, 10, 6)

    return (date.today() - launch_date).days + 1


def score_guess(guess, answer):

    result = ["absent"] * 5
    remaining = []

    # Pass 1: correct letters
    for i in range(5):

        if guess[i] == answer[i]:
            result[i] = "correct"
        else:
            remaining.append(answer[i])

    # Pass 2: present letters
    for i in range(5):

        if result[i] == "correct":
            continue

        if guess[i] in remaining:
            result[i] = "present"
            remaining.remove(guess[i])

    return result

def generate_share_text():

    output = []

    output.append(
        f"Port Sunlight Wordle #{get_puzzle_number()}"
    )

    output.append("")

    for guess, score in st.session_state.guesses:

        row = ""

        for s in score:

            if s == "correct":
                row += "🟩"

            elif s == "present":
                row += "🟨"

            else:
                row += "⬜"

        output.append(row)

    output.append("")

    output.append(
        f"{len(st.session_state.guesses)}/{MAX_GUESSES}"
    )

    if st.session_state.finish_time is not None:

        elapsed = int(
            st.session_state.finish_time
            - st.session_state.start_time
        )

        mins = elapsed // 60
        secs = elapsed % 60

        output.append(
            f"⏱️ {mins:02d}:{secs:02d}"
        )

    return "\n".join(output)

def create_board():

    board_html = '<div class="wordle-board">'

    for row in range(MAX_GUESSES):

        board_html += '<div class="wordle-row">'

        if row < len(st.session_state.guesses):

            guess, score = st.session_state.guesses[row]

            for letter, result in zip(guess, score):

                board_html += (
                    f'<div class="wordle-tile {result}">'
                    f'{letter}'
                    f'</div>'
                )

        else:

            for _ in range(5):
                board_html += (
                    '<div class="wordle-tile empty">'
                    '&nbsp;'
                    '</div>'
                )

        board_html += "</div>"

    board_html += "</div>"

    return board_html


# -----------------------------
# SESSION STATE
# -----------------------------

if "answer" not in st.session_state:
    st.session_state.answer = get_daily_word()

if "guesses" not in st.session_state:
    st.session_state.guesses = []

if "game_over" not in st.session_state:
    st.session_state.game_over = False

if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "finish_time" not in st.session_state:
    st.session_state.finish_time = None


# -----------------------------
# -------------------------

st.markdown(
    """
    <style>

    .block-container {
        max-width: 520px;
        padding-top: 1rem;
        padding-bottom: 1rem;
    }

    h1 {
        text-align: center;
        margin-top: 0;
        margin-bottom: 0.25rem;
    }

    .game-info {
        text-align: center;
        margin-bottom: 0.6rem;
        color: #555555;
    }

    .wordle-board {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 5px;
        margin: 8px auto 12px auto;
    }

    .wordle-row {
        display: flex;
        gap: 5px;
    }

    .wordle-tile {
        width: 46px;
        height: 46px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 4px;
        font-size: 24px;
        font-weight: 700;
        color: white;
        box-sizing: border-box;
    }

    .wordle-tile.empty {
        background-color: white;
        border: 2px solid #d3d6da;
        color: #333333;
    }

    .wordle-tile.correct {
        background-color: #6aaa64;
        border: 2px solid #6aaa64;
    }

    .wordle-tile.present {
        background-color: #c9b458;
        border: 2px solid #c9b458;
    }

    .wordle-tile.absent {
        background-color: #787c7e;
        border: 2px solid #787c7e;
    }

    div[data-testid="stTextInput"] {
        max-width: 300px;
        margin: auto;
    }

    div[data-testid="stFormSubmitButton"] {
        text-align: center;
    }

    div[data-testid="stFormSubmitButton"] button {
        width: 180px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# -----------------------------
# TITLE AND BOARD
# -----------------------------

st.title(
    f"Port Sunlight Wordle #{get_puzzle_number()}"
)

guesses_remaining = (
    MAX_GUESSES
    - len(st.session_state.guesses)
)

st.markdown(
    f"""
    <div class="game-info">
        Guess the five-letter word the fastest to win a shield ·
        {guesses_remaining} guesses remaining
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    create_board(),
    unsafe_allow_html=True
)


# -----------------------------
# LIVE TIMER
# -----------------------------

@st.fragment(run_every=1)
def show_timer():

    if st.session_state.start_time is None:
        elapsed = 0

    elif st.session_state.finish_time is not None:
        elapsed = (
            st.session_state.finish_time
            - st.session_state.start_time
        )

    else:
        elapsed = (
            time.time()
            - st.session_state.start_time
        )

    minutes = int(elapsed) // 60
    seconds = int(elapsed) % 60

    st.markdown(
        f"<p style='text-align:center;'>"
        f"⏱️ {minutes:02d}:{seconds:02d}"
        f"</p>",
        unsafe_allow_html=True
    )


show_timer()


# -----------------------------
# GUESS FORM
# -----------------------------

if not st.session_state.game_over:

    with st.form(
        key="guess_form",
        clear_on_submit=True
    ):

        guess = st.text_input(
            "Enter a five-letter word",
            max_chars=5,
            label_visibility="collapsed",
            placeholder="Type your guess"
        ).strip().upper()

        submitted = st.form_submit_button(
            "Submit guess",
            use_container_width=False
        )

    if submitted:

        if len(guess) != 5:
            st.error("Your guess must be exactly five letters.")

        elif not guess.isalpha():
            st.error("Please use letters only.")

        elif guess not in VALID_WORDS:
            st.error("That word is not in the word list.")

        else:

            if st.session_state.start_time is None:
                st.session_state.start_time = time.time()

            result = score_guess(
                guess,
                st.session_state.answer
            )

            st.session_state.guesses.append(
                (guess, result)
            )

            if guess == st.session_state.answer:

                st.session_state.finish_time = time.time()
                st.session_state.game_over = True

            elif (
                len(st.session_state.guesses)
                >= MAX_GUESSES
            ):

                st.session_state.finish_time = time.time()
                st.session_state.game_over = True

            st.rerun()


# -----------------------------
# FINAL RESULT
# -----------------------------

if st.session_state.game_over:

    if (
        st.session_state.guesses[-1][0]
        == st.session_state.answer
    ):

        st.success(
            f"You got it in "
            f"{len(st.session_state.guesses)} guesses!"
        )

    else:

        st.error(
            f"Out of guesses. The answer was "
            f"{st.session_state.answer}."
        )

    st.info(
        "You have completed today's puzzle. "
        "Come back tomorrow for the next word."
    )
share_text = generate_share_text()

st.code(
    share_text,
    language=None
)

st.download_button(
    "Download Result",
    share_text,
    "PortSunlightWordle.txt"
)
