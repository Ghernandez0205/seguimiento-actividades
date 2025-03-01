import streamlit as st
import pandas as pd
import os
import zipfile
from datetime import datetime
from PIL import Image

# **CONFIGURACIÓN DE RUTAS**
BASE_PATH = "C:/Users/sup11/OneDrive/Attachments/Documentos/Interfaces de phyton/Proyecto almacenamiento interactivo"
ZIP_PATH = os.path.join(BASE_PATH, "Zips")

# **CREAR CARPETAS SI NO EXISTEN**
os.makedirs(ZIP_PATH, exist_ok=True)

# **INTERFAZ DE STREAMLIT**
st.set_page_config(page_title="Registro de Actividades", layout="wide")
st.title("📂 Registro de Actividades")

# **SELECCIÓN DE ACTIVIDAD Y TURNO**
actividad = st.text_input("📌 Ingrese la actividad:")
fecha_actividad = st.date_input("📅 Seleccione la fecha de la actividad:")
turno = st.radio("⏰ Seleccione el turno:", ("Matutino (08:00 - 12:30)", "Vespertino (13:30 - 16:30)"))

# **SUBIDA DE FOTOGRAFÍAS**
st.subheader("📎 Cargar hasta 3 fotos de la actividad")
uploaded_files = st.file_uploader("Seleccione imágenes", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# **GENERACIÓN DE ZIP PARA PROCESO LOCAL**
if st.button("Generar ZIP y Descargar"):
    if actividad and fecha_actividad and uploaded_files:
        zip_filename = f"{ZIP_PATH}/Registro_{actividad}_{fecha_actividad}.zip"
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for i, file in enumerate(uploaded_files, 1):
                file_name = f"{actividad}_{fecha_actividad}_{i:02}.jpg"
                file_path = os.path.join(ZIP_PATH, file_name)
                with open(file_path, "wb") as f:
                    f.write(file.getbuffer())
                zipf.write(file_path, os.path.basename(file_path))

        st.success(f"✅ ZIP generado correctamente: {zip_filename}")
        with open(zip_filename, "rb") as f:
            st.download_button(label="Descargar ZIP", data=f, file_name=os.path.basename(zip_filename), mime="application/zip")

    else:
        st.warning("⚠️ Debe ingresar todos los datos y subir al menos una imagen.")
