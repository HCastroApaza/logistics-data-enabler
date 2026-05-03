import streamlit as st
import pandas as pd
import urllib.parse
import unicodedata
import re
from datetime import datetime
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA CORPORATIVA ---
st.set_page_config(page_title="BBVA - Sistema de Rutas", layout="wide")

# --- ESTILOS CSS PERSONALIZADOS (MODO AZUL INTENSO BBVA) ---
st.markdown(
    """
    <style>
        .stApp { background-color: #072146; color: #FFFFFF !important; }
        [data-testid="stSidebar"] { background-color: #004481 !important; }
        h1, h2, h3, h4, p, label { color: #FFFFFF !important; }
        div.stButton > button:first-child { background-color: #004481 !important; color: #FFFFFF !important; border: 2px solid #FFFFFF; border-radius: 8px; font-weight: bold; }
        div.stButton > button:first-child:hover { background-color: #FFFFFF !important; color: #004481 !important; }
        div[data-testid="stFileUploadDropzone"] div { color: #FFFFFF !important; }
        
        /* Ajuste para alertas y avisos */
        .stAlert[data-baseweb="alert"] { background-color: rgba(26, 188, 156, 0.2); color: #FFFFFF !important; border: 1px solid #1abc9c; }
        .stAlert[data-baseweb="alert-warning"] { background-color: rgba(241, 196, 15, 0.2); color: #FFFFFF !important; border: 1px solid #f1c40f; }
        .stAlert[data-baseweb="alert-error"] { background-color: rgba(231, 76, 60, 0.2); color: #FFFFFF !important; border: 1px solid #e74c3c; }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<h1 style='text-align: center; color: white;'>BBVA</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: white; font-size: 1.2rem;'>Sistema de Rutas Inteligente</p>", unsafe_allow_html=True)
st.divider()

# --- CONFIGURACIÓN DEL RECEPTOR (APPS SCRIPT) ---
ID_WEB_APP = "AKfycbxZL8hCWSU3tYmSjr7oOSXIoPFpFITgqtNdTtmAOfma9k2kD4Lry17D5-PG4zVrsaTp"
URL_BASE_GAS = f"https://script.google.com/macros/s/{ID_WEB_APP}/exec"

# --- FUNCIONES DE LIMPIEZA Y PROCESAMIENTO ---
def limpiar(valor):
    return "" if pd.isna(valor) else str(valor).strip()

def normalizar_texto(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).strip().upper()
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    texto = re.sub(r"[^A-Z0-9 ]", "", texto)
    return texto

def procesar_fila(fila, nombre_cap):
    marca = limpiar(fila.get("Marca"))
    direccion = limpiar(fila.get("Dirección"))
    distrito = limpiar(fila.get("Distrito"))
    kam = limpiar(fila.get("KAM"))
    psi = limpiar(fila.get("PSI"))
    puntos = limpiar(fila.get("Puntos BBVA"))

    query = urllib.parse.quote(f"{marca} {direccion} {distrito} Lima Peru")

    maps_url = f"https://www.google.com/maps/search/{query}"
    google_url = f"https://www.google.com/search?q={query}"
    
    query_params = urllib.parse.urlencode({
        "comercio": marca,
        "dir": direccion,
        "kam": kam,
        "psi": psi,
        "puntos": puntos,
        "cap": nombre_cap
    })
    magic_link = f"{URL_BASE_GAS}?{query_params}"

    # Fórmulas de Excel (Se mantienen para el respaldo)
    maps_text = f'=HYPERLINK("{maps_url}", "LINK MAPS")'
    google_text = f'=HYPERLINK("{google_url}", "LINK GOOGLE")'
    magic_text = f'=HYPERLINK("{magic_link}", "AUTO-RELLENO")'

    # Retornamos ambas versiones: fórmulas para excel y raw URLs para la web interactiva
    return pd.Series([maps_text, google_text, magic_text, maps_url, google_url, magic_link])

# --- CARGA DE BASE MAESTRA ---
try:
    df_datos_base = pd.read_excel("data/Datos.xlsx", sheet_name="Datos")
except FileNotFoundError:
    st.error("No se encontró el archivo base 'Datos.xlsx' en la carpeta 'data'.")
    st.stop()

# --- INTERFAZ PRINCIPAL ---
archivo = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if archivo:
    xl = pd.ExcelFile(archivo)

    # 1. Selección de hoja
    tipo_visita = st.radio(
        "¿Qué tipo de visita tienes?",
        options=["PUERTA CALLE", "CENTRO COMERCIAL"],
        index=None
    )

    if tipo_visita:
        nombre_hoja = "PC" if tipo_visita == "PUERTA CALLE" else "CC"
        
        try:
            df = pd.read_excel(archivo, sheet_name=nombre_hoja)
        except ValueError:
            st.error(f"El archivo Excel subido no contiene la pestaña '{nombre_hoja}'. Revisa el formato.")
            st.stop()

        # Reemplazo de columna para Centro Comercial
        if nombre_hoja == "CC":
            if "Centro Comercial o P.C." in df.columns:
                df['Centro Comercial_norm'] = df['Centro Comercial o P.C.'].apply(normalizar_texto)
                df_datos = df_datos_base.copy()
                df_datos['Centro Comercial_norm'] = df_datos['Centro Comercial'].apply(normalizar_texto)

                df = df.merge(
                    df_datos[['Centro Comercial_norm', 'Dirección', 'Distrito']],
                    on='Centro Comercial_norm',
                    how='left'
                )
                df = df.drop(columns=['Centro Comercial o P.C.', 'Centro Comercial_norm'])
            else:
                st.error("La hoja CC no contiene la columna 'Centro Comercial o P.C.'. Revisa tu archivo Excel.")
                st.stop()

        # 2. Seguro Anti-Errores para Columna 'Fecha'
        if 'Fecha' not in df.columns:
            st.error("El archivo Excel no contiene la columna 'Fecha'. Por favor, verifica el encabezado original.")
            st.stop()

        hoy = datetime.now().date()
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce').dt.date
        invalid_rows = df['Fecha'].isna().sum()
        df = df.dropna(subset=['Fecha'])

        if invalid_rows > 0:
            st.warning(f"Se descartaron {invalid_rows} filas por tener fechas o formatos inválidos.")

        # Reordenar columnas
        columnas_finales = [
            "KAM", "Marca", "PSI", "Puntos BBVA",
            "Dirección", "Distrito", "Indicaciones para Visitas",
            "Fecha", "CAP"
        ]
        for col in columnas_finales:
            if col not in df.columns:
                df[col] = "" 
        df = df[columnas_finales]

        fechas_futuras = sorted([f for f in df['Fecha'].unique() if f >= hoy])

        if not fechas_futuras:
            st.warning("No hay rutas programadas para hoy o fechas futuras.")
        else:
            fecha_sel = st.selectbox("¿Qué fecha?", options=fechas_futuras)

            if fecha_sel:
                # 3. Selección de CAP
                nombre_sel = st.radio(
                    "¿Cuál es tu nombre?",
                    options=["Augusto", "Gustavo", "Harold", "Ivan", "Mateo"],
                    index=None
                )

                if nombre_sel:
                    # Filtrado final
                    df_final = df[(df['Fecha'] == fecha_sel) & (df['CAP'] == nombre_sel)].copy()

                    if df_final.empty:
                        st.info(f"No hay rutas para {nombre_sel} el {fecha_sel}.")
                    else:
                        st.success(f"Se encontraron {len(df_final)} locales para visitar.")

                        # 4. Enriquecimiento con hipervínculos (Web y Excel)
                        columnas_generadas = ['Link MAPS (Excel)', 'Link GOOGLE (Excel)', 'Auto-Relleno (Excel)', 'URL_MAPS', 'URL_GOOGLE', 'URL_MAGIC']
                        df_final[columnas_generadas] = df_final.apply(lambda x: procesar_fila(x, nombre_sel), axis=1)
                        
                        st.divider()
                        st.subheader("Panel de Ruta Interactivo (Directo en Web)")
                        st.info("Haz clic en 'Abrir Formulario' directamente desde esta tabla para reportar tu visita sin descargar el Excel.")

                        # Mostrar tabla configurada para Links Web
                        st.dataframe(
                            df_final,
                            column_config={
                                "URL_MAGIC": st.column_config.LinkColumn(
                                    "REPORTAR VISITA", 
                                    display_text="Abrir Formulario"
                                ),
                                "URL_MAPS": st.column_config.LinkColumn(
                                    "MAPS", 
                                    display_text="Ir a Maps"
                                ),
                                # Ocultamos las columnas que son exclusivas del Excel
                                "Link MAPS (Excel)": None,
                                "Link GOOGLE (Excel)": None,
                                "Auto-Relleno (Excel)": None,
                                "URL_GOOGLE": None
                            },
                            use_container_width=True,
                            hide_index=True
                        )

                        # 5. Exportar Excel tradicional
                        # Limpiamos las URLs puras para que el Excel solo tenga las fórmulas
                        df_excel = df_final.drop(columns=['URL_MAPS', 'URL_GOOGLE', 'URL_MAGIC'])
                        
                        output = BytesIO()
                        df_excel.to_excel(output, index=False, engine='openpyxl')
                        st.download_button(
                            "(Opcional) Descargar Excel tradicional",
                            data=output.getvalue(),
                            file_name=f"Ruta_{nombre_sel}_{fecha_sel}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                        st.success("Archivo enriquecido listo por si lo necesitas offline.")