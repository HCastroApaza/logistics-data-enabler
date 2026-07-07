import streamlit as st

def mostrar():
    col_titulo, col_volver = st.columns([4, 1])
    with col_titulo:
        st.title("Dashboard Gerencial")
    with col_volver:
        st.write("")
        if st.button("← Volver al Inicio", use_container_width=True, key="volver_dashboard"):
            st.session_state.vista_actual = 'Inicio'
            st.session_state.last_cap = None
            st.session_state.last_ger = None
            st.rerun()
            
    if st.session_state.gerencia_desbloqueada:
        st.success("Acceso autorizado. Bienvenido al panel de control de gerencia.")
        st.info("Esta sección está en desarrollo. Próximamente se agregarán gráficas.")
    else:
        st.error("🔒 Acceso denegado. Por favor, utiliza el menú lateral 'GERENCIA' para ingresar tu clave.")