import streamlit as st
import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno del archivo .env
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Configuración de conexión
DB_CONFIG = {
    "host": "localhost",
    "database": os.getenv("POSTGRES_DB", "aupa"),
    "user": os.getenv("POSTGRES_USER", "aupa"),
    "password": os.getenv("POSTGRES_PASSWORD", "password"),
    "port": "5432"
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    """Crea la tabla de comercios si no existe."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS comercios (
            id SERIAL PRIMARY KEY,
            comercio_id VARCHAR(50) UNIQUE NOT NULL,
            nombre VARCHAR(100) NOT NULL,
            categoria VARCHAR(50) NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# --- INTERFAZ STREAMLIT ---
##st.set_page_config(page_title="Admin Comercios", page_icon="🗄️")
st.title("🗄️ Aupa- Gestión Comercios")

init_db()

# Estado para controlar la edición
if 'editing_id' not in st.session_state:
    st.session_state.editing_id = None

# --- FORMULARIO DINÁMICO (CREAR / EDITAR) ---
titulo_form = "📝 Editar Comercio" if st.session_state.editing_id else "➕ Añadir Nuevo Comercio"
with st.expander(titulo_form, expanded=st.session_state.editing_id is not None):
    
    # Si estamos editando, precargar datos
    default_id = ""
    default_nombre = ""
    default_cat_idx = 0
    categorias = ["Alimentos", "Hogar", "Restaurante", "Moda", "Servicios"]

    if st.session_state.editing_id:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT comercio_id, nombre, categoria FROM comercios WHERE comercio_id = %s", (st.session_state.editing_id,))
        comercio_actual = cur.fetchone()
        if comercio_actual:
            default_id, default_nombre, current_cat = comercio_actual
            default_cat_idx = categorias.index(current_cat) if current_cat in categorias else 0
        cur.close()
        conn.close()

    with st.form("form_comercio", clear_on_submit=True):
        c_id = st.text_input("ID del Comercio", value=default_id, disabled=st.session_state.editing_id is not None)
        nombre = st.text_input("Nombre del Comercio", value=default_nombre)
        categoria = st.selectbox("Categoría", categorias, index=default_cat_idx)
        
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            texto_boton = "Actualizar Cambios" if st.session_state.editing_id else "Guardar"
            submit = st.form_submit_button(texto_boton)
        with col_btn2:
            if st.session_state.editing_id:
                cancelar = st.form_submit_button("Cancelar Edición")
                if cancelar:
                    st.session_state.editing_id = None
                    st.rerun()

        if submit:
            try:
                conn = get_connection()
                cur = conn.cursor()
                if st.session_state.editing_id:
                    # OPERACIÓN: EDITAR [Novedad]
                    cur.execute(
                        "UPDATE comercios SET nombre = %s, categoria = %s WHERE comercio_id = %s",
                        (nombre, categoria, st.session_state.editing_id)
                    )
                    st.success(f"✅ {nombre} actualizado correctamente.")
                    st.session_state.editing_id = None
                else:
                    # OPERACIÓN: CREAR
                    cur.execute(
                        "INSERT INTO comercios (comercio_id, nombre, categoria) VALUES (%s, %s, %s)",
                        (c_id, nombre, categoria)
                    )
                    st.success(f"✅ {nombre} guardado correctamente.")
                
                conn.commit()
                cur.close()
                conn.close()
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {e}")

# --- VISUALIZACIÓN Y ACCIONES ---
st.subheader("📋 Comercios Registrados")
try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT comercio_id, nombre, categoria FROM comercios ORDER BY id DESC")
    rows = cur.fetchall()
    
    if rows:
        # Encabezados de tabla
        h_col1, h_col2, h_col3, h_col4 = st.columns([2, 3, 2, 2])
        h_col1.write("**ID**")
        h_col2.write("**Nombre**")
        h_col3.write("**Categoría**")
        h_col4.write("**Acciones**")
        st.divider()

        for r in rows:
            col1, col2, col3, col4 = st.columns([2, 3, 2, 2])
            col1.write(r[0])
            col2.write(r[1])
            col3.write(r[2])
            
            # Botones de Acción
            btn_edit, btn_del = col4.columns(2)
            if btn_edit.button("✏️", key=f"edit_{r[0]}"):
                st.session_state.editing_id = r[0]
                st.rerun()
                
            if btn_del.button("🗑️", key=f"del_{r[0]}"):
                cur.execute("DELETE FROM comercios WHERE comercio_id = %s", (r[0],))
                conn.commit()
                st.rerun()
    else:
        st.info("No hay comercios registrados aún.")
    
    cur.close()
    conn.close()
except Exception as e:
    st.error(f"Error al leer la base de datos: {e}")