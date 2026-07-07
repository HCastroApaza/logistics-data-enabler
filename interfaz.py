import streamlit as st
import streamlit.components.v1 as components 
import vistas.inicio as inicio
import vistas.reporte_visitas as reporte_visitas
import vistas.reporte_campanas as reporte_campanas
import vistas.dashboard as dashboard
import vistas.metricas as metricas 

# --- CONFIGURACIÓN DE PÁGINA Y CSS ---
st.set_page_config(page_title="Portal Operativo Integrado", layout="wide", initial_sidebar_state="expanded")

def cargar_css(archivo):
    try:
        with open(archivo, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

cargar_css("assets/estilos.css")

URL_LOGO_REWARDS = "https://raw.githubusercontent.com/hcastro-rewards/Formulario_CAP/main/LOGO_REWARDS.png"
CLAVE_GERENCIA = "GER123"

# --- INICIALIZACIÓN DE VARIABLES DE SESIÓN ---
if 'vista_actual' not in st.session_state:
    st.session_state.vista_actual = 'Inicio'
if 'gerencia_desbloqueada' not in st.session_state:
    st.session_state.gerencia_desbloqueada = False
if 'dict_hojas' not in st.session_state:
    st.session_state['dict_hojas'] = None  
if 'cerrar_sidebar' not in st.session_state:
    st.session_state.cerrar_sidebar = False  

# --- INYECCIÓN JS: AUTO-CIERRE DE BARRA LATERAL (BÚSQUEDA FÍSICA DEL BOTÓN << ) ---
if st.session_state.cerrar_sidebar:
    components.html(
        """
        <script>
            // Sale del iframe y busca el botón de colapsar nativo de Streamlit en la ventana principal
            const parentDoc = window.parent.document;
            const closeBtn = parentDoc.querySelector('[data-testid="stSidebarCollapseButton"] button') || 
                             parentDoc.querySelector('[data-testid="stSidebarCollapseButton"]') ||
                             parentDoc.querySelector('button[kind="header"]');
            if (closeBtn) {
                closeBtn.click();
            }
        </script>
        """,
        height=0, width=0
    )
    st.session_state.cerrar_sidebar = False

# --- MODAL DE SEGURIDAD ---
@st.dialog("🔒 Acceso Restringido - Gerencia")
def modal_seguridad():
    st.write("Ingresa la clave de autorización para ver el Dashboard y módulos gerenciales.")
    clave = st.text_input("Contraseña", type="password", placeholder="••••••")
    
    if st.button("DESBLOQUEAR", use_container_width=True):
        if clave == CLAVE_GERENCIA:
            st.session_state.gerencia_desbloqueada = True
            st.session_state.vista_actual = 'Dashboard'
            st.session_state.cerrar_sidebar = True  # Dispara el auto-cierre
            st.rerun()
        else:
            st.error("❌ Contraseña incorrecta. Inténtalo de nuevo.")

# --- MENÚ LATERAL ---
with st.sidebar:
    st.markdown(f"<div style='text-align: center; margin-bottom: 30px;'><img src='{URL_LOGO_REWARDS}' width='100%'></div>", unsafe_allow_html=True)
        
    # --- SECCIÓN CAPACITADOR ---
    with st.expander("CAPACITACIÓN", expanded=(st.session_state.vista_actual in ["Plataforma de rutas", "Reporte de Campañas"])):
        
        if st.button("Plataforma de rutas", use_container_width=True):
            st.session_state.vista_actual = 'Plataforma de rutas'
            st.session_state.cerrar_sidebar = True  
            st.rerun()
            
        if st.button("Reporte de Campañas", use_container_width=True):
            st.session_state.vista_actual = 'Reporte de Campañas'
            st.session_state.cerrar_sidebar = True  
            st.rerun()

    # --- SECCIÓN GERENCIA ---
    with st.expander("GERENCIA", expanded=(st.session_state.vista_actual in ["Dashboard", "Métricas"])):
        
        if st.button("Dashboard", use_container_width=True):
            if not st.session_state.gerencia_desbloqueada:
                modal_seguridad()
            else:
                st.session_state.vista_actual = 'Dashboard'
                st.session_state.cerrar_sidebar = True  
                st.rerun()
                
        if st.button("Métricas", use_container_width=True):
            st.session_state.vista_actual = 'Métricas'
            st.session_state.cerrar_sidebar = True  
            st.rerun()

# --- ENRUTAMIENTO DE VISTAS ---
if st.session_state.vista_actual == 'Inicio':
    inicio.mostrar()
elif st.session_state.vista_actual == 'Plataforma de rutas':
    reporte_visitas.mostrar()
elif st.session_state.vista_actual == 'Reporte de Campañas':
    reporte_campanas.mostrar()
elif st.session_state.vista_actual == 'Dashboard':
    dashboard.mostrar()
elif st.session_state.vista_actual == 'Métricas':
    metricas.mostrar()