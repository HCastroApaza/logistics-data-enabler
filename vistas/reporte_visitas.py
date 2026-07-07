import streamlit as st
import pandas as pd
import re
import pytz  # <-- NUEVA LIBRERÍA DE ZONA HORARIA
from datetime import datetime, timedelta
from io import BytesIO
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from modulos.procesamiento_datos import normalizar_texto, procesar_fila

URL_BASE_DATOS_GS = "https://docs.google.com/spreadsheets/d/186GinOg7PgFcp1g9LAmW32K5vlTEK8ChYjI3qnsf1-4/edit?usp=sharing"

def mostrar():
    col_titulo, col_volver = st.columns([4, 1])
    with col_titulo:
        st.markdown("<h1 style='font-size: 32px; padding-top: 0rem;'>Plataforma de rutas inteligentes</h1>", unsafe_allow_html=True)
    with col_volver:
        st.write("") # Alineación vertical
        if st.button("← Volver al Inicio", use_container_width=True, key="volver_visitas"):
            st.session_state.vista_actual = 'Inicio'
            st.session_state.last_cap = None
            st.session_state.last_ger = None
            st.rerun()
    
    try:
        df_datos_base = pd.read_excel("data/Datos.xlsx", sheet_name="Datos")
    except FileNotFoundError:
        st.error("No se encontró el archivo base 'Datos.xlsx' en la carpeta 'data'.")
        st.stop()

    if st.session_state['dict_hojas'] is None:
        st.info("El sistema está listo para conectarse a la base de datos en la nube.")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 Sincronizar Rutas en Vivo", use_container_width=True):
                with st.spinner("Descargando datos desde Google Sheets..."):
                    match = re.search(r"/d/([a-zA-Z0-9-_]+)", URL_BASE_DATOS_GS)
                    if match:
                        sheet_id = match.group(1)
                        excel_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
                        try:
                            st.session_state['dict_hojas'] = pd.read_excel(excel_url, sheet_name=None)
                            st.rerun() 
                        except Exception as e:
                            st.error(f"Error al descargar datos: {e}")
                    else:
                        st.error("Enlace de Google Sheet no válido.")
    else:
        col_estado, col_boton = st.columns([3, 1])
        with col_estado:
            st.success("✅ Datos sincronizados correctamente.")
        with col_boton:
            if st.button("Refrescar Datos"):
                st.session_state['dict_hojas'] = None
                st.rerun()
                
        st.divider()

        df_pc_raw = st.session_state['dict_hojas'].get("PC 2026 - 2")
        df_cc_raw = st.session_state['dict_hojas'].get("CC 2026 - 2")
        df_cap_raw = st.session_state['dict_hojas'].get("CAPACITACIONES")

        # --- AQUÍ ESTÁ LA CORRECCIÓN DE LA HORA (LIMA, PERÚ) ---
        zona_lima = pytz.timezone('America/Lima')
        hoy = datetime.now(zona_lima).date()
        
        opciones_fechas = {
            f"Ayer ({(hoy - timedelta(days=1)).strftime('%Y-%m-%d')})": hoy - timedelta(days=1),
            f"Hoy ({hoy.strftime('%Y-%m-%d')})": hoy,
            f"Mañana ({(hoy + timedelta(days=1)).strftime('%Y-%m-%d')})": hoy + timedelta(days=1)
        }
        
        col_f, col_n = st.columns(2)
        with col_f:
            fecha_str = st.selectbox("¿Qué fecha deseas consultar?", options=list(opciones_fechas.keys()), index=None)
        with col_n:
            nombre_sel = st.selectbox("¿Cuál es tu nombre?", options=["Augusto", "Flor", "Gustavo", "Harold", "Ivan", "Mateo"], index=None)

        if fecha_str and nombre_sel:
            fecha_sel = opciones_fechas[fecha_str]
            st.divider()
            
            encontro_datos = False 

            def mostrar_modulo(df_final, titulo):
                st.markdown(f"<h3 style='color: #38bdf8 !important;'> {titulo}</h3>", unsafe_allow_html=True)
                
                columnas_generadas = ['Link MAPS (Excel)', 'Link GOOGLE (Excel)', 'Auto-Relleno (Excel)', 'URL_MAPS', 'URL_GOOGLE', 'URL_MAGIC']
                df_final[columnas_generadas] = df_final.apply(lambda x: procesar_fila(x, nombre_sel), axis=1)

                gb = GridOptionsBuilder.from_dataframe(df_final)
                
                cols_to_hide = ['Link MAPS (Excel)', 'Link GOOGLE (Excel)', 'Auto-Relleno (Excel)', 'URL_GOOGLE', 'Indicaciones para Visitas', 'Fecha', 'CAP']
                for col in cols_to_hide:
                    gb.configure_column(col, hide=True)

                gb.configure_default_column(
                    resizable=True, filter=False, sortable=False, suppressMenu=True, suppressMovable=True, 
                    minWidth=180, wrapText=True, autoHeight=True,
                    cellStyle={'fontSize': '14px', 'whiteSpace': 'normal', 'padding': '10px 15px', 'backgroundColor': '#0f172a', 'color': '#f8fafc'} 
                )

                cell_renderer_btns = JsCode('''
                class BtnCellRenderer {
                    init(params) {
                        this.eGui = document.createElement('div');
                        this.eGui.style.display = 'flex';
                        this.eGui.style.alignItems = 'center';
                        this.eGui.style.justifyContent = 'center';
                        this.eGui.style.height = '100%';
                        let label = params.colDef.headerName === "REPORTAR" ? "VISITA" : "MAPS";
                        let bgColor = params.colDef.headerName === "REPORTAR" ? "#38bdf8" : "#f59e0b";
                        this.eGui.innerHTML = `
                         <a href="${params.value}" target="_blank" style="
                            display: inline-block; width: 90%; background-color: ${bgColor}; color: #0f172a;
                            text-align: center; border-radius: 5px; text-decoration: none; font-weight: bold;
                            padding: 8px 0; font-size: 12px; line-height: 1; box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                        ">${label}</a>`;
                    }
                    getGui() { return this.eGui; }
                }
                ''')

                gb.configure_column("URL_MAGIC", headerName="REPORTAR", cellRenderer=cell_renderer_btns, pinned='right', width=100, minWidth=100, maxWidth=100)
                gb.configure_column("URL_MAPS", headerName="UBICAR", cellRenderer=cell_renderer_btns, pinned='right', width=100, minWidth=100, maxWidth=100)
                gb.configure_grid_options(headerHeight=50, rowHeight=60) 
                
                custom_css = {
                    ".ag-root-wrapper": {"background-color": "#1e293b", "border-color": "#334155"},
                    ".ag-header": {"background-color": "#0f172a", "color": "#94a3b8", "border-bottom": "1px solid #334155"},
                    ".ag-row": {"background-color": "#1e293b", "color": "#f8fafc", "border-bottom": "1px solid #334155"},
                    ".ag-row-hover": {"background-color": "#334155 !important"},
                }

                gridOptions = gb.build()

                AgGrid(
                    df_final,
                    gridOptions=gridOptions,
                    allow_unsafe_jscode=True, 
                    fit_columns_on_grid_load=False,
                    theme='streamlit', 
                    custom_css=custom_css 
                )

                df_excel = df_final.copy()
                cols_existentes = [col for col in ['URL_MAPS', 'URL_GOOGLE', 'URL_MAGIC', 'Auto-Relleno (Excel)', '::auto_unique_id::'] if col in df_excel.columns]
                df_excel = df_excel.drop(columns=cols_existentes)
                df_excel = df_excel.loc[:, ~df_excel.columns.str.contains('^Unnamed')]

                output = BytesIO()
                df_excel.to_excel(output, index=False, engine='openpyxl')
                
                st.download_button(
                    f"Descargar Excel - {titulo}",
                    data=output.getvalue(),
                    file_name=f"Ruta_{titulo.replace(' ', '_')}_{nombre_sel}_{fecha_sel}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"btn_{titulo}" 
                )
                st.divider()

            if df_pc_raw is not None and 'Fecha' in df_pc_raw.columns:
                df_pc = df_pc_raw.copy()
                df_pc['Fecha'] = pd.to_datetime(df_pc['Fecha'], errors='coerce').dt.date
                df_pc_filtrado = df_pc[(df_pc['Fecha'] == fecha_sel) & (df_pc['CAP'] == nombre_sel)].copy()
                
                if not df_pc_filtrado.empty:
                    encontro_datos = True
                    df_pc_filtrado['Centro Comercial o P.C.'] = "PUERTA CALLE"
                    columnas_pc = ["KAM", "Marca", "PSI", "Puntos BBVA", "Centro Comercial o P.C.", "Dirección", "Distrito", "Indicaciones para Visitas", "Fecha", "CAP"]
                    for col in columnas_pc:
                        if col not in df_pc_filtrado.columns: df_pc_filtrado[col] = ""
                    mostrar_modulo(df_pc_filtrado[columnas_pc], "PUERTA CALLE")

            if df_cc_raw is not None and 'Fecha' in df_cc_raw.columns:
                df_cc = df_cc_raw.copy()
                df_cc['Fecha'] = pd.to_datetime(df_cc['Fecha'], errors='coerce').dt.date
                df_cc_filtrado = df_cc[(df_cc['Fecha'] == fecha_sel) & (df_cc['CAP'] == nombre_sel)].copy()
                
                if not df_cc_filtrado.empty:
                    encontro_datos = True
                    if "Centro Comercial o P.C." in df_cc_filtrado.columns:
                        df_cc_filtrado['Centro Comercial_norm'] = df_cc_filtrado['Centro Comercial o P.C.'].apply(normalizar_texto)
                        df_datos = df_datos_base.copy()
                        df_datos['Centro Comercial_norm'] = df_datos['Centro Comercial'].apply(normalizar_texto)

                        columnas_a_borrar = [col for col in ['Dirección', 'Distrito'] if col in df_cc_filtrado.columns]
                        if columnas_a_borrar: df_cc_filtrado = df_cc_filtrado.drop(columns=columnas_a_borrar)
                        df_cc_filtrado = df_cc_filtrado.merge(df_datos[['Centro Comercial_norm', 'Dirección', 'Distrito']], on='Centro Comercial_norm', how='left')
                    
                    columnas_cc = ["KAM", "Marca", "PSI", "Puntos BBVA", "Centro Comercial o P.C.", "Dirección", "Distrito", "Indicaciones para Visitas", "Fecha", "CAP"]
                    for col in columnas_cc:
                        if col not in df_cc_filtrado.columns: df_cc_filtrado[col] = ""
                    mostrar_modulo(df_cc_filtrado[columnas_cc], "CENTRO COMERCIAL")

            if df_cap_raw is not None and 'Fecha' in df_cap_raw.columns:
                df_cap = df_cap_raw.copy()
                df_cap['Fecha'] = pd.to_datetime(df_cap['Fecha'], errors='coerce').dt.date
                df_cap_filtrado = df_cap[(df_cap['Fecha'] == fecha_sel) & (df_cap['CAP'] == nombre_sel)].copy()
                
                if not df_cap_filtrado.empty:
                    encontro_datos = True
                    mostrar_modulo(df_cap_filtrado, "CAPACITACIONES")

            if not encontro_datos:
                st.warning(f"No tienes rutas ni capacitaciones asignadas para el {fecha_sel}.")