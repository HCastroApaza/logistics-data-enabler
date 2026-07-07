import streamlit as st

URL_BASE_APP_SCRIPT = "https://script.google.com/macros/s/AKfycbwuEm88zF8pAYBnsGfMmWhSA0bSKiO0Lh_xo9Iw9mLRzJIt2HbWfU_JEL4FktTe81yjMw/exec" 

def mostrar():
    col_titulo, col_volver = st.columns([4, 1])
    with col_titulo:
        # Título personalizado con tamaño reducido y color corporativo
        st.markdown("<h1 style='font-size: 32px; color: #f8fafc; margin-top: 0px;'>Reporte de Campañas</h1>", unsafe_allow_html=True)
    with col_volver:
        st.write("")
        if st.button("← Volver al Inicio", use_container_width=True, key="volver_campanas"):
            st.session_state.vista_actual = 'Inicio'
            st.session_state.last_cap = None
            st.session_state.last_ger = None
            st.rerun()
            
    st.markdown("<p style='color: #94a3b8; font-size: 18px; margin-top: -10px;'>Generar reporte de campaña.</p>", unsafe_allow_html=True)
    st.divider()

    url_campana = f"{URL_BASE_APP_SCRIPT}?tipo=campana"

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info(" Haz clic en el botón inferior para abrir el formulario.")
        st.link_button(" ABRIR FORMULARIO DE CAMPAÑA", url=url_campana, use_container_width=True)