import streamlit as st
import pandas as pd
import os
import cv2
import pytesseract
import sqlite3
import zipfile
from datetime import datetime
from fpdf import FPDF
from PIL import Image

# **CONFIGURACIÓN DE RUTAS**
BASE_PATH = "C:/Users/sup11/OneDrive/Attachments/Documentos/Interfaces de phyton/Proyecto almacenamiento interactivo"
VISIT_PATH = os.path.join(BASE_PATH, "Visitas")
EVIDENCE_PATH = os.path.join(BASE_PATH, "Evidencia fotografica")
DB_PATH = os.path.join(BASE_PATH, "auditoria.sqlite")
ZIP_PATH = os.path.join(BASE_PATH, "Zips")

# **CREAR BASE DE DATOS SI NO EXISTE**
def create_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS auditoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            actividad TEXT,
            turno TEXT,
            documento TEXT,
            texto_ocr TEXT,
            fotos TEXT,
            meta TEXT
        )
    ''')
    conn.commit()
    conn.close()

# **GUARDAR REGISTRO EN BASE DE DATOS**
def save_audit_record(fecha, actividad, turno, documento, texto_ocr, fotos, meta):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO auditoria (fecha, actividad, turno, documento, texto_ocr, fotos, meta) 
                      VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                   (fecha, actividad, turno, documento, texto_ocr, fotos, meta))
    conn.commit()
    conn.close()

# **CONVERSIÓN DE FOTO A PDF Y OCR**
def process_document(image_path, pdf_path):
    img = Image.open(image_path).convert("RGB")
    img.save(pdf_path, "PDF", resolution=100.0)
    
    text = pytesseract.image_to_string(cv2.imread(image_path))
    return text

# **INTERFAZ DE STREAMLIT**
st.set_page_config(page_title="Registro de Actividades", layout="wide")
st.title("📂 Registro de Actividades con OCR")

# **SELECCIÓN DE ACTIVIDAD Y TURNO**
actividad = st.text_input("📌 Ingrese la actividad:")
fecha_actividad = st.date_input("📅 Seleccione la fecha de la actividad:")
turno = st.radio("⏰ Seleccione el turno:", ("Matutino (08:00 - 12:30)", "Vespertino (13:30 - 16:30)"))

# **PROCESAMIENTO DE DOCUMENTO CON OCR**
st.subheader("📸 Captura de documento y conversión a PDF con OCR")
captured_photo = st.camera_input("Capturar documento")
if captured_photo:
    img_path = os.path.join(VISIT_PATH, f"Visita-{actividad}-{fecha_actividad.strftime('%Y-%m-%d')}.jpg")
    pdf_path = img_path.replace(".jpg", ".pdf")
    with open(img_path, "wb") as f:
        f.write(captured_photo.getbuffer())
    text_extracted = process_document(img_path, pdf_path)
    st.success(f"✅ Documento procesado y guardado localmente.")

# **SUBIDA DE FOTOGRAFÍAS**
st.subheader("📎 Cargar hasta 3 fotos de la actividad")
uploaded_files = st.file_uploader("Seleccione imágenes", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
foto_paths = []
if uploaded_files:
    for i, file in enumerate(uploaded_files, 1):
        file_name = f"{actividad}-{fecha_actividad.strftime('%Y-%m-%d')}-{i:02}.jpg"
        file_path = os.path.join(EVIDENCE_PATH, file_name)
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
        foto_paths.append(file_name)
    st.success("✅ Evidencias guardadas correctamente.")

# **SELECCIÓN DE META**
st.subheader("🎯 Seleccionar Meta de Actividad")
meta_df = pd.read_excel("/mnt/data/Avance de metas 24-25.xlsx")
meta = st.selectbox("Seleccione la meta correspondiente:", meta_df['Meta'].tolist())

# **GUARDAR REGISTRO EN BASE DE DATOS**
if st.button("Guardar Registro"):
    save_audit_record(fecha_actividad.strftime('%Y-%m-%d'), actividad, turno, pdf_path, text_extracted, ",".join(foto_paths), meta)
    st.success("✅ Registro guardado en la base de datos.")
