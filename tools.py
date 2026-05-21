import json
import os
import logging
from agenda_tarefas import consultar_agenda, listar_tarefas, adicionar_tarefa, concluir_tarefa, adicionar_evento_agenda
from rag_engine import buscar_material_rag

# Cria diretório de logs se não existir
os.makedirs('logs', exist_ok=True)

# Configuração do logging
logging.basicConfig(
    filename='logs/tool_calls.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# Descrição das ferramentas para o prompt da LLM (tool calling manual)
tools_description = """
Você tem acesso a estas ferramentas:

1. consultar_agenda(periodo)
   - periodo: "hoje", "semana" ou "YYYY-MM-DD" (ex: "2025-05-21")
   - Retorna os eventos da agenda.

2. listar_tarefas()
   - Lista todas as tarefas com seus IDs e status.

3. adicionar_tarefa(descricao)
   - descricao: texto da tarefa
   - Adiciona uma nova tarefa pendente.

4. concluir_tarefa(id)
   - id: número inteiro da tarefa
   - Marca a tarefa como concluída.

5. buscar_material_rag(pergunta)
   - pergunta: texto da consulta
   - Busca nos documentos de estudo (PDF, TXT) e retorna trechos relevantes.

6. adicionar_evento_agenda(titulo, data_hora, tipo)
   - titulo: string com o nome do evento
   - data_hora: string no formato "YYYY-MM-DD HH:MM:SS" ou "YYYY-MM-DDTHH:MM:SS"
   - tipo: "aula", "prova" ou "evento"
   - Adiciona um evento à agenda acadêmica.
"""


def log_tool_call(tool_name, inputs, outputs):
    """Registra a chamada da ferramenta no arquivo de log."""
    logging.info(f"TOOL: {tool_name} | INPUT: {json.dumps(inputs)} | OUTPUT: {str(outputs)[:200]}")

def execute_tool_call(tool_name: str, arguments: dict):
    """
    Executa uma ferramenta manualmente (usado no app com tool calling via prompt).
    """
    result = None
    if tool_name == "consultar_agenda":
        periodo = arguments.get("periodo", "hoje")
        result = consultar_agenda(periodo)
    elif tool_name == "listar_tarefas":
        result = listar_tarefas()
    elif tool_name == "adicionar_tarefa":
        descricao = arguments.get("descricao")
        result = adicionar_tarefa(descricao)
    elif tool_name == "concluir_tarefa":
        id_tarefa = arguments.get("id")
        result = concluir_tarefa(id_tarefa)
    elif tool_name == "buscar_material_rag":
        pergunta = arguments.get("pergunta")
        result = buscar_material_rag(pergunta)
    elif tool_name == "adicionar_evento_agenda":
        titulo = arguments.get("titulo")
        data_hora = arguments.get("data_hora")
        tipo = arguments.get("tipo", "evento")
        result = adicionar_evento_agenda(titulo, data_hora, tipo)
    else:
        result = f"Ferramenta desconhecida: {tool_name}"
    
    log_tool_call(tool_name, arguments, result)
    return result

# Mantido apenas para referência (não usado no novo app, mas compatível)
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "consultar_agenda",
            "description": "Consulta a agenda acadêmica para um período. Use 'hoje', 'semana' ou 'YYYY-MM-DD'.",
            "parameters": {
                "type": "object",
                "properties": {"periodo": {"type": "string", "enum": ["hoje", "semana"], "description": "Período a consultar"}},
                "required": ["periodo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "listar_tarefas",
            "description": "Lista todas as tarefas com seus status.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "adicionar_tarefa",
            "description": "Adiciona uma nova tarefa à lista.",
            "parameters": {
                "type": "object",
                "properties": {"descricao": {"type": "string"}},
                "required": ["descricao"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "concluir_tarefa",
            "description": "Marca uma tarefa como concluída pelo seu ID.",
            "parameters": {
                "type": "object",
                "properties": {"id": {"type": "integer"}},
                "required": ["id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_material_rag",
            "description": "Busca nos materiais de estudo (documentos) trechos relevantes para uma pergunta.",
            "parameters": {
                "type": "object",
                "properties": {"pergunta": {"type": "string"}},
                "required": ["pergunta"]
            }
        }
    }
]