import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importação corrigida para apontar para a pasta tools
from tools.learning import gerar_plano_estudos

# Caminhos do patch corrigidos para tools.learning
@patch('tools.learning.call_llm')
@patch('tools.learning.buscar_material_rag_com_metadados')
@patch('tools.learning.consultar_agenda')
@patch('tools.learning.listar_tarefas')
def test_gerar_plano_estudos_sucesso(mock_listar_tarefas, mock_consultar_agenda, mock_rag, mock_llm):
    
    mock_consultar_agenda.return_value = [(1, "Aula de IA", "2026-06-20T10:00", "aula")]
    mock_listar_tarefas.return_value = [(1, "Ler artigo de RAG", "pendente")]
    mock_rag.return_value = [{"documento": "Texto ficticio sobre RAG", "source": "aula_rag.pdf"}]
    mock_llm.return_value = "Aqui está seu plano de estudos focado em IA!..."

    resultado = gerar_plano_estudos(objetivo="Aprender IA", periodo="semana")

    assert "Aqui está seu plano de estudos" in resultado
    
    mock_consultar_agenda.assert_called_once_with("semana")
    mock_listar_tarefas.assert_called_once()
    mock_rag.assert_called_once()
    mock_llm.assert_called_once()