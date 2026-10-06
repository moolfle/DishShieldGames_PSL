import hashlib
import time
from collections import Counter
from datetime import datetime, date
from zoneinfo import ZoneInfo

import streamlit as st
from st_copy import copy_button


# --------------------------------------------------
# APP SETTINGS
# --------------------------------------------------

st.set_page_config(
    page_title="Port Sunlight Wordle",
    page_icon="🟩",
    layout="centered"
)

MAX_GUESSES = 6
WORD_LENGTH = 5

# Add as many five-letter answers as you like.
# Everyone receives the same answer on the same date.
WORDS = [
    "FAIRY",
    "RINSE",
    "CLEAN",
    "SCRUB",
    "DROPS",
    "SHINE",
    "PLATE",
    "GLASS",
    "BRUSH",
    "FOAMY",
    "WATER",
    "POWER",
    "FRESH",
    "SUDSY",
    "SPARK",
]

UK_TIMEZONE = ZoneInfo("Europe/London")


# --------------------------------------------------
# DAILY PUZZLE
# --------------------------------------------------

def get_today():
    return datetime.now(UK_TIMEZONE).date()


def get_daily_word(puzzle_date):
    """
    Selects one consistent word from the list for a given date.
    Unlike Python's built-in hash(), SHA-256 gives a stable result.
    """
    date_text = puzzle_date.isoformat()
    digest = hashlib.sha256(date_text.encode("utf-8")).hexdigest()
    word_index = int(digest, 16) % len(WORDS)
    return WORDS[word_index]


def get_puzzle_number(puzzle_date):
    """
    Puzzle numbering begins on 6 October 2026.
    """
    launch_date = date(2026, 10, 6)
    return (puzzle_date - launch_date).days + 1


# --------------------------------------------------
# WORDLE SCORING
# --------------------------------------------------
def score_guess(guess, answer):
    """
    G = correct letter in the correct position
    Y = correct letter in the wrong position
    B = letter is not present

    This also handles repeated letters correctly.
    """
    result = ["B"] * WORD_LENGTH
    remaining_letters = Counter()

    # First pass: mark letters in the correct position
    for index in range(WORD_LENGTH):
        if guess[index] == answer[index\]:
            result[index] = "G"
        else:
            remaining_letters[answer[index]] += 1

    # Second pass: mark correct letters in the wrong position
    for index in range(WORD_LENGTH):
        if result[index] == "G":
            continue

        letter = guess[index]

        if remaining_letters[letter] > 0:
            result[index] = "Y"
            remaining_letters[letter] -= 1

    return result

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

today = get_today()
daily_answer = get_daily_word(today)
puzzle_number = get_puzzle_number(today)

if "puzzle_date" not in st.session_state:
    st.session_state.puzzle_date = today

# Reset automatically when a new daily puzzle begins
if st.session_state.puzzle_date != today:
    st.session_state.clear()
    st.session_state.puzzle_date = today

if "answer" not in st.session_state:
    st.session_state.answer = daily_answer

if "guesses" not in st.session_state:
    st.session_state.guesses = []

if "scores" not in st.session_state:
    st.session_state.scores = []

if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "finish_time" not in st.session_state:
    st.session_state.finish_time = None

if "game_over" not in st.session_state:
    st.session_state.game_over = False

if "won" not in st.session_state:
    st.session_state.won = False


# --------------------------------------------------
# DISPLAY FUNCTIONS
# --------------------------------------------------

def tile_html(letter, status):
    colours = {
        "G": "#538d4e",
        "Y": "#b59f3b",
        "B": "#3a3a3c",
        "E": "#ffffff",
    }

    borders = {
        "G": "#538d4e",
        "Y": "#b59f3b",
        "B": "#3a3a3c",
        "E": "#878a8c",
    }

    text_colour = "#ffffff" if status != "E" else "#000000"

    return f"""
    <div style="
        width: 56px;
        height: 56px;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: {colours[status]};
        border: 2px solid {borders[status]};
        color: {text_colour};
        font-size: 28px;
        font-weight: 700;
        font-family: Arial, sans-serif;
        box-sizing: border-box;
    ">
        {letter}
    </div>
    """


def display_board():
    for row_number in range(MAX_GUESSES):
        columns = st.columns(
            [1, 1, 1, 1, 1],
            gap="small"
        )

        if row_number < len(st.session_state.guesses):
            guess = st.session_state.guesses[row_number]
            score = st.session_state.scores[row_number]

            for column, letter, status in zip(columns, guess, score):
                with column:
                    st.markdown(
                        tile_html(letter, status),
                        unsafe_allow_html=True
                    )
        else:
            for column in columns:
                with column:
                    st.markdown(
                        tile_html("", "E"),
                        unsafe_allow_html=True
                    )


def get_keyboard_status():
    """
    Determine the strongest known status for every letter.
    Green overrides yellow, and yellow overrides grey.
    """
    status_priority = {
        "B": 1,
        "Y": 2,
        "G": 3
    }

    keyboard_status = {}

    for guess, score in zip(
        st.session_state.guesses,
        st.session_state.scores
    ):
        for letter, status in zip(guess, score):
            old_status = keyboard_status.get(letter)

            if old_status is None:
                keyboard_status[letter] = status
            elif status_priority[status] > status_prioritykeyboard_status[letter] = status

    return keyboard_status


def keyboard_key_html(letter, status):
    colours = {
        "G": "#538d4e",
        "Y": "#b59f3b",
        "B": "#3a3a3c",
        "U": "#d3d6da",
    }

    text_colour = "#ffffff" if status in ["G", "Y", "B"] else "#000000"

    return f"""
    <span style="
        display: inline-block;
        min-width: 32px;
        margin: 3px 1px;
        padding: 9px 4px;
        border-radius: 4px;
        background-color: {colours[status]};
        color: {text_colour};
        text-align: center;
        font-family: Arial, sans-serif;
        font-size: 15px;
        font-weight: 700;
    ">
        {letter}
    </span>
    """


def display_keyboard():
    keyboard_status = get_keyboard_status()

    rows = [
        "QWERTYUIOP",
        "ASDFGHJKL",
        "ZXCVBNM"
    ]

    for row in rows:
        row_html = '<div style="text-align: center;">'

        for letter in row:
            status = keyboard_status.get(letter, "U")
            row_html += keyboard_key_html(letter, status)

        row_html += "</div>"

        st.markdown(
            row_html,
            unsafe_allow_html=True
        )


def format_elapsed_time(seconds):
    total_seconds = int(seconds)
    minutes = total_seconds // 60
    remaining_seconds = total_seconds % 60

    return f"{minutes}:{remaining_seconds:02d}"


def get_elapsed_seconds():
    if st.session_state.start_time is None:
        return 0

    end_time = (
        st.session_state.finish_time
        if st.session_state.finish_time is not None
        else time.time()
    )

    return end_time - st.session_state.start_time


def build_share_text():
    if st.session_state.won:
        result_text = (
            f"{len(st.session_state.guesses)}/{MAX_GUESSES}"
        )
    else:
        result_text = f"X/{MAX_GUESSES}"

    elapsed_text = format_elapsed_time(get_elapsed_seconds())

    lines = [
        f"Port Sunlight Wordle #{puzzle_number}",
        f"{result_text} ⏱️ {elapsed_text}",
        ""
    ]

    emoji_map = {
        "G": "🟩",
        "Y": "🟨",
        "B": "⬜"
    }

    for score in st.session_state.scores:
        lines.append(
            "".join(emoji_map[status] for status in score)
        )

    return "\n".join(lines)


# --------------------------------------------------
# GAME HEADER
# --------------------------------------------------

st.title("Port Sunlight Wordle")
st.caption(
    f"Daily puzzle #{puzzle_number} • "
    f"{today.strftime('%d %B %Y')}"
)

st.write(
    "Guess the five-letter word in six attempts. "
    "The timer starts after your first valid guess."
)


# --------------------------------------------------
# PROGRESS
# --------------------------------------------------

guesses_used = len(st.session_state.guesses)
progress_value = guesses_used / MAX_GUESSES

st.progress(
    progress_value,
    text=f"Guesses used: {guesses_used} of {MAX_GUESSES}"
)


# --------------------------------------------------
# BOARD
# --------------------------------------------------

display_board()


# --------------------------------------------------
# GUESS ENTRY
# --------------------------------------------------

if not st.session_state.game_over:

    with st.form(
        key="guess_form",
        clear_on_submit=True
    ):
        guess = st.text_input(
            "Enter your guess",
            max_chars=WORD_LENGTH,
            placeholder="Five-letter word"
        ).upper().strip()

        submitted = st.form_submit_button(
            "Submit guess",
            type="primary",
            use_container_width=True
        )

    if submitted:

        if len(guess) != WORD_LENGTH:
            st.error("Your guess must contain exactly five letters.")

        elif not guess.isalpha():
            st.error("Please use letters only.")

        else:
            # Start the timer on the first valid guess
            if st.session_state.start_time is None:
                st.session_state.start_time = time.time()

            score = score_guess(
                guess,
                st.session_state.answer
            )

            st.session_state.guesses.append(guess)
            st.session_state.scores.append(score)

            if guess == st.session_state.answer:
                st.session_state.won = True
                st.session_state.game_over = True
                st.session_state.finish_time = time.time()

            elif len(st.session_state.guesses) >= MAX_GUESSES:
                st.session_state.won = False
                st.session_state.game_over = True
                st.session_state.finish_time = time.time()

            st.rerun()


# --------------------------------------------------
# KEYBOARD
# --------------------------------------------------

st.subheader("Keyboard")
display_keyboard()


# --------------------------------------------------
# TIMER
# --------------------------------------------------

if st.session_state.start_time is None:
    st.info("The timer will begin when you submit your first valid guess.")
else:
    elapsed_time = format_elapsed_time(get_elapsed_seconds())
    st.metric("Time since first guess", elapsed_time)


# --------------------------------------------------
# END-OF-GAME RESULT
# --------------------------------------------------

if st.session_state.game_over:

    elapsed_time = format_elapsed_time(get_elapsed_seconds())

    if st.session_state.won:
        st.success(
            f"You solved it in "
            f"{len(st.session_state.guesses)} guesses "
            f"and {elapsed_time}."
        )
    else:
        st.error(
            f"Out of guesses. The answer was "
            f"{st.session_state.answer}."
        )

    st.subheader("Share your result")

    share_text = build_share_text()

    st.code(
        share_text,
        language=None
    )

    copy_button(
        share_text,
        tooltip="Copy result",
        copied_label="Copied!",
        icon="st",
        key="copy_result"
    )
