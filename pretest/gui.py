import io
from typing import TextIO
import os
from copy import deepcopy

import streamlit as st

from filter import censor, create_profanty_table, append_curse

def get_profanity_file() -> TextIO:
    dir = os.path.dirname(__file__)
    full_path = os.path.join(dir, "dataset/wulgaryzmy-cache.txt")
    return io.open(full_path, mode="r", encoding="utf-8")

@st.cache(persist=True)
def get_profanity_table() -> dict:
    file = get_profanity_file()
    hash = create_profanty_table(file)
    file.close()
    return hash

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

persistent_prof_table = get_profanity_table()
prof_table = deepcopy(persistent_prof_table)

st.title("Filtr wulgaryzmów")

if not "messages" in st.session_state:
    st.session_state["messages"] = []

messages = st.session_state.messages

message = st.text_input("Wiadomość do ocenzurowania", value="Przykładowa wiadomość :)")

additional_profs = st.text_area("Dodatkowe wulgaryzmy zdefiniowane przez użytkownika").split()
additional_profs = list(map(lambda word: word.strip(), additional_profs))
for prof in additional_profs:
    append_curse(prof, prof_table)

filtered_message = filter_message(message, prof_table)

st.markdown("---")

messages.append((message,
                 filtered_message))

if len(messages) > 10:
    messages = messages[-10:]

st.session_state.messages = messages
show_messages(messages)
