import streamlit as st
import pandas as pd
import os
import zipfile
from datetime import datetime
from PIL import Image

# **CONFIGURACIÓN DE RUTAS**
BASE_PATH = "C:/Users/sup11/OneDrive/Attachments/Documentos/Interfaces de phyton/Proyecto almacenamiento interactivo"
EVIDENCE_PATH = os.path.join(BASE_PATH, "Evidencia fotografica")
ZIP_PATH = os.path.join(BASE_PATH, "Zips")
DOC_PATH = os.path.join(BASE_PATH, "Visitas")

# **CREAR CARPETAS SI NO EXISTEN**
os.makedirs(EVIDENCE_PATH, exist_ok=True)
os.makedirs(ZIP_PATH, exist_ok=True)
os.makedirs(DOC_PATH, exist_ok=True)

# **METAS IDENTIFICADAS DEL DOCUMENTO**
metas = [
    "Efectuar 3 Informes trimestrales del Programa de mejora de la supervisión",
    "Realizar 12 Informes (uno cada mes) de Actividades Relevantes",
    "Realizar seguimiento a la implementación de los planes de asesoría en los diferentes niveles educativos",
    "Realizar 10 jornadas académicas con la estructura de supervisión para fortalecer la comunicación interna",
    "Implementar acciones para la actualización sobre métodos de asesoría y comunicación asertiva",
    "Promover la participación de los PCD y ECAEF en los CTE para implementar el plan analítico",
    "Implementar una estrategia de intervención y colaboración en el Consejo Técnico Escolar",
    "Desarrollar una estrategia de acompañamiento en la implementación del Plan y Programas de Estudio",
    "Aplicar un plan de asesoría de Educación Física en educación básica",
    "Lograr la participación del 100% de docentes en el CTE",
    "Realizar asesoría y acompañamiento para el 100% de docentes con y sin perfil profesional",
    "Desarrollar una estrategia de intervención en el CTE y talleres intensivos de formación continua",
    "Desarrollar una estrategia de actualización sobre la propuesta curricular 2022",
    "Realizar al menos tres visitas trimestrales de asesoría a docentes de secundaria",
    "Implementar estrategias para proyectos de educación física estatales",
    "Diseñar una estrategia para la actividad física y el cuidado de la salud en el 100% de las escuelas",
    "Implementar al 100% las estrategias de fortalecimiento académico",
    "Diseñar e implementar las etapas de los Juegos Deportivos Escolares"
]

# **CONFIGURACIÓN DE STREAMLIT**
st.set_page_config(page_title="Registro de Actividades", layout="wide")
st.title("📂 Registro de Actividades en Streamlit")

# **SELECCIÓN DE ACTIVIDAD Y META**
actividad = st.text_input("📌 Ingrese la actividad:")
fecha_actividad = st.date_input("📅 Seleccione la fecha de la actividad:")
turno = st.radio("⏰ Seleccione el turno:", ("Matutino (08:00 - 12:30)", "Vespertino (13:30 - 16:30)"))
meta = st.selectbox("🎯 Seleccione la meta atendida:", metas)

# **SUBIDA DEL DOCUMENTO A CONVERTIR A PDF**
st.subheader("📄 Seleccione el documento en imagen que se convertirá en PDF")
documento = st.file_uploader("📎 Subir documento en formato JPG o PNG", type=["jpg", "jpeg", "png"])

# **SUBIDA DE FOTOGRAFÍAS COMO EVIDENCIA**
st.subheader("📎 Cargar hasta 3 fotos de la actividad")
uploaded_files = st.file_uploader("📎 Subir evidencias", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# **GUARDADO DE ARCHIVOS**
doc_path = ""
foto_paths = []

if documento:
    doc_name = f"Documento-{actividad}-{fecha_actividad.strftime('%Y-%m-%d')}.jpg"
    doc_path = os.path.join(DOC_PATH, doc_name)
    with open(doc_path, "wb") as f:
        f.write(documento.getbuffer())
    st.success("✅ Documento guardado correctamente.")

if uploaded_files:
    for i, file in enumerate(uploaded_files, 1):
        file_name = f"Evidencia-{actividad}-{fecha_actividad.strftime('%Y-%m-%d')}-{i:02}.jpg"
        file_path = os.path.join(EVIDENCE_PATH, file_name)
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
        foto_paths.append(file_path)
    st.success("✅ Evidencias guardadas correctamente.")

# **GENERACIÓN DE ARCHIVO ZIP**
def create_zip():
    zip_name = f"Registro_{actividad}_{fecha_actividad.strftime('%Y%m%d')}.zip"
    zip_path = os.path.join(ZIP_PATH, zip_name)
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        if documento:
            zipf.write(doc_path, os.path.basename(doc_path))
        for file_path in foto_paths:
            zipf.write(file_path, os.path.basename(file_path))
    return zip_path

if st.button("📥 Generar ZIP y Descargar"):
    if documento or foto_paths:
        zip_path = create_zip()
        st.success(f"✅ Archivo ZIP generado: {zip_path}")
        with open(zip_path, "rb") as f:
            st.download_button("⬇️ Descargar ZIP", f, file_name=os.path.basename(zip_path))
    else:
        st.warning("⚠️ No hay archivos para comprimir.")

st.info("📌 Recuerda que este ZIP será procesado por la interfaz local para generar auditorías.")
