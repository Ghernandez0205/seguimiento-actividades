import streamlit as st
import pandas as pd
import os
import zipfile
from datetime import datetime
from PIL import Image

# **CONFIGURACIÓN DE RUTAS LOCALES**
BASE_PATH = "C:/Users/sup11/OneDrive/Attachments/Documentos/Interfaces de phyton/Proyecto almacenamiento interactivo"
EVIDENCE_PATH = os.path.join(BASE_PATH, "Evidencia fotografica")
ZIP_PATH = os.path.join(BASE_PATH, "Zips")

# **CREAR CARPETAS SI NO EXISTEN**
os.makedirs(EVIDENCE_PATH, exist_ok=True)
os.makedirs(ZIP_PATH, exist_ok=True)

# **CONFIGURACIÓN DE STREAMLIT**
st.set_page_config(page_title="Registro de Actividades", layout="wide")
st.title("📂 Registro de Actividades en Streamlit")

# **SELECCIÓN DE ACTIVIDAD Y TURNO**
actividad = st.text_input("📌 Ingrese la actividad:")
fecha_actividad = st.date_input("📅 Seleccione la fecha de la actividad:")
turno = st.radio("⏰ Seleccione el turno:", ("Matutino (08:00 - 12:30)", "Vespertino (13:30 - 16:30)"))

# **SUBIDA DE ARCHIVO EXCEL DE METAS**
uploaded_file = st.file_uploader("📂 Cargar archivo de metas (Excel)", type=["xlsx"])
if uploaded_file is not None:
    meta_df = pd.read_excel(uploaded_file)
    meta = st.selectbox("🎯 Seleccione la meta correspondiente:", meta_df['Meta'].tolist())
    st.success("✅ Archivo cargado correctamente.")
else:
    meta = None

# **CAPTURA DE IMÁGENES Y ALMACENAMIENTO**
st.subheader("📸 Captura de Evidencias de la Actividad")
uploaded_files = st.file_uploader("📎 Subir hasta 3 imágenes", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

foto_paths = []
if uploaded_files:
    for i, file in enumerate(uploaded_files, 1):
        file_name = f"{actividad}-{fecha_actividad.strftime('%Y-%m-%d')}-{i:02}.jpg"
        file_path = os.path.join(EVIDENCE_PATH, file_name)
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
        foto_paths.append(file_path)
    st.success("✅ Evidencias guardadas correctamente.")

# **GENERACIÓN DE ARCHIVO ZIP**
def create_zip():
    zip_name = f"registro_de_actividades_{fecha_actividad.strftime('%Y%m%d')}.zip"
    zip_path = os.path.join(ZIP_PATH, zip_name)
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file_path in foto_paths:
            zipf.write(file_path, os.path.basename(file_path))
    return zip_path

if st.button("📥 Generar ZIP y Descargar"):
    if foto_paths:
        zip_path = create_zip()
        st.success(f"✅ Archivo ZIP generado: {zip_path}")
        with open(zip_path, "rb") as f:
            st.download_button("⬇️ Descargar ZIP", f, file_name=os.path.basename(zip_path))
    else:
        st.warning("⚠️ No hay imágenes para comprimir.")

st.info("📌 Recuerda que este ZIP será procesado por la interfaz local.")
