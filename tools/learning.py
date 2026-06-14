import json
import random
from core.llm_client import call_llm
from services.rag_engine import buscar_material_rag_com_metadados
from tools.agenda import consultar_agenda, listar_tarefas

def gerar_exercicios(topico: str, quantidade: int = 3) -> dict:
    """Gera exercícios de múltipla escolha baseados nos materiais de estudo."""
    chunks = buscar_material_rag_com_metadados(topico, top_k=5)
    if not chunks:
        return {"erro": f"Não encontrei material sobre '{topico}'."}
    
    contexto = "\n\n".join([c["documento"] for c in chunks])
    
    prompt = f"""Com base no seguinte conteúdo, gere {quantidade} perguntas de múltipla escolha (cada uma com 4 alternativas) para avaliar o entendimento do aluno. Inclua a resposta correta e uma breve explicação.

Conteúdo:
{contexto}

Formato de saída (JSON apenas):
{{
  "exercicios": [
    {{
      "pergunta": "texto da pergunta",
      "opcoes": ["A) opção1", "B) opção2", "C) opção3", "D) opção4"],
      "resposta_correta": "A",
      "explicacao": "breve explicação da resposta correta"
    }}
  ]
}}
Apenas retorne o JSON, sem texto adicional."""
    
    resposta = call_llm([{"role": "user", "content": prompt}], temperature=0.5)
    try:
        inicio = resposta.find('{')
        fim = resposta.rfind('}') + 1
        if inicio != -1 and fim != -1:
            data = json.loads(resposta[inicio:fim])
            # Adiciona o tópico a cada exercício para uso na recomendação
            for ex in data.get("exercicios", []):
                ex["topico"] = topico
            return data
        else:
            return {"erro": "Falha ao gerar exercícios (formato inválido)."}
    except Exception as e:
        return {"erro": f"Erro ao processar exercícios: {e}"}

def recomendar_revisao(topicos_dificeis: list) -> list:
    """Recomenda arquivos da pasta data/ relacionados aos tópicos difíceis."""
    recomendados = set()
    for topico in topicos_dificeis:
        chunks = buscar_material_rag_com_metadados(topico, top_k=2)
        for chunk in chunks:
            if "source" in chunk:
                recomendados.add(chunk["source"])
    return list(recomendados)

def gerar_plano_estudos(objetivo: str, periodo: str = "semana") -> str:
    """
    Funcionalidade 3.4 - Planejamento de estudos
    Combina dados da agenda, tarefas e materiais para gerar um plano com a LLM.
    """
    # 1. Obter os eventos da agenda para o período solicitado
    eventos = consultar_agenda(periodo)
    str_eventos = "Nenhum evento na agenda." if not eventos else "\n".join([f"- {e[1]} em {e[2]} ({e[3]})" for e in eventos])

    # 2. Obter a lista de tarefas pendentes
    tarefas = listar_tarefas()
    # Filtra apenas as tarefas pendentes, se desejar, ou lista todas
    str_tarefas = "Nenhuma tarefa registrada." if not tarefas else "\n".join([f"- {t[1]} (Status: {t[2]})" for t in tarefas])

    # 3. Obter os materiais de estudo relevantes usando o RAG
    materiais = buscar_material_rag_com_metadados(objetivo, top_k=3)
    str_materiais = "Nenhum material específico encontrado." if not materiais else "\n".join(list(set([f"- {m['source']}" for m in materiais])))

    # 4. Construir o prompt que será enviado à LLM para gerar o plano
    prompt = f"""Atue como o JARVIS, um assistente e tutor acadêmico inteligente.
Sua missão é montar um plano de estudos estruturado e prático para o seguinte objetivo/foco: '{objetivo}'.

Para montar este plano, leve em consideração a disponibilidade de tempo baseada na agenda do aluno, as tarefas que ele precisa concluir e os materiais de estudo disponíveis.

📅 Eventos na Agenda ({periodo}):
{str_eventos}

✅ Tarefas Atuais:
{str_tarefas}

📚 Materiais de Estudo Sugeridos (com base no RAG):
{str_materiais}

Crie um planejamento em texto bem formatado e amigável. Indique o que o aluno deve priorizar, sugira como encaixar os estudos na agenda atual e como utilizar os materiais recomendados.
"""

    # 5. Chama a LLM para gerar a resposta baseada no contexto[cite: 3]
    try:
        resposta = call_llm([{"role": "user", "content": prompt}], temperature=0.5)
        return resposta
    except Exception as e:
        return f"Erro ao gerar plano de estudos: {e}"