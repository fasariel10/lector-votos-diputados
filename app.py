import streamlit as st
import requests
import numpy as np
import pandas as pd
from PIL import Image
import io

st.set_page_config(page_title="Lectura de Votos - Diputados", layout="wide")
st.title("📥 Extractor de Votos para Diputados por Imagen")
st.markdown("Subí una imagen de la planilla electoral para extraer el número de mesa y los votos de diputados.")

API_KEY = 'K85174237188957'  # Tu clave de OCR.space

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
    mesa = ""
    resultados = []

    partidos = {
        "900 B MEJOR CIUDAD": "",
        "900 D ENCONTRARNOS RENOVADOS": "",
        "900 E CIUDAD SUSTENTABLE": "",
        "900 F LIBRES EN UNIÓN Y ORDEN": "",
        "900 G ENCUENTRO POR MI CIUDAD": "",
        "900 H RENOVANDO CON LA GENTE": "",
        "900 I LA CIUDAD QUE QUIERO": "",
        "900 J COMPROMISO RENOVADO": "",
        "900 K LA SALUD PRIMERO": "",
        "900 L TU VOZ, MI COMPROMISO": "",
        "900 M COMPROMISO CON VOS": "",
        "900 N PODES": "",
        "900 O POSDATA": "",
        "900 Q HACEMOS FUTURO": "",
        "900 S FUERZA LIBERAL": "",
        "900 X LA CIUDAD MÁS LINDA": "",
        "901-CONFLUENCIA POPULAR POR LA PATRIA": "",
        "901 ZAB COMPROMISO Y HONESTIDAD CON LA GENTE": "",
        "901 ZT DIGNIDAD Y TRABAJO": "",
        "901 ZG LA VOZ DEL BARRIO": "",
        "901 ZN CIUDAD HUMANA": "",
        "901 ZR UNIÓN POR LA PATRIA": "",
        "901 ZZ PARA RECUPERAR DERECHOS": "",
        "902-FRENTE UNIDOS POR EL FUTURO": "",
        "902 WF FUTURO": "",
        "902 ZM TE QUIERO CON FUTURO": "",
        "902 ZN UNIDOS POR NUESTRA CIUDAD": "",
        "902 ZS UNIDOS POR EL FUTURO": "",
        "902 ZT MARCANDO HUELLAS": "",
        "902 ZW PUEDE +": ""
    }

    # Buscar número de mesa
    for linea in lineas:
        if "mesa" in linea.lower():
            partes = linea.split()
            for p in partes:
                if p.isdigit():
                    mesa = p

    # Buscar filas con números manuscritos (suelen estar al final de la línea)
    for linea in lineas:
        partes = linea.rsplit(" ", 1)
        if len(partes) == 2 and partes[1].strip().isdigit():
            nombre_lista = partes[0].strip().upper()
            votos = int(partes[1].strip())

            for clave in partidos.keys():
                if clave in nombre_lista:
                    resultados.append({
                        "Mesa": mesa,
                        "Lista": clave,
                        "Votos Diputados": votos
                    })

    return resultados

imagenes_subidas = st.file_uploader("📸 Subí una o más imágenes", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if imagenes_subidas:
    todos_los_datos = []
    for imagen in imagenes_subidas:
        img_bytes = imagen.read()
        texto = ocr_space_api(img_bytes)
        
        st.text_area("📄 Texto OCR detectado:", texto, height=200)

        datos = procesar_texto(texto)
        todos_los_datos.extend(datos)

    if todos_los_datos:
        df = pd.DataFrame(todos_los_datos)
        st.success("✅ Datos extraídos correctamente:")
        st.dataframe(df, use_container_width=True)

        st.subheader("📊 Totales por Lista/Sublema")
        totales = df.groupby("Lista", as_index=False)["Votos Diputados"].sum()
        st.dataframe(totales, use_container_width=True)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Votos Diputados')
            totales.to_excel(writer, index=False, sheet_name='Totales por Lista')
        st.download_button("📥 Descargar Excel", data=output.getvalue(), file_name="votos_diputados.xlsx")
    else:
        st.warning("⚠️ No se encontraron datos válidos en las imágenes.")
