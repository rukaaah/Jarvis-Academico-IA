# tests/test_agenda_tarefas.py
import sys
import os
import tempfile
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools import agenda
original_db_path = agenda.DB_PATH
agenda.DB_PATH = tempfile.mktemp(suffix=".db")

@pytest.fixture(autouse=True)
def setup_db():
    """Cria um banco temporário antes de cada teste."""
    agenda.init_db()
    yield
    if os.path.exists(agenda.DB_PATH):
        os.remove(agenda.DB_PATH)

def test_adicionar_tarefa():
    resultado = agenda.adicionar_tarefa("Estudar Python")
    assert "Tarefa 'Estudar Python' adicionada" in resultado
    tarefas = agenda.listar_tarefas()
    assert len(tarefas) == 1
    assert tarefas[0][1] == "Estudar Python"
    assert tarefas[0][2] == "pendente"

def test_concluir_tarefa():
    agenda.adicionar_tarefa("Revisar RAG")
    tarefas = agenda.listar_tarefas()
    id_tarefa = tarefas[0][0]
    resultado = agenda.concluir_tarefa(id_tarefa)
    assert f"Tarefa {id_tarefa} concluída" in resultado
    tarefas_atualizadas = agenda.listar_tarefas()
    assert tarefas_atualizadas[0][2] == "concluida"

def test_consultar_agenda():
    # Adiciona um evento manualmente no banco temporário
    conn = agenda.sqlite3.connect(agenda.DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO agenda (titulo, data_hora, tipo) VALUES (?, ?, ?)",
              ("Aula de IA", "2025-12-31T10:00:00", "aula"))
    conn.commit()
    conn.close()
    eventos = agenda.consultar_agenda("2025-12-31")
    assert len(eventos) == 1
    assert eventos[0][1] == "Aula de IA"

def test_adicionar_e_remover_evento_agenda():
    # Adicionamos o :00 no final da string de data/hora
    resultado_add = agenda.adicionar_evento_agenda("Prova de IA", "2026-06-20 14:00:00", "prova")
    assert "adicionado" in resultado_add
    
    eventos = agenda.consultar_agenda("2026-06-20")
    assert len(eventos) == 1
    assert eventos[0][1] == "Prova de IA"
    
    id_evento = eventos[0][0]
    resultado_rem = agenda.remover_evento_agenda(id_evento)
    assert f"removido da agenda" in resultado_rem
    
    eventos_depois = agenda.consultar_agenda("2026-06-20")
    assert len(eventos_depois) == 0