import streamlit as st
import pandas as pd
import datetime
import os
import random
import urllib.request
import string

# ---------- CONSTANTS ----------
ADMIN_PASSWORD = "letmein7787"
LOG_FILE = "hangman_log.csv"
WORD_SOURCE_URL = "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"

# ---------- LOAD WORD LIST ----------
@st.cache_data
def load_word_list():
    response = urllib.request.urlopen(WORD_SOURCE_URL)
    words = response.read().decode().splitlines()
    return [w.upper() for w in words if len(w) >= 5 and w.isalpha()]

word_list = load_word_list()

# ---------- INIT SESSION STATE ----------
if 'player_name' not in st.session_state:
    st.session_state.player_name = ""
if 'used_words' not in st.session_state:
    st.session_state.used_words = set()
if 'word' not in st.session_state:
    st.session_state.word = random.choice(word_list)
    st.session_state.used_words.add(st.session_state.word)
    st.session_state.guessed_letters = []
    st.session_state.attempts_left = 6
    st.session_state.game_over = False
    st.session_state.won = False
    st.session_state.tries = 0
if 'clicked_letter' not in st.session_state:
    st.session_state.clicked_letter = None

# ---------- FUNCTIONS ----------
def get_display_word():
    return " ".join([letter if letter in st.session_state.guessed_letters else "_" for letter in st.session_state.word])

def log_game():
    if not os.path.exists(LOG_FILE):
        df = pd.DataFrame(columns=["Name", "Word", "Tries", "Result", "Timestamp"])
        df.to_csv(LOG_FILE, index=False)

    df = pd.read_csv(LOG_FILE)
    new_entry = {
        "Name": st.session_state.player_name,
        "Word": st.session_state.word,
        "Tries": st.session_state.tries,
        "Result": "Won" if st.session_state.won else "Lost",
        "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv(LOG_FILE, index=False)

def reset_game():
    unused_words = list(set(word_list) - st.session_state.used_words)
    if not unused_words:
        st.session_state.used_words = set()
        unused_words = word_list
    new_word = random.choice(unused_words)
    st.session_state.word = new_word
    st.session_state.used_words.add(new_word)
    st.session_state.guessed_letters = []
    st.session_state.attempts_left = 6
    st.session_state.game_over = False
    st.session_state.won = False
    st.session_state.tries = 0
    st.session_state.clicked_letter = None

# ---------- LOGIN ----------
if not st.session_state.player_name:
    st.title("🎮 Hangman Game")
    st.session_state.player_name = st.text_input("Enter your name to begin:")
    st.stop()

st.title(f"🔤 Welcome {st.session_state.player_name} to Hangman!")

# ---------- DISPLAY GAME STATUS ----------
st.subheader("Guess the hidden word!")
st.markdown(f"### Word: `{get_display_word()}`")
st.markdown(f"**Attempts left**: {st.session_state.attempts_left}")
st.markdown(f"**Guessed letters**: {' '.join(st.session_state.guessed_letters)}")

# ---------- LETTER BUTTONS ----------
if not st.session_state.game_over:
    cols = st.columns(13)
    for i, letter in enumerate(string.ascii_uppercase):
        if letter in st.session_state.guessed_letters:
            cols[i % 13].button(letter, disabled=True, key=f"btn_{letter}")
        else:
            if cols[i % 13].button(letter, key=f"btn_{letter}"):
                st.session_state.clicked_letter = letter

# ---------- PROCESS CLICKED LETTER ----------
letter = st.session_state.clicked_letter
if letter and not st.session_state.game_over:
    if letter not in st.session_state.guessed_letters:
        st.session_state.guessed_letters.append(letter)
        st.session_state.tries += 1
        if letter in st.session_state.word:
            st.success(f"'{letter}' is in the word.")
        else:
            st.session_state.attempts_left -= 1
            st.error(f"'{letter}' is not in the word.")

        # Win/Loss check
        if all(l in st.session_state.guessed_letters for l in st.session_state.word):
            st.session_state.won = True
            st.session_state.game_over = True
            log_game()
        elif st.session_state.attempts_left <= 0:
            st.session_state.game_over = True
            log_game()

    st.session_state.clicked_letter = None  # reset after processing

# ---------- GAME OVER ----------
if st.session_state.game_over:
    if st.session_state.won:
        st.balloons()
        st.success(f"You won! The word was '{st.session_state.word}' 🎉")
    else:
        st.error(f"Game Over! The word was '{st.session_state.word}' 😢")

    if st.button("Play Again"):
        reset_game()

# ---------- ADMIN SECTION ----------
st.markdown("---")
st.markdown("🔐 **Admin Login**")

admin_pass = st.text_input("Enter admin password", type="password")
if admin_pass == ADMIN_PASSWORD:
    st.success("Admin access granted.")
    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
        st.dataframe(df)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Game Log", csv, "hangman_log.csv", "text/csv")
    else:
        st.info("No games played yet.")
elif admin_pass != "":
    st.error("Incorrect password.")

        st


