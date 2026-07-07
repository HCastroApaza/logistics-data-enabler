import streamlit as st

def mostrar():
    # --- ENCABEZADO CENTRADO ---
    st.markdown(
        """
        <div style='text-align: center; margin-top: -15px; margin-bottom: 40px;'>
            <h1 style='color: #f8fafc; font-size: 35px; font-family: sans-serif; font-weight: bold;'>Sistema Gestión Integrada</h1>
            <p style='color: #94a3b8; font-size: 20px;'>Gestión centralizada de reportería, campañas y gerencia</p>
        </div>
        """, unsafe_allow_html=True
    )
    
    # --- CARDS DE NAVEGACIÓN ---
    col1, col2, col3 = st.columns(3, gap="medium")
    
    # Definimos las tarjetas
    cards = [
        {
            #"emoji": "📋", # Comentado para activar luego
            "title": "Plataforma de Rutas",
            "desc": "Completar y revisar visitas programadas.",
            "btn_text": "Ir a Visitas",
            "key": "btn_ir_visitas",
            "vista": "Plataforma de rutas",
            "color": "#38bdf8"
        },
        {
            #"emoji": "📢", # Comentado para activar luego
            "title": "Reporte de Campañas",
            "desc": "Generar reportes y gestión de eventos masivos.",
            "btn_text": "Ir a Campañas",
            "key": "btn_ir_campanas",
            "vista": "Reporte de Campañas",
            "color": "#14b8a6"
        },
        {
            #"emoji": "📈", # Comentado para activar luego
            "title": "Dashboard Gerencial",
            "desc": "Métricas, gráficas y KPIs operativos de gerencia.",
            "btn_text": "Ir a Dashboard",
            "key": "btn_ir_dashboard",
            "vista": "Dashboard",
            "color": "#f59e0b"
        }
    ]

    for i, col in enumerate([col1, col2, col3]):
        with col:
            # Altura 220 para ser compacto
            with st.container(height=220, border=True):
                
                # Espacio reservado para el emoji (puedes descomentar la línea de abajo cuando quieras)
                # st.markdown(f"<h1 style='text-align: center; font-size: 2rem;'>{cards[i].get('emoji', '')}</h1>", unsafe_allow_html=True)
                
                # Título
                st.markdown(f"<h4 style='text-align: center; color: {cards[i]['color']}; font-weight: bold; margin-bottom: 5px;'>{cards[i]['title']}</h4>", unsafe_allow_html=True)
                
                # Descripción estandarizada
                st.markdown(f"<p style='text-align: center; color: #94a3b8; font-size: 15px; margin-bottom: 15px;'>{cards[i]['desc']}</p>", unsafe_allow_html=True)
                
                # --- AQUÍ ESTÁ EL AJUSTE PARA EL BOTÓN MÁS ESTRECHO ---
                # Usamos columnas internas [1, 4, 1] para centrar y reducir el ancho
                _, c_btn, _ = st.columns([1, 4, 1]) 
                
                with c_btn:
                    if st.button(cards[i]['btn_text'], use_container_width=True, key=cards[i]['key']):
                        st.session_state.vista_actual = cards[i]['vista']
                        
                        # Lógica de navegación
                        if "Gerencial" in cards[i]['title']:
                            st.session_state.last_ger = cards[i]['vista']
                            st.session_state.last_cap = None
                        else:
                            st.session_state.last_cap = cards[i]['vista']
                            st.session_state.last_ger = None
                        st.rerun()