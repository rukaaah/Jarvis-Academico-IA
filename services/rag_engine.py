import os
from typing import List
import chromadb
from pypdf import PdfReader
from fastembed import TextEmbedding
from .ocr_processor import extrair_texto_imagem

DOCS_DIR = "data"
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "documentos"

_client = None
_collection = None
_embedding_model = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
    return _embedding_model

def gerar_embedding(texto: str) -> List[float]:
    model = get_embedding_model()
    embedding = next(model.embed([texto]))
    return embedding.tolist()

def get_chroma_collection():
    global _client, _collection
    if _client is None:
        _client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = _client.get_or_create_collection(name=COLLECTION_NAME)
    return _collection

def extrair_texto_pdf(caminho: str) -> str:
    reader = PdfReader(caminho)
    texto = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            texto += page_text + "\n"
    return texto

def carregar_documentos():
    col = get_chroma_collection()
    if col.count() > 0:
        return
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR)
    docs, metadatas, ids = [], [], []
    for filename in os.listdir(DOCS_DIR):
        filepath = os.path.join(DOCS_DIR, filename)
        ext = filename.lower()
        if ext.endswith(".txt"):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        elif ext.endswith(".pdf"):
            content = extrair_texto_pdf(filepath)
        elif ext.endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff")):
            content = extrair_texto_imagem(filepath)
        else:
            continue
        if not content.strip():
            print(f"⚠️ Conteúdo vazio para {filename}")
            continue
        chunks = [content[j:j+500] for j in range(0, len(content), 450)]
        for k, chunk in enumerate(chunks):
            if chunk.strip():
                docs.append(chunk)
                metadatas.append({"source": filename})
                ids.append(f"{filename}_{k}")
    if docs:
        embeddings = [gerar_embedding(doc) for doc in docs]
        col.add(ids=ids, embeddings=embeddings, documents=docs, metadatas=metadatas)
        print(f"{len(docs)} chunks indexados")
    else:
        print("Nenhum documento válido encontrado na pasta 'data'.")

def buscar_material_rag(pergunta: str, top_k: int = 10) -> List[dict]:
    print(f"🔍 Buscando no RAG: {pergunta}")
    col = get_chroma_collection()
    query_embedding = gerar_embedding(pergunta)
    results = col.query(query_embeddings=[query_embedding], n_results=top_k)
    if not results['documents']:
        return []
    output = []
    for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
        output.append({"texto": doc, "fonte": meta.get("source", "desconhecido")})
    return output

def buscar_material_rag_com_metadados(pergunta: str, top_k: int = 3) -> List[dict]:
    col = get_chroma_collection()
    query_embedding = gerar_embedding(pergunta)
    results = col.query(query_embeddings=[query_embedding], n_results=top_k)
    if not results['documents']:
        return []
    output = []
    for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
        output.append({"documento": doc, "source": meta.get("source", "desconhecido")})
    return output

def adicionar_documento(filepath: str) -> bool:
    if not os.path.exists(filepath):
        return False
    filename = os.path.basename(filepath)
    ext = filename.lower()
    if ext.endswith(".txt"):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    elif ext.endswith(".pdf"):
        content = extrair_texto_pdf(filepath)
    elif ext.endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff")):
        content = extrair_texto_imagem(filepath)
    else:
        return False
    if not content.strip():
        return False
    col = get_chroma_collection()
    chunks = [content[j:j+500] for j in range(0, len(content), 450)]
    docs, metadatas, ids = [], [], []
    for k, chunk in enumerate(chunks):
        if chunk.strip():
            docs.append(chunk)
            metadatas.append({"source": filename})
            ids.append(f"{filename}_{k}")
    if not docs:
        return False
    embeddings = [gerar_embedding(doc) for doc in docs]
    col.add(ids=ids, embeddings=embeddings, documents=docs, metadatas=metadatas)
    print(f"{len(docs)} chunks adicionados de {filename}")
    return True

def remover_documento(nome_arquivo: str) -> bool:
    col = get_chroma_collection()
    try:
        resultados = col.get(where={"source": nome_arquivo})
        ids_remover = resultados['ids']
        if ids_remover:
            col.delete(ids=ids_remover)
            print(f"Removidos {len(ids_remover)} chunks do documento {nome_arquivo}")
            return True
        else:
            print(f"Nenhum chunk encontrado para {nome_arquivo}")
            return False
    except Exception as e:
        print(f"Erro ao remover documento {nome_arquivo}: {e}")
        return False

carregar_documentos()