from .agenda import (
    consultar_agenda, listar_tarefas, adicionar_tarefa, concluir_tarefa,
    adicionar_evento_agenda, remover_evento_agenda
)
from .rag_tool import buscar_material_rag
from .executor import execute_tool_call
from .description import tools_description
from .learning import gerar_exercicios, recomendar_revisao