import streamlit as st
import pandas as pd
import os
import cv2
import easyocr
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
CSV_AUDIT_PATH = os.path.join(BASE_PATH, "Registro_Auditoria.csv")

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

# **CREAR O ACTUALIZAR EL CSV DE AUDITORÍA**
def update_audit_csv(fecha, actividad, turno, documento, texto_ocr, fotos, meta):
    data = {
        "Fecha": [fecha],
        "Actividad": [actividad],
        "Turno": [turno],
        "Documento": [documento],
        "Texto OCR": [texto_ocr],
        "Fotos": [fotos],
        "Meta": [meta]
    }
    
    df = pd.DataFrame(data)
    
    if not os.path.exists(CSV_AUDIT_PATH):
        df.to_csv(CSV_AUDIT_PATH, index=False, mode='w', encoding='utf-8')
    else:
        df.to_csv(CSV_AUDIT_PATH, index=False, mode='a', header=False, encoding='utf-8')

# **CONVERSIÓN DE FOTO A PDF Y OCR USANDO EASYOCR**
reader = easyocr.Reader(['es'])

def process_document(image_path, pdf_path):
    img = Image.open(image_path).convert("RGB")
    img.save(pdf_path, "PDF", resolution=100.0)

    # Extraer texto con EasyOCR
    text_result = reader.readtext(image_path, detail=0)
    text_extracted = " ".join(text_result)

    return text_extracted

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

# **GUARDAR REGISTRO EN BASE DE DATOS Y CSV**
if st.button("Guardar Registro"):
    save_audit_record(fecha_actividad.strftime('%Y-%m-%d'), actividad, turno, pdf_path, text_extracted, ",".join(foto_paths), meta)
    update_audit_csv(fecha_actividad.strftime('%Y-%m-%d'), actividad, turno, pdf_path, text_extracted, ",".join(foto_paths), meta)
    st.success("✅ Registro guardado en la base de datos y auditoría.")

# **DESCARGA DE ZIP**
if st.button("Descargar ZIP de Auditoría"):
    zip_filename = os.path.join(ZIP_PATH, f"Registro_de_Actividades_{fecha_actividad.strftime('%Y-%m-%d')}.zip")
    with zipfile.ZipFile(zip_filename, "w") as zipf:
        zipf.write(CSV_AUDIT_PATH, os.path.basename(CSV_AUDIT_PATH))
        if os.path.exists(pdf_path):
            zipf.write(pdf_path, os.path.basename(pdf_path))
        for foto in foto_paths:
            foto_full_path = os.path.join(EVIDENCE_PATH, foto)
            if os.path.exists(foto_full_path):
                zipf.write(foto_full_path, os.path.basename(foto_full_path))

    with open(zip_filename, "rb") as f:
        st.download_button("⬇️ Descargar ZIP", f, file_name=os.path.basename(zip_filename))

