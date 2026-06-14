import sys
import os
import pytest
from core.agent import extract_tool_calls

def test_extract_tool_calls_json_simples():
    resposta_llm = '{"tool": "listar_tarefas", "arguments": {}}'
    tools = extract_tool_calls(resposta_llm)
    
    assert len(tools) == 1
    assert tools[0]["tool"] == "listar_tarefas"

def test_extract_tool_calls_multiplos_jsons():
    resposta_llm = '''
    {"tool": "concluir_tarefa", "arguments": {"id": 1}}
    {"tool": "adicionar_tarefa", "arguments": {"descricao": "Estudar embeddings"}}
    '''
    tools = extract_tool_calls(resposta_llm)
    
    assert len(tools) == 2
    assert tools[0]["tool"] == "concluir_tarefa"
    assert tools[1]["tool"] == "adicionar_tarefa"
    assert tools[1]["arguments"]["descricao"] == "Estudar embeddings"

def test_extract_tool_calls_sem_json():
    resposta_llm = "Olá! A regressão logística é um algoritmo de classificação..."
    tools = extract_tool_calls(resposta_llm)
    
    assert len(tools) == 0