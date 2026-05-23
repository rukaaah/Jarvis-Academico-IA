# tools/agenda.py
import sqlite3
from datetime import datetime, timedelta

DB_PATH = "jarvis.db"

# Criação ou inicialização do banco de dados
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS agenda
                 (id INTEGER PRIMARY KEY, titulo TEXT, data_hora TEXT, tipo TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS tarefas
                 (id INTEGER PRIMARY KEY, descricao TEXT, status TEXT)''')
    conn.commit()
    conn.close()

# Consulta de agenda
def consultar_agenda(periodo="hoje"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    hoje = datetime.now().date()
    if periodo == "hoje":
        start = datetime.combine(hoje, datetime.min.time())
        end = datetime.combine(hoje, datetime.max.time())
        c.execute("SELECT id, titulo, data_hora, tipo FROM agenda WHERE data_hora BETWEEN ? AND ?", (start.isoformat(), end.isoformat()))
    elif periodo == "semana":
        fim = hoje + timedelta(days=7)
        c.execute("SELECT id, titulo, data_hora, tipo FROM agenda WHERE date(data_hora) BETWEEN ? AND ?", (hoje.isoformat(), fim.isoformat()))
    else:
        c.execute("SELECT id, titulo, data_hora, tipo FROM agenda WHERE date(data_hora) = ?", (periodo,))
    rows = c.fetchall()
    conn.close()
    return rows

# Tarefas
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

# Função para interpretar entradas de forma neutra
def parse_data_hora(entrada: str) -> str:
    agora = datetime.now()
    entrada = entrada.strip().lower()
    
    if entrada == 'hoje':
        data = agora.date()
        hora = agora.time().replace(microsecond=0)
        return datetime.combine(data, hora).isoformat()
    elif entrada == 'amanhã':
        data = agora.date() + timedelta(days=1)
        hora = agora.time().replace(microsecond=0)
        return datetime.combine(data, hora).isoformat()
    elif entrada.startswith('amanhã às '):
        hora_str = entrada.split('às ')[-1]
        data = agora.date() + timedelta(days=1)
        dt = datetime.strptime(f"{data} {hora_str}", "%Y-%m-%d %H:%M")
        return dt.isoformat()
    elif entrada.startswith('hoje às '):
        hora_str = entrada.split('às ')[-1]
        data = agora.date()
        dt = datetime.strptime(f"{data} {hora_str}", "%Y-%m-%d %H:%M")
        return dt.isoformat()
    else:
        try:
            if 'T' in entrada:
                return entrada
            if '/' in entrada:
                if ' ' in entrada:
                    data_str, hora_str = entrada.split(' ')
                    dia, mes, ano = map(int, data_str.split('/'))
                    dt = datetime(ano, mes, dia, *map(int, hora_str.split(':')))
                else:
                    dia, mes, ano = map(int, entrada.split('/'))
                    dt = datetime(ano, mes, dia)
                return dt.isoformat()
            return datetime.strptime(entrada, "%Y-%m-%d %H:%M:%S").isoformat()
        except Exception:
            raise ValueError(f"Formato de data/hora não reconhecido: {entrada}")

def adicionar_evento_agenda(titulo: str, data_hora: str, tipo: str = "evento") -> str:
    try:
        data_hora_iso = parse_data_hora(data_hora)
    except ValueError as e:
        return f"Erro: {e}"
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO agenda (titulo, data_hora, tipo) VALUES (?, ?, ?)",
              (titulo, data_hora_iso, tipo))
    conn.commit()
    conn.close()
    return f"Evento '{titulo}' adicionado para {data_hora_iso}."

def remover_evento_agenda(id_evento: int) -> str:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM agenda WHERE id = ?", (id_evento,))
    if not c.fetchone():
        conn.close()
        return f"Evento com ID {id_evento} não encontrado."
    c.execute("DELETE FROM agenda WHERE id = ?", (id_evento,))
    conn.commit()
    conn.close()
    return f"Evento {id_evento} removido da agenda."

# Inicializa o banco de dados na primeira importação
init_db()