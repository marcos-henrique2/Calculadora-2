import sqlite3
import json
import os

# Define o nome da pasta de dados
DATA_DIR = "data"
# Cria o caminho completo para o arquivo do banco de dados
DB_FILE = os.path.join(DATA_DIR, "orcamento_persistente.db")

def init_db():
    """Garante que a pasta 'data' exista e cria a tabela no banco."""
    # Cria a pasta 'data/' se ela não existir
    os.makedirs(DATA_DIR, exist_ok=True)
    
    conn = sqlite3.connect(DB_FILE)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS orcamento_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_data TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def load_items():
    """Carrega todos os itens do banco de dados."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.execute('SELECT item_data FROM orcamento_items')
    # Converte cada linha de texto JSON de volta para um dicionário Python
    items = [json.loads(row[0]) for row in cursor.fetchall()]
    conn.close()
    return items

def save_all_items(items_list):
    """Apaga todos os itens antigos no banco e salva a lista nova."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM orcamento_items')
    
    if items_list:
        # Converte cada dicionário da lista para texto JSON para salvar
        data_to_insert = [(json.dumps(item),) for item in items_list]
        cursor.executemany(
            'INSERT INTO orcamento_items (item_data) VALUES (?)',
            data_to_insert
        )
    
    conn.commit()
    conn.close()