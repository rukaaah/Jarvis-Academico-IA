import streamlit as st
from openai import OpenAI
from tools import execute_tool_call, tools_description
from rag_engine import remover_documento, adicionar_documento
import json
import re
import os
from file_monitor import iniciar_monitoramento
import rag_engine
from dotenv import load_dotenv

load_dotenv()

if "monitor_iniciado" not in st.session_state:
    observer = iniciar_monitoramento(rag_engine)
    st.session_state.monitor_iniciado = True
    # Para garantir que o monitor seja parado ao fechar o app (opcional)
    import atexit
    atexit.register(observer.stop)
API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")
API_URL = st.secrets.get("API_URL")
API_KEY = st.secrets["API_KEY"]
client = OpenAI(base_url=API_URL, api_key=API_KEY)

st.set_page_config(page_title="JARVIS Acadêmico", layout="wide")
st.title("🎓 JARVIS Acadêmico")
st.caption("Assistente inteligente com RAG + Tool Calling (manual) | Gemma 12B")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

SYSTEM_PROMPT = f"""Você é o JARVIS, um assistente acadêmico. Você tem acesso a estas ferramentas:

{tools_description}

Quando o usuário pedir algo que exija uma ferramenta, responda APENAS com um JSON no seguinte formato:
{{"tool": "nome_da_ferramenta", "arguments": {{"param1": "valor1", ...}}}}

Se não precisar de ferramenta, responda normalmente em linguagem natural.

Exemplos:
- Usuário: "Adicione tarefa Estudar IA" → {{"tool": "adicionar_tarefa", "arguments": {{"descricao": "Estudar IA"}}}}
- Usuário: "O que tenho hoje?" → {{"tool": "consultar_agenda", "arguments": {{"periodo": "hoje"}}}}
- Usuário: "Explique regressão logística" → resposta normal (sem tool)

Nunca invente respostas. Se não souber, diga que não sabe.
"""

def call_llm(messages):
    response = client.chat.completions.create(
        model='google/gemma-3-12b-it',
        messages=messages,
        temperature=0.3
    )
    return response.choices[0].message.content

def extract_tool_call(content):
    try:
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            data = json.loads(match.group())
            if "tool" in data and "arguments" in data:
                return data
    except:
        pass
    return None

# ========== SIDEBAR OTIMIZADA ==========
from agenda_tarefas import listar_tarefas, consultar_agenda

# Métricas lado a lado (sem CSS extra)
tarefas = listar_tarefas()
pendentes = [t for t in tarefas if t[2] == "pendente"]
hoje = consultar_agenda("hoje")

col1, col2 = st.sidebar.columns(2)
with col1:
    st.metric("📝 Pendentes", len(pendentes))
with col2:
    st.metric("📅 Eventos hoje", len(hoje))

st.sidebar.divider()

# Seção de upload recolhida por padrão
with st.sidebar.expander("📎 Adicionar Material de Estudo", expanded=False):
    if "upload_key" not in st.session_state:
        st.session_state.upload_key = 0

    uploaded_file = st.file_uploader(
        "Envie PDF ou TXT",
        type=["pdf", "txt"],
        key=f"file_uploader_{st.session_state.upload_key}",
        help="O arquivo será processado e incorporado à base de conhecimento."
    )

    DATA_DIR = "data"
    # Botão com largura total e texto reduzido para evitar quebra
    if st.button("Adicionar", use_container_width=True):
        if uploaded_file is None:
            st.error("❌ Selecione um arquivo.")
        else:
            filepath = os.path.join(DATA_DIR, uploaded_file.name)
            if os.path.exists(filepath):
                st.warning(f"⚠️ '{uploaded_file.name}' já existe.")
            else:
                with open(filepath, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                with st.spinner("Processando..."):
                    try:
                        from rag_engine import adicionar_documento
                        success = adicionar_documento(filepath)
                        if success:
                            st.success(f"✅ {uploaded_file.name} adicionado!")
                            st.session_state.upload_key += 1
                            st.rerun()
                        else:
                            st.error(f"❌ Falha ao processar {uploaded_file.name}.")
                    except Exception as e:
                        st.error(f"Erro: {str(e)}")

st.sidebar.divider()

# Seção de arquivos recolhida por padrão
with st.sidebar.expander("📂 Arquivos de Estudo", expanded=False):
    os.makedirs(DATA_DIR, exist_ok=True)  # DATA_DIR já definido acima
    arquivos = [f for f in os.listdir(DATA_DIR) if f.endswith(('.pdf', '.txt'))]

    if arquivos:
        for arq in arquivos:
            col_arq, col_btn = st.columns([0.8, 0.2])
            col_arq.write(f"📄 {arq}")
            if col_btn.button("🗑️", key=f"del_{arq}"):
                os.remove(os.path.join(DATA_DIR, arq))
                remover_documento(arq)
                st.success(f"✅ {arq} removido.")
                st.rerun()
    else:
        st.info("Nenhum arquivo adicionado ainda.")

# ========== CHAT ==========
prompt = st.chat_input("Digite sua pergunta...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_text = ""
        placeholder = st.empty()
        try:
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            for m in st.session_state.messages:
                messages.append({"role": m["role"], "content": m["content"]})
            
            assistant_msg = call_llm(messages)
            tool_call = extract_tool_call(assistant_msg)
            
            if tool_call:
                tool_name = tool_call["tool"]
                args = tool_call["arguments"]
                result = execute_tool_call(tool_name, args)
                messages.append({"role": "assistant", "content": f"[Chamando ferramenta {tool_name}]"})
                messages.append({"role": "user", "content": f"Resultado da ferramenta: {result}"})
                final_response = call_llm(messages)
                response_text = final_response
            else:
                response_text = assistant_msg
            
            placeholder.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
        except Exception as e:
            st.error(f"Erro: {e}")