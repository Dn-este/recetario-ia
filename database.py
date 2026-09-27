import sqlite3
from typing import List, Dict

DB_NAME = "recetas.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS recetas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            url TEXT,
            ingredientes TEXT,
            pasos TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def guardar_receta(titulo: str, url: str, ingredientes: str, pasos: str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "INSERT INTO recetas (titulo, url, ingredientes, pasos) VALUES (?, ?, ?, ?)",
        (titulo, url, ingredientes, pasos)
    )
    conn.commit()
    conn.close()

def obtener_recetas() -> List[Dict]:
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM recetas ORDER BY fecha DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def actualizar_receta(id_receta: int, titulo: str, pasos: str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "UPDATE recetas SET titulo = ?, pasos = ? WHERE id = ?",
        (titulo, pasos, id_receta)
    )
    conn.commit()
    conn.close()

def eliminar_receta(id_receta: int):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM recetas WHERE id = ?", (id_receta,))
    conn.commit()
    conn.close()
