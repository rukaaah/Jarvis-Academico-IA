import os
import logging
from .agenda import consultar_agenda, listar_tarefas, adicionar_tarefa, concluir_tarefa, adicionar_evento_agenda, remover_evento_agenda
from .rag_tool import buscar_material_rag
from .learning import gerar_exercicios, recomendar_revisao, gerar_plano_estudos
import logging

os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    filename='logs/tool_calls.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

def execute_tool_call(tool_name: str, arguments: dict):
    logging.info(f"TOOL: {tool_name} | ARGS: {arguments}")
    if tool_name == "consultar_agenda":
        periodo = arguments.get("periodo", "hoje")
        rows = consultar_agenda(periodo)
        if not rows:
            return "Nenhum evento encontrado."
        return "\n".join([f"ID: {r[0]} | {r[1]} - {r[2]} ({r[3]})" for r in rows])
    elif tool_name == "listar_tarefas":
        rows = listar_tarefas()
        return "\n".join([f"ID: {r[0]} | {r[1]} - {r[2]}" for r in rows]) if rows else "Nenhuma tarefa."
    elif tool_name == "adicionar_tarefa":
        return adicionar_tarefa(arguments.get("descricao"))
    elif tool_name == "concluir_tarefa":
        return concluir_tarefa(arguments.get("id"))
    elif tool_name == "buscar_material_rag":
        resultados = buscar_material_rag(arguments.get("pergunta"))
        if not resultados:
            result = "Nenhum trecho relevante encontrado."
        else:
            result = "\n".join([f"[{r['fonte']}] {r['texto']}" for r in resultados])
        return result
    elif tool_name == "adicionar_evento_agenda":
        return adicionar_evento_agenda(arguments.get("titulo"), arguments.get("data_hora"), arguments.get("tipo", "evento"))
    elif tool_name == "remover_evento_agenda":
        return remover_evento_agenda(arguments.get("id_evento"))
    elif tool_name == "gerar_exercicios":
        topico = arguments.get("topico")
        quantidade = arguments.get("quantidade", 3)
        result = gerar_exercicios(topico, quantidade)
        return result
    elif tool_name == "recomendar_revisao":
        topicos = arguments.get("topicos_dificeis", [])
        result = recomendar_revisao(topicos)
        return result
    elif tool_name == "gerar_plano_estudos":
        objetivo = arguments.get("objetivo", "organizar os estudos gerais")
        periodo = arguments.get("periodo", "semana")
        dia = arguments.get("dia")
        return gerar_plano_estudos(objetivo, periodo, dia)
    else:
        return f"Ferramenta desconhecida: {tool_name}"