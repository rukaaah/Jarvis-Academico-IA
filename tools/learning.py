import json
import random
from core.llm_client import call_llm
from services.rag_engine import buscar_material_rag_com_metadados

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