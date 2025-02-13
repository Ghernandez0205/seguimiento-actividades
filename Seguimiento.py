import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from office365.sharepoint.client_context import ClientContext
from msal import PublicClientApplication
import requests
from PIL import Image
import pyotp  # Biblioteca para autenticación TOTP
from fpdf import FPDF  # Biblioteca para crear PDFs

# Configuración de la interfaz
st.set_page_config(page_title="Registro Diario de Actividades", layout="wide")

# Configuración de autenticación con MSAL
CLIENT_ID = "38597832-95f3-4cde-973e-5af2618665dc"  # ID de aplicación de Azure
TENANT_ID = "2c9053b0-cfd0-484f-bc8f-5c045a175125"  # ID de Directorio (Inquilino)
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["Files.ReadWrite", "User.Read"]  # Permisos para OneDrive

# Usuario autorizado (Solo este usuario podrá acceder)
AUTHORIZED_EMAIL = "tu_correo@outlook.com"  # Reemplázalo con tu correo de Microsoft
AUTHORIZED_USER_ID = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"  # Reemplázalo con tu ID único de Microsoft

# Clave secreta para generar códigos en la App de Autenticador
SECRET_KEY = "JBSWY3DPEHPK3PXP"  # Genera una clave secreta y agrégala aquí

# Carpeta de almacenamiento de evidencias
BASE_STORAGE_PATH = "C:/Users/sup11/OneDrive/Attachments/Documentos/Interfaces de phyton/Proyecto almacenamiento interactivo/Visitas"

def generate_totp():
    """Genera el código dinámico TOTP."""
    totp = pyotp.TOTP(SECRET_KEY)
    return totp.now()

def verify_totp(user_code):
    """Verifica si el código TOTP ingresado es correcto."""
    totp = pyotp.TOTP(SECRET_KEY)
    return totp.verify(user_code)

def save_images_as_pdf(image_list, pdf_path):
    """Convierte una lista de imágenes en un único archivo PDF."""
    if image_list:
        pdf = FPDF()
        for img_path in image_list:
            pdf.add_page()
            pdf.image(img_path, x=10, y=10, w=190)
        pdf.output(pdf_path, "F")

def scan_and_save_pdf(activity_name):
    """Función para capturar imágenes con la cámara y guardarlas como un solo PDF."""
    st.write("📷 Escaneo de documentos")
    images = []
    for i in range(3):  # Permitir tomar hasta 3 fotos
        photo = st.camera_input(f"Tomar foto {i+1}")
        if photo is not None:
            fecha_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            mes_actual = datetime.now().strftime("%Y-%m")
            folder_path = os.path.join(BASE_STORAGE_PATH, mes_actual)
            os.makedirs(folder_path, exist_ok=True)
            file_path = os.path.join(folder_path, f"{activity_name}_{fecha_hora}_{i+1}.jpg")
            with open(file_path, "wb") as f:
                f.write(photo.getbuffer())
            images.append(file_path)
    
    if images:
        pdf_path = os.path.join(folder_path, f"{activity_name}_{fecha_hora}.pdf")
        save_images_as_pdf(images, pdf_path)
        st.success(f"✅ PDF guardado en {pdf_path}")

def upload_evidence_files(activity_name):
    """Función para seleccionar imágenes desde el dispositivo y guardarlas con la nomenclatura adecuada."""
    uploaded_files = st.file_uploader("Subir evidencias (imágenes)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
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
        st.success(f"✅ Evidencias guardadas en {folder_path}")

# Configuración de la aplicación como cliente público
app = PublicClientApplication(CLIENT_ID, authority=AUTHORITY, token_cache=None)

if "token" not in st.session_state:
    st.session_state["token"] = None
    st.session_state["token_expiration"] = datetime.now()
    st.session_state["user_email"] = None
    st.session_state["user_id"] = None
    st.session_state["totp_verified"] = False

if not st.session_state.get("token"):
    if st.button("Autenticarse con Microsoft"):
        authenticate()
else:
    if not st.session_state.get("totp_verified"):
        st.info("🔐 Introduce el código dinámico generado en tu App de Autenticador.")
        user_totp = st.text_input("Código TOTP", max_chars=6, type="password")
        if st.button("Verificar Código"):
            if verify_totp(user_totp):
                st.session_state["totp_verified"] = True
                st.success("✅ Autenticación completada con éxito.")
            else:
                st.error("🚫 Código incorrecto. Intenta de nuevo.")
                st.session_state["totp_verified"] = False
                st.experimental_rerun()
    else:
        st.success(f"Sesión activa como {st.session_state['user_email']}")
        
        # Escaneo y conversión a PDF
        activity_name = st.text_input("Nombre de la actividad:")
        if activity_name:
            scan_and_save_pdf(activity_name)
            upload_evidence_files(activity_name)
