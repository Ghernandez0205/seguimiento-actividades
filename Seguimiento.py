import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
from PIL import Image

# **CONFIGURACIÓN DE RUTAS**
BASE_PATH = "C:/Users/sup11/OneDrive/Attachments/Documentos/Interfaces de phyton/Proyecto almacenamiento interactivo"
AUDIT_PATH = os.path.join(BASE_PATH, "Auditorias")
EVIDENCE_PATH = os.path.join(BASE_PATH, "Evidencia fotografica")
DOCUMENT_PATH = os.path.join(BASE_PATH, "Visitas")

# **CREAR CARPETAS SI NO EXISTEN**
os.makedirs(AUDIT_PATH, exist_ok=True)
os.makedirs(EVIDENCE_PATH, exist_ok=True)
os.makedirs(DOCUMENT_PATH, exist_ok=True)

# **CÓDIGOS ATLAS.TI Y COLORES**
codes_dict = {
    "Participación Activa": "🟢 Verde",
    "Baja Participación": "🟡 Amarillo",
    "Problemas Organizativos": "🔴 Rojo",
    "Éxito en la Implementación": "🟢 Verde",
    "Requiere Seguimiento": "🔵 Azul",
    "Impacto Social": "🟣 Morado"
}

# **LISTA DE METAS INTEGRADAS EN EL CÓDIGO**
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

# **SUBIDA DEL DOCUMENTO A CONVERTIR EN PDF**
st.subheader("📄 Seleccione el documento principal en imagen para convertir en PDF")
documento = st.file_uploader("📎 Subir documento en formato JPG o PNG", type=["jpg", "jpeg", "png"])

# **CAPTURA DE EVIDENCIAS**
st.subheader("📸 Captura de Evidencias de la Actividad")
uploaded_files = st.file_uploader("Seleccione imágenes", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# **SELECCIÓN DE CÓDIGO ATLAS.TI**
st.subheader("🏷️ Seleccionar Código para Atlas.ti")
codigo_seleccionado = st.selectbox("Seleccione un código:", list(codes_dict.keys()) + ["Otro"])

if codigo_seleccionado == "Otro":
    nuevo_codigo = st.text_input("Ingrese un nuevo código:")
    nuevo_color = st.color_picker("Seleccione un color para el código:")
    if nuevo_codigo:
        codes_dict[nuevo_codigo] = nuevo_color
        codigo_seleccionado = nuevo_codigo
        color_codigo = nuevo_color
    else:
        color_codigo = ""
else:
    color_codigo = codes_dict[codigo_seleccionado]

# **GUARDAR REGISTRO EN EXCEL**
if st.button("Guardar Registro de Auditoría"):
    audit_file = os.path.join(AUDIT_PATH, f"Auditoria_{fecha_actividad.strftime('%Y%m%d')}.xlsx")
    data = {
        "Fecha": [fecha_actividad.strftime('%Y-%m-%d')],
        "Actividad": [actividad],
        "Meta Atendida": [meta_seleccionada],
        "Turno": [turno],
        "Código_Atlas_TI": [codigo_seleccionado],
        "Color_Código": [color_codigo],
        "Observaciones": [""],
    }
    df = pd.DataFrame(data)
    if os.path.exists(audit_file):
        df_existente = pd.read_excel(audit_file)
        df = pd.concat([df_existente, df], ignore_index=True)
    df.to_excel(audit_file, index=False)
    st.success("✅ Registro de auditoría guardado correctamente.")

    # **GUARDAR DOCUMENTO PRINCIPAL**
    if documento:
        doc_name = f"Documento-{actividad}-{fecha_actividad.strftime('%Y-%m-%d')}.jpg"
        doc_path = os.path.join(DOCUMENT_PATH, doc_name)
        with open(doc_path, "wb") as f:
            f.write(documento.getbuffer())
        st.success("✅ Documento guardado correctamente.")

    # **GUARDAR EVIDENCIAS**
    for i, file in enumerate(uploaded_files, 1):
        file_name = f"{actividad}-{fecha_actividad.strftime('%Y-%m-%d')}-{i:02}.jpg"
        file_path = os.path.join(EVIDENCE_PATH, file_name)
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
    st.success("✅ Evidencias guardadas correctamente.")

