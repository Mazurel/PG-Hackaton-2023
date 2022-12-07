import streamlit as st

def filter_message(message: str) -> str:
    # TODO: Filtrowanie wulgaryzmów tutaj !
    return message

def show_messages(messages: list[tuple[str, str]]):
    body = '''
| Lp | Oryginalna | Przefiltrowana |
| -- | ---------- | -------------- |
'''

    for id, (msg_in, msg_filt) in enumerate(reversed(messages)):
        body += f"| {id+1} | {msg_in} | {msg_filt} |\n"

    st.markdown(body)


st.title("Filtr wulgaryzmów")

if not "messages" in st.session_state:
    st.session_state["messages"] = []

messages = st.session_state.messages

message = st.text_input("Podaj wiadomość:", value="Przykładowa wiadomość :)")
filtered_message = filter_message(message)

messages.append((message, filter_message(message)))
st.session_state.messages = messages
show_messages(messages)