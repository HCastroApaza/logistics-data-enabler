import pandas as pd
import urllib.parse
import unicodedata
import re

ID_WEB_APP = "AKfycbyGm99E8XYuBEL3sqKzj0njCYQFLITJ5qYekZQg5ZG53bD0VQzg5Cns6pQfkQTjsQJ5hQ"
URL_BASE_GAS = f"https://script.google.com/macros/s/{ID_WEB_APP}/exec"

def limpiar(valor):
    return "" if pd.isna(valor) else str(valor).strip()

def normalizar_texto(texto):
    if pd.isna(texto): return ""
    texto = str(texto).strip().upper()
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    return re.sub(r"[^A-Z0-9 ]", "", texto)

def procesar_fila(fila, nombre_cap):
    marca = limpiar(fila.get("Marca"))
    direccion = limpiar(fila.get("Dirección"))
    distrito = limpiar(fila.get("Distrito"))
    kam = limpiar(fila.get("KAM"))
    psi = limpiar(fila.get("PSI"))
    puntos = limpiar(fila.get("Puntos BBVA"))
    tipo_local = limpiar(fila.get("Centro Comercial o P.C.")) 
    indicaciones = limpiar(fila.get("Indicaciones para Visitas"))

    query = urllib.parse.quote(f"{marca} {direccion} {distrito} Lima Peru")
    maps_url = f"https://www.google.com/maps/search/{query}"
    google_url = f"https://www.google.com/search?q={query}"
    
    query_params = urllib.parse.urlencode({
        "comercio": marca, "dir": direccion, "kam": kam, "psi": psi,
        "puntos": puntos, "cap": nombre_cap, "tipo_local": tipo_local, "indicaciones": indicaciones
    })
    magic_link = f"{URL_BASE_GAS}?{query_params}"

    # --- CORRECCIÓN: Construcción dinámica de fórmulas para Excel ---
    formula_maps = f'=HYPERLINK("{maps_url}", "Ubicación en Maps")'
    formula_google = f'=HYPERLINK("{google_url}", "Buscar en Google")'
    formula_magic = f'=HYPERLINK("{magic_link}", "Reportar Visita")'

    return pd.Series([formula_maps, formula_google, formula_magic, maps_url, google_url, magic_link])