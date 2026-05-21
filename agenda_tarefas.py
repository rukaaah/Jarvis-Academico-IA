import sqlite3
from datetime import datetime, timedelta

DB_PATH = "jarvis.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS agenda
                 (id INTEGER PRIMARY KEY, titulo TEXT, data_hora TEXT, tipo TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS tarefas
                 (id INTEGER PRIMARY KEY, descricao TEXT, status TEXT)''')
    conn.commit()
    # Dados de exemplo
    hoje = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
    amanha = hoje + timedelta(days=1)
    c.execute("SELECT COUNT(*) FROM agenda")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO agenda (titulo, data_hora, tipo) VALUES (?,?,?)",
                  ("Aula de IA", hoje.isoformat(), "aula"))
        c.execute("INSERT INTO agenda (titulo, data_hora, tipo) VALUES (?,?,?)",
                  ("Prova de ML", amanha.isoformat(), "prova"))
    c.execute("SELECT COUNT(*) FROM tarefas")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO tarefas (descricao, status) VALUES (?,?)",
                  ("Revisar regressão logística", "pendente"))
        c.execute("INSERT INTO tarefas (descricao, status) VALUES (?,?)",
                  ("Preparar apresentação RAG", "pendente"))
    conn.commit()
    conn.close()

def consultar_agenda(periodo="hoje"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    hoje = datetime.now().date()
    if periodo == "hoje":
        start = datetime.combine(hoje, datetime.min.time())
        end = datetime.combine(hoje, datetime.max.time())
        c.execute("SELECT titulo, data_hora, tipo FROM agenda WHERE data_hora BETWEEN ? AND ?", (start.isoformat(), end.isoformat()))
    elif periodo == "semana":
        fim = hoje + timedelta(days=7)
        c.execute("SELECT titulo, data_hora, tipo FROM agenda WHERE date(data_hora) BETWEEN ? AND ?", (hoje.isoformat(), fim.isoformat()))
    else:  # data específica (formato YYYY-MM-DD)
        c.execute("SELECT titulo, data_hora, tipo FROM agenda WHERE date(data_hora) = ?", (periodo,))
    rows = c.fetchall()
    conn.close()
    return rows

def listar_tarefas():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, descricao, status FROM tarefas")
    rows = c.fetchall()
    conn.close()
    return rows

def adicionar_tarefa(descricao):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO tarefas (descricao, status) VALUES (?, ?)", (descricao, "pendente"))
    conn.commit()
    conn.close()
    return f"Tarefa '{descricao}' adicionada."

def concluir_tarefa(id_tarefa):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE tarefas SET status = 'concluida' WHERE id = ?", (id_tarefa,))
    conn.commit()
    conn.close()
    return f"Tarefa {id_tarefa} concluída."

init_db()