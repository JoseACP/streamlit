from openai import OpenAI
import streamlit as st
import shelve


st.title("Generador de Copies y Tags para Instagram")

USER_AVATAR = "👤"
BOT_AVATAR = "🤖"
client = OpenAI(api_key="sk-99ffecb9e5ff4cfe9ce0960adfff9a56", base_url="https://api.deepseek.com")

# Instrucción de sistema para dar contexto
SYSTEM_PROMPT = (
    "Eres un experto en marketing digital. "
    "Tu tarea es generar únicamente copies atractivos y hashtags relevantes para publicaciones de Instagram, "
    "basándote en el mensaje del usuario. "
    "Responde siempre en el siguiente formato:\n\n"
    "Copy:\n<copy aquí>\n\nTags:\n#tag1 #tag2 #tag3"
)

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "deepseek-reasoner"

def load_chat_history():
    with shelve.open("chat_history") as db:
        return db.get("messages", [])

def save_chat_history(messages):
    with shelve.open("chat_history") as db:
        db["messages"] = messages

if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

with st.sidebar:
    if st.button("Borrar el historial"):
        st.session_state.messages = []
        save_chat_history([])

# Mostrar historial
for message in st.session_state.messages:
    avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Interfaz principal
if prompt := st.chat_input("Describe tu publicación o idea para Instagram"):
    # Añadir mensaje de sistema solo al inicio de la conversación
    if not any(msg["role"] == "system" for msg in st.session_state.messages):
        st.session_state.messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        message_placeholder = st.empty()
        full_response = ""
        for response in client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=st.session_state["messages"],
            stream=True,
        ):
            full_response += response.choices[0].delta.content or ""
            message_placeholder.markdown(full_response + "|")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})

save_chat_history(st.session_state.messages)