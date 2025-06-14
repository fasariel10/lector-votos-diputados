import streamlit as st
import requests
import numpy as np
import pandas as pd
from PIL import Image
import io

st.set_page_config(page_title="Lectura de Votos - Diputados", layout="wide")
st.title("📥 Extractor de Votos para Diputados por Imagen")
st.markdown("Subí una imagen de la planilla electoral para extraer el número de mesa y los votos de diputados.")

API_KEY = 'K85174237188957'

def ocr_space_api(imagen_bytes):
    response = requests.post(
        'https://api.ocr.space/parse/image',
        files={'filename': ('image.jpg', imagen_bytes)},
        data={'apikey': API_KEY, 'language': 'spa'}
    )
    result = response.json()
    if result.get('IsErroredOnProcessing'):
        return ""
    else:
        return result['ParsedResults'][0]['ParsedText']

def procesar_texto(texto):
    lineas = texto.splitlines()

    resultados = []
    mesa = ""
    for linea in lineas:
        linea = linea.strip()

        # Extraer número de mesa
        if "Mesa" in linea or "N° de Mesa" in linea or "Número de Mesa" in linea:
            partes = linea.split(" ")
            for p in partes:
                if p.isdigit():
                    mesa = p

        # Buscar líneas con votos para diputados
        if "Diputado" in linea or "Diputada" in linea or "Diputados" in linea:
            partes = linea.split()
            nombre_lista = " ".join(partes[:-1])
            try:
                voto = int(partes[-1])
            except:
                voto = "-"
            resultados.append({"Mesa": mesa, "Lista": nombre_lista, "Votos Diputados": voto})

    return resultados

imagenes_subidas = st.file_uploader("📸 Subí una o más imágenes", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if imagenes_subidas:
    todos_los_datos = []
    for imagen in imagenes_subidas:
        img_bytes = imagen.read()
        texto = ocr_space_api(img_bytes)
        datos = procesar_texto(texto)
        todos_los_datos.extend(datos)

    if todos_los_datos:
        df = pd.DataFrame(todos_los_datos)
        st.success("✅ Datos extraídos correctamente:")
        st.dataframe(df, use_container_width=True)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Votos Diputados')
        st.download_button("📥 Descargar Excel", data=output.getvalue(), file_name="votos_diputados.xlsx")
    else:
        st.warning("No se encontraron datos válidos en las imágenes.")
