import pandas as pd
from database_config import get_connection

def crear_tablas():
    """Crea la tabla 'categoria_comercio' y asegura que las columnas sean las correctas."""
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            # 1. Crear la tabla con la nueva estructura simplificada
            cur.execute('''
                CREATE TABLE IF NOT EXISTS categoria_comercio (
                    id SERIAL PRIMARY KEY,   
                    comercio_id TEXT NOT NULL,
                    nombre TEXT NOT NULL,
                    categoria TEXT
                )
            ''')
            
            # 2. Lógica de migración: Si existe 'nombre_comercio', renombrarla a 'nombre'
            cur.execute("""
                DO $$ 
                BEGIN 
                    IF EXISTS (SELECT 1 FROM information_schema.columns 
                               WHERE table_name='comercios' AND column_name='nombre_comercio') THEN
                        ALTER TABLE comercios RENAME COLUMN nombre_comercio TO nombre;
                    END IF;
                END $$;
            """)
            conn.commit()
            cur.close()
        finally:
            conn.close()

def insertar_comercio(comercio_id, nombre, categoria):
    """Guarda un nuevo registro en la tabla 'categoria_comercio'."""
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            query = "INSERT INTO categoria_comercio (comercio_id, nombre, categoria) VALUES (%s, %s, %s)"
            cur.execute(query, (comercio_id, nombre, categoria))
            conn.commit()
            cur.close()
        finally:
            conn.close()

def obtener_comercios():
    """Recupera los comercios asegurando que las columnas coincidan con el DataFrame."""
    conn = get_connection()
    df = pd.DataFrame()
    if conn:
        try:
            # Consultamos la tabla 'comercios' que es la que el error reportaba
            query = "SELECT id, comercio_id, nombre, categoria FROM categoria_comercio ORDER BY id DESC"
            df = pd.read_sql(query, conn)
            df.columns = [c.lower() for c in df.columns]
        finally:
            conn.close()
    return df

def actualizar_comercio(id_db, comercio_id, nombre, categoria):
    """Actualiza un categoria_comercio existente en la tabla 'comercios'."""
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            query = """
                UPDATE categoria_comercio 
                SET comercio_id = %s, nombre = %s, categoria = %s
                WHERE id = %s
            """
            cur.execute(query, (comercio_id, nombre, categoria, id_db))
            conn.commit()
            cur.close()
        finally:
            conn.close()

def eliminar_comercio(id_db):
    """Borra un registro por su ID único."""
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM categoria_comercio WHERE id = %s", (id_db,))
            conn.commit()
            cur.close()
        finally:
            conn.close()