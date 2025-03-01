import streamlit as st
import pandas as pd
import os
import zipfile
from datetime import datetime
from PIL import Image

# **CONFIGURACIÓN DE RUTAS**
BASE_PATH = "C:/Users/sup11/OneDrive/Attachments/Documentos/Interfaces de phyton/Proyecto almacenamiento interactivo"
AUDIT_PATH = os.path.join(BASE_PATH, "Auditorias")
EVIDENCE_PATH = os.path.join(BASE_PATH, "Evidencia fotografica")
DOCUMENT_PATH = os.path.join(BASE_PATH, "Visitas")
ZIP_PATH = os.path.join(BASE_PATH, "Registros_ZIP")

# **CREAR CARPETAS SI NO EXISTEN**
os.makedirs(AUDIT_PATH, exist_ok=True)
os.makedirs(EVIDENCE_PATH, exist_ok=True)
os.makedirs(DOCUMENT_PATH, exist_ok=True)
os.makedirs(ZIP_PATH, exist_ok=True)

# **LISTA DE METAS**
metas = [
    "Efectuar 3 Informes trimestrales del Programa de mejora de la supervisión",
    "Realizar 12 Informes (uno cada mes) de Actividades Relevantes",
    "Realizar seguimiento a la implementación de los planes de asesoría en los diferentes niveles educativos",
    "Implementar estrategias para proyectos de educación física estatales",
    "Diseñar una estrategia para la actividad física y el cuidado de la salud en el 100% de las escuelas",
    "Implementar al 100% las estrategias de fortalecimiento académico",
    "Diseñar e implementar las etapas de los Juegos Deportivos Escolares"
]

# **LISTA DE CÓDIGOS PARA ATLAS.TI CON COLORES**
codigos_atlasti = {
    "Éxito en la Implementación": "🟢",
    "Desafíos y Obstáculos": "🟠",
    "Impacto Positivo": "🔵",
    "Requiere Mejoras": "🔴",
    "Participación Baja": "⚫",
    "Alta Eficiencia en Recursos": "🟣"
}

# **INTERFAZ DE STREAMLIT**
st.set_page_config(page_title="Registro de Actividades en Streamlit", layout="wide")
st.title("📂 Registro de Actividades en Streamlit")

# **SELECCIÓN DE ACTIVIDAD Y TURNO**
actividad = st.text_input("📌 Ingrese la actividad:")
fecha_actividad = st.date_input("📅 Seleccione la fecha de la actividad:")
turno = st.radio("⏰ Seleccione el turno:", ("Matutino (08:00 - 12:30)", "Vespertino (13:30 - 16:30)"))

# **SELECCIÓN DE META DESDE LISTA INTERNA**
st.subheader("🎯 Selección de la Meta Atendida")
meta_seleccionada = st.selectbox("Seleccione la meta atendida:", metas)

# **SELECCIÓN DE CÓDIGO PARA ATLAS.TI**
st.subheader("🏷️ Seleccionar Código para Atlas.ti")
codigo_atlasti = st.selectbox("Seleccione un código:", [f"{color} {codigo}" for codigo, color in codigos_atlasti.items()])

# **PREGUNTAS DE EVALUACIÓN PARA ANÁLISIS ESTADÍSTICO**
st.subheader("📊 Evaluación de la Actividad")
pregunta_1 = st.slider("Nivel de participación (1-10):", 1, 10, 5)
pregunta_2 = st.slider("Organización del evento (1-10):", 1, 10, 5)
pregunta_3 = st.slider("Impacto en los participantes (1-10):", 1, 10, 5)

# **SUBIDA DEL DOCUMENTO PRINCIPAL**
st.subheader("📄 Seleccione el documento principal en imagen")
documento = st.file_uploader("📎 Subir documento en formato JPG o PNG", type=["jpg", "jpeg", "png"])

# **CAPTURA DE EVIDENCIAS**
st.subheader("📸 Captura de Evidencias de la Actividad")
uploaded_files = st.file_uploader("Seleccione imágenes", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# **GUARDAR REGISTRO EN EXCEL**
if st.button("Guardar Registro de Auditoría"):
    audit_file = os.path.join(AUDIT_PATH, f"Auditoria_{fecha_actividad.strftime('%Y%m%d')}.xlsx")
    data = {
        "Fecha": [fecha_actividad.strftime('%Y-%m-%d')],
        "Actividad": [actividad],
        "Meta Atendida": [meta_seleccionada],
        "Turno": [turno],
        "Código Atlas.ti": [codigo_atlasti],
        "Nivel de Participación": [pregunta_1],
        "Organización del Evento": [pregunta_2],
        "Impacto en los Participantes": [pregunta_3]
    }
    df = pd.DataFrame(data)
    if os.path.exists(audit_file):
        df_existente = pd.read_excel(audit_file)
        df = pd.concat([df_existente, df], ignore_index=True)
    df.to_excel(audit_file, index=False)
    st.success("✅ Registro de auditoría guardado correctamente.")

    # **GUARDAR DOCUMENTO PRINCIPAL**
    if documento:
        doc_path = os.path.join(DOCUMENT_PATH, f"Visita_{actividad}_{fecha_actividad.strftime('%Y%m%d')}.jpg")
        with open(doc_path, "wb") as f:
            f.write(documento.getbuffer())
        st.success("✅ Documento guardado correctamente.")

    # **GUARDAR EVIDENCIAS**
    for idx, file in enumerate(uploaded_files):
        file_path = os.path.join(EVIDENCE_PATH, f"{actividad}_{fecha_actividad.strftime('%Y%m%d')}_evidencia{idx+1}.jpg")
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
    st.success("✅ Evidencias guardadas correctamente.")
