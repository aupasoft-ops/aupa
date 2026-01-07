import psycopg2
import streamlit as st

def get_connection():
    """Establece la conexión base a PostgreSQL."""
    try:
        return psycopg2.connect(
            host="localhost",
            database="aupa",
            user="aupa",
            password="Aupasoftware2025*?",
            port="5432"
        )
    except Exception as e:
        st.error(f"❌ Error crítico de conexión: {e}")
        return None