import streamlit as st
import os
from datetime import datetime
from fpdf import FPDF  # Para crear PDFs
from PIL import Image

# Configuración de la aplicación
st.set_page_config(page_title="Registro Diario de Actividades", layout="wide")

# Carpeta de almacenamiento de evidencias
BASE_STORAGE_PATH = "C:/Users/sup11/OneDrive/Attachments/Documentos/Interfaces de phyton/Proyecto almacenamiento interactivo/Visitas"

def save_images_as_pdf(image_list, pdf_path):
    """Convierte imágenes en un archivo PDF."""
    if image_list:
        pdf = FPDF()
        for img_path in image_list:
            pdf.add_page()
            pdf.image(img_path, x=10, y=10, w=190)
        pdf.output(pdf_path, "F")

def upload_evidence_files(activity_name):
    """Subir imágenes desde el dispositivo y guardarlas con la nomenclatura adecuada."""
    uploaded_files = st.file_uploader("📂 Subir evidencias (imágenes)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    
    if uploaded_files:
        fecha_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        mes_actual = datetime.now().strftime("%Y-%m")
        folder_path = os.path.join(BASE_STORAGE_PATH, mes_actual)
        os.makedirs(folder_path, exist_ok=True)
        file_paths = []
        
        for i, file in enumerate(uploaded_files):
            file_path = os.path.join(folder_path, f"{activity_name}_{fecha_hora}_evidencia_{i+1}.jpg")
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
            file_paths.append(file_path)
        
        # Guardar como PDF
        pdf_path = os.path.join(folder_path, f"{activity_name}_{fecha_hora}.pdf")
        save_images_as_pdf(file_paths, pdf_path)
        
        st.success(f"✅ Evidencias guardadas en {folder_path}")
        st.success(f"📄 PDF generado: {pdf_path}")

# UI
activity_name = st.text_input("📌 Nombre de la actividad:")

if activity_name:
    upload_evidence_files(activity_name)
