# COMANDO PARA RODAR: streamlit run chatbot.py

import secrets

import streamlit as st
from groq import Groq

modelo_ia = Groq(api_key=st.secrets["groq_api_key"])  # ← corrigido para usar secrets
st.write("# CHATBOT COM IA")

# INICIALIZA A LISTA DE MENSAGENS
if "list_mensagens" not in st.session_state:
    st.session_state["list_mensagens"] = []

# MOSTRA O HISTÓRICO DE MENSAGENS
for mensagem in st.session_state["list_mensagens"]:
    role = mensagem["role"]
    content = mensagem["content"]
    st.chat_message(role).write(content)  # ← era mensagens[content] (errado)

# INPUT DO USUÁRIO
texto_usuario = st.chat_input("O que quer saber hoje?")
st.file_uploader("Envie um arquivo para a IA analisar")

# SÓ PROCESSA SE O USUÁRIO ENVIOU ALGO
if texto_usuario:

    # 1. MOSTRA E SALVA A MENSAGEM DO USUÁRIO
    st.chat_message("user").write(texto_usuario)
    mensagem_usuario = {"role": "user", "content": texto_usuario}
    st.session_state["list_mensagens"].append(mensagem_usuario)  # ← typo corrigido

    # 2. ENVIA PARA A IA E PEGA A RESPOSTA (ordem correta!)
    resposta_ia = modelo_ia.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=st.session_state["list_mensagens"]
    )

    # 3. MOSTRA E SALVA A RESPOSTA DA IA
    # Extrai a resposta da IA do objeto resposta_ia e armazena em texto_resposta_ia
    texto_resposta_ia = resposta_ia.choices[0].message.content  
    # Escreve a resposta da IA na interface do usuário, utilizando o componente st.chat_message
    st.chat_message("assistant").write(texto_resposta_ia)
    # Cria um dicionário que representa a mensagem da IA, com o papel ("role") e o conteúdo ("content")
    mensagem_ia = {"role": "assistant", "content": texto_resposta_ia}
    # Adiciona a mensagem da IA à lista de mensagens armazenada na sessão do usuário
    st.session_state["list_mensagens"].append(mensagem_ia)