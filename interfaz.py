import streamlit as st
import pandas as pd
import urllib.parse
import unicodedata
import re
from datetime import datetime
from io import BytesIO

# Configuración inicial
st.set_page_config(page_title="🚀 Sistema de Rutas Inteligente", layout="wide")
st.title("🚀 Sistema de Rutas Inteligente + Enriquecedor")

# Configuración del Receptor (Apps Script)
ID_WEB_APP = "TU_ID_AQUI"
URL_BASE_GAS = f"https://script.google.com/macros/s/{ID_WEB_APP}/exec"

# Función de limpieza
def limpiar(valor):
    return "" if pd.isna(valor) else str(valor).strip()

# Función de normalización de nombres (quita tildes y caracteres especiales)
def normalizar_texto(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).strip().upper()
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    texto = re.sub(r"[^A-Z0-9 ]", "", texto)  # solo letras, números y espacios
    return texto

# Función para generar hipervínculos (Excel-friendly)
def procesar_fila(fila):
    marca = limpiar(fila.get("Marca"))
    direccion = limpiar(fila.get("Dirección"))
    distrito = limpiar(fila.get("Distrito"))
    kam = limpiar(fila.get("KAM"))
    psi = limpiar(fila.get("PSI"))

    query = urllib.parse.quote(f"{marca} {direccion} {distrito}")

    maps_url = f"https://www.google.com/maps/search/{query}"
    google_url = f"https://www.google.com/search?q={query}"
    magic_link = (
        f"{URL_BASE_GAS}?comercio={urllib.parse.quote(marca)}"
        f"&dir={urllib.parse.quote(direccion)}"
        f"&kam={urllib.parse.quote(kam)}"
        f"&psi={urllib.parse.quote(psi)}"
    )

    # Fórmulas Excel con hipervínculo
    maps_text = f'=HYPERLINK("{maps_url}", "LINK MAPS")'
    google_text = f'=HYPERLINK("{google_url}", "LINK GOOGLE")'
    magic_text = f'=HYPERLINK("{magic_link}", "AUTO-RELLENO")'

    return pd.Series([maps_text, google_text, magic_text])

# 📌 Cargar hoja Datos desde archivo fijo en el proyecto
df_datos_base = pd.read_excel("data/Datos.xlsx", sheet_name="Datos")

# Subida de archivo
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
        df = pd.read_excel(archivo, sheet_name=nombre_hoja)

        # Si se selecciona CC, reemplazar columna "Centro Comercial o P.C." con Dirección y Distrito usando df_datos_base
        if nombre_hoja == "CC":
            if "Centro Comercial o P.C." in df.columns:
                df['Centro Comercial_norm'] = df['Centro Comercial o P.C.'].apply(normalizar_texto)
                df_datos = df_datos_base.copy()
                df_datos['Centro Comercial_norm'] = df_datos['Centro Comercial'].apply(normalizar_texto)

                # Merge con Datos
                df = df.merge(
                    df_datos[['Centro Comercial_norm', 'Dirección', 'Distrito']],
                    on='Centro Comercial_norm',
                    how='left'
                )

                # Eliminar columna original
                df = df.drop(columns=['Centro Comercial o P.C.', 'Centro Comercial_norm'])
            else:
                st.error("❌ La hoja CC no contiene la columna 'Centro Comercial o P.C.'. Revisa tu archivo Excel.")

        # 2. Filtro de fecha (manejo robusto de valores inválidos)
        hoy = datetime.now().date()
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce').dt.date
        invalid_rows = df['Fecha'].isna().sum()
        df = df.dropna(subset=['Fecha'])

        if invalid_rows > 0:
            st.warning(f"⚠️ Se descartaron {invalid_rows} filas por tener fechas inválidas.")

        # Reordenar columnas al formato requerido
        columnas_finales = [
            "KAM", "Marca", "PSI", "Puntos BBVA",
            "Dirección", "Distrito", "Indicaciones para Visitas",
            "Fecha", "CAP"
        ]
        for col in columnas_finales:
            if col not in df.columns:
                df[col] = ""  # crear columna vacía si falta
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

                        # 4. Enriquecimiento con hipervínculos
                        df_final[['Link MAPS', 'Link GOOGLE', 'Auto-Relleno']] = df_final.apply(procesar_fila, axis=1)

                        # Mostrar tabla
                        st.dataframe(df_final)

                        # 5. Exportar Excel con hipervínculos
                        output = BytesIO()
                        df_final.to_excel(output, index=False, engine='openpyxl')
                        st.download_button(
                            "📥 Descargar Excel enriquecido",
                            data=output.getvalue(),
                            file_name=f"Ruta_{nombre_sel}_{fecha_sel}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                        # Mensaje final
                        st.success("✅ Archivo enriquecido listo para entregar al personal.")