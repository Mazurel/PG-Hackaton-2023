import io
from typing import TextIO
import os

import streamlit as st

from filter import censor, create_profanty_table

def get_profanity_file() -> TextIO:
    dir = os.path.dirname(__file__)
    full_path = os.path.join(dir, "dataset/curses_55k.txt")
    return io.open(full_path, mode="r", encoding="utf-8")

@st.cache()
def get_profanity_table() -> dict:
    file = get_profanity_file()
    return create_profanty_table(file)

def filter_message(message: str, prof_table: dict) -> str:
    return censor(message, prof_table)

def show_messages(messages: list[tuple[str, str]]):
    body = '''
| Lp | Oryginalna | Przefiltrowana |
| -- | ---------- | -------------- |
'''

    for id, (msg_in, msg_filt) in enumerate(reversed(messages)):
        body += f"| {id+1} | {msg_in} | {msg_filt} |\n"

    st.markdown(body)

prof_table = get_profanity_table()

st.title("Filtr wulgaryzmów")

if not "messages" in st.session_state:
    st.session_state["messages"] = []

messages = st.session_state.messages

message = st.text_input("Podaj wiadomość:", value="Przykładowa wiadomość :)")
filtered_message = filter_message(message, prof_table)

messages.append((message,
                 filtered_message))
st.session_state.messages = messages
show_messages(messages)