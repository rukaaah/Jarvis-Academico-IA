import streamlit as st
from core.agent import run_agent
from tools import listar_tarefas, consultar_agenda, gerar_exercicios, recomendar_revisao
from services.rag_engine import remover_documento, adicionar_documento
from services.file_monitor import iniciar_monitoramento
import services.rag_engine as rag_engine
from datetime import datetime
import os
import re
from dotenv import load_dotenv

load_dotenv()

# Inicia o monitor da pasta data/ (uma única vez)
if "monitor_iniciado" not in st.session_state:
    observer = iniciar_monitoramento(rag_engine)
    st.session_state.monitor_iniciado = True
    import atexit
    atexit.register(observer.stop)

st.set_page_config(page_title="JARVIS Acadêmico", layout="wide")
st.title("JARVIS Acadêmico")
st.caption("Assistente inteligente com RAG + Tool Calling (manual) | Gemma 12B")

# Estados para os exercícios
if "exercicios" not in st.session_state:
    st.session_state.exercicios = None
    st.session_state.exercicio_atual = 0
    st.session_state.respostas = []
    st.session_state.pontuacao = 0
    st.session_state.erros = []

# Histórico da conversa
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Sidebar
tarefas = listar_tarefas()
pendentes = [t for t in tarefas if t[2] == "pendente"]
hoje = consultar_agenda("hoje")

col1, col2 = st.sidebar.columns(2)
with col1:
    st.metric("Pendentes", len(pendentes))
with col2:
    st.metric("Eventos hoje", len(hoje))

st.sidebar.divider()

# Upload de arquivos
DATA_DIR = "data"
with st.sidebar.expander("Adicionar Material de Estudo", expanded=False):
    if "upload_key" not in st.session_state:
        st.session_state.upload_key = 0

    uploaded_file = st.file_uploader(
        "Anexe aqui seus arquivos de estudo",
        type=["pdf", "txt", "png", "jpg", "jpeg"],
        key=f"file_uploader_{st.session_state.upload_key}",
    )

    if st.button("Adicionar", use_container_width=True):
        if uploaded_file is None:
            st.error("Selecione um arquivo.")
        else:
            filepath = os.path.join(DATA_DIR, uploaded_file.name)
            if os.path.exists(filepath):
                st.warning(f"'{uploaded_file.name}' já existe.")
            else:
                with open(filepath, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                with st.spinner("Processando..."):
                    try:
                        success = adicionar_documento(filepath)
                        if success:
                            st.success(f"{uploaded_file.name} adicionado!")
                            st.session_state.upload_key += 1
                            st.rerun()
                        else:
                            st.error(f"Falha ao processar {uploaded_file.name}.")
                    except Exception as e:
                        st.error(f"Erro: {str(e)}")

st.sidebar.divider()

# Lista de arquivos já adicionados
with st.sidebar.expander("Arquivos de Estudo", expanded=False):
    os.makedirs(DATA_DIR, exist_ok=True)
    arquivos = [f for f in os.listdir(DATA_DIR) if f.endswith(('.pdf', '.txt', '.png', '.jpg', '.jpeg'))]
    if arquivos:
        for arq in arquivos:
            col_arq, col_btn = st.columns([0.8, 0.2])
            col_arq.write(f"📄 {arq}")
            if col_btn.button("🗑️", key=f"del_{arq}"):
                os.remove(os.path.join(DATA_DIR, arq))
                remover_documento(arq)
                st.success(f"{arq} removido.")
                st.rerun()
    else:
        st.info("Nenhum arquivo adicionado ainda.")
# Chat
prompt = st.chat_input("Digite sua pergunta...")
if prompt:
    # Verifica se o usuário quer gerar exercícios (ex: "gerar exercícios sobre regressão logística")
    match_ex = re.search(r"(?:gerar|criar|quero)\s+(?:exercícios?\s+(?:sobre|de|para|acerca de)\s+)(.+)", prompt, re.IGNORECASE)
    if match_ex:
        topico = match_ex.group(1).strip()
        with st.chat_message("assistant"):
            with st.spinner(f"🔍 Gerando exercícios sobre '{topico}'..."):
                data = gerar_exercicios(topico, quantidade=3)
                if "erro" in data:
                    st.error(data["erro"])
                else:
                    st.session_state.exercicios = data["exercicios"]
                    st.session_state.exercicio_atual = 0
                    st.session_state.pontuacao = 0
                    st.session_state.erros = []
                    st.success(f"✅ Exercícios sobre '{topico}' gerados! Veja na área acima.")
                    st.rerun()
    else:
        # Processa normalmente com o agente
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                try:
                    response = run_agent(st.session_state.messages)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"Erro: {e}")