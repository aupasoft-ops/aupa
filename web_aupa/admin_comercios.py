import streamlit as st
from tables_comercios import crear_tablas, insertar_comercio, obtener_comercios, eliminar_comercio, actualizar_comercio

def main():
    st.title("🗄️ Administración de Comercios")
    crear_tablas()

    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False
        st.session_state.comercio_a_editar = None

    titulo_form = "✏️ Editar Comercio" if st.session_state.edit_mode else "➕ Registrar Nuevo Comercio"
    
    with st.expander(titulo_form, expanded=st.session_state.edit_mode):
        with st.form("form_comercio"):
            v_cid = st.session_state.comercio_a_editar['comercio_id'] if st.session_state.edit_mode else ""
            v_nom = st.session_state.comercio_a_editar['nombre'] if st.session_state.edit_mode else ""
            v_cat = st.session_state.comercio_a_editar['categoria'] if st.session_state.edit_mode else "Tienda"

            col1, col2 = st.columns(2)
            c_id = col1.text_input("ID de Comercio (Slug/Código)", value=v_cid)
            nombre = col2.text_input("Nombre del Comercio", value=v_nom)
            categoria = st.selectbox("Categoría", ["Restaurante", "Tienda", "Servicios", "Otros"], 
                                     index=["Restaurante", "Tienda", "Servicios", "Otros"].index(v_cat) if st.session_state.edit_mode else 1)
            
            submit_label = "Actualizar" if st.session_state.edit_mode else "Guardar"
            if st.form_submit_button(submit_label):
                if c_id and nombre:
                    if st.session_state.edit_mode:
                        actualizar_comercio(st.session_state.comercio_a_editar['id'], c_id, nombre, categoria)
                        st.success("✅ Actualizado")
                        st.session_state.edit_mode = False
                    else:
                        insertar_comercio(c_id, nombre, categoria)
                        st.success("✅ Guardado")
                    st.rerun()
                else:
                    st.error("⚠️ ID y Nombre son obligatorios.")
        
        if st.session_state.edit_mode:
            if st.button("Cancelar"):
                st.session_state.edit_mode = False
                st.rerun()

    st.subheader("📋 Lista de Comercios")
    df = obtener_comercios()
    
    if not df.empty:
        cols = st.columns([1, 2, 3, 2, 2])
        headers = ["ID DB", "Comercio ID", "Nombre", "Categoría", "Acciones"]
        for col, h in zip(cols, headers): col.write(f"**{h}**")
        st.divider()

        for _, row in df.iterrows():
            c1, c2, c3, c4, c5 = st.columns([1, 2, 3, 2, 2])
            c1.write(row['id']) 
            c2.write(row['comercio_id'])
            c3.write(row['nombre'])
            c4.write(row['categoria'])
            
            btn_edit, btn_del = c5.columns(2)
            
            if btn_del.button("🗑️", key=f"del_{row['id']}"):
                eliminar_comercio(row['id'])
                st.rerun()
            
            if btn_edit.button("✏️", key=f"edit_{row['id']}"):
                st.session_state.edit_mode = True
                st.session_state.comercio_a_editar = row
                st.rerun()
    else:
        st.info("No hay registros.")