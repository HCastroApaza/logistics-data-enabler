import streamlit as st

def mostrar():
    col_titulo, col_volver = st.columns([4, 1])
    with col_titulo:
        st.title("Métricas")
    with col_volver:
        st.write("")
        if st.button("← Volver al Inicio", use_container_width=True, key="volver_metricas"):
            st.session_state.vista_actual = 'Inicio'
            st.session_state.last_cap = None
            st.session_state.last_ger = None
            st.rerun()
            
    st.info("Esta sección está en desarrollo. Próximamente se agregarán indicadores clave.")