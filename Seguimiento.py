import streamlit as st
import pandas as pd
import os
import requests
import pyotp
from datetime import datetime
from msal import PublicClientApplication
from fpdf import FPDF
from PIL import Image
import time

# **CONFIGURACIÓN DE AZURE AD**
CLIENT_ID = "38597832-95f3-4cde-973e-5af2618665dc"
TENANT_ID = "2c905b0-cfd0-484f-bc8f-5c045a175125"
CLIENT_SECRET = "TU_SECRETO_DE_CLIENTE"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["Files.ReadWrite", "User.Read"]

# **CONFIGURACIÓN DE AUTENTICACIÓN (TOTP)**
SECRET_KEY = "JBSWY3DPEHPK3PXP"

# **RUTAS DE GUARDADO (Forzando rutas correctas en OneDrive)**
BASE_STORAGE_PATH = r"C:\Users\sup11\OneDrive\Attachments\Documentos\Interfaces de phyton\Proyecto almacenamiento interactivo"
VISIT_STORAGE_PATH = os.path.join(BASE_STORAGE_PATH, "Visitas")
EVIDENCE_STORAGE_PATH = os.path.join(BASE_STORAGE_PATH, "Evidencia fotografica")
AUDIT_FILE = os.path.join(BASE_STORAGE_PATH, "registro_auditoria.xlsx")
AUDIT_CSV_FILE = os.path.join(BASE_STORAGE_PATH, "registro_auditoria.csv")

# **Verificar y Crear Directorios si No Existen**
for path in [BASE_STORAGE_PATH, VISIT_STORAGE_PATH, EVIDENCE_STORAGE_PATH]:
    os.makedirs(path, exist_ok=True)

# **CONFIGURACIÓN DE STREAMLIT**
st.set_page_config(page_title="Registro de Visitas", layout="wide")

# **FUNCIÓN PARA AUTENTICACIÓN**
def verify_totp(user_code):
    totp = pyotp.TOTP(SECRET_KEY)
    return totp.verify(user_code)

# **FUNCIÓN PARA GUARDAR EN EXCEL Y CSV**
def save_to_audit(data):
    df = pd.DataFrame([data])
    
    # Guardar en Excel
    if os.path.exists(AUDIT_FILE):
        df_existing = pd.read_excel(AUDIT_FILE, engine="openpyxl")
        df = pd.concat([df_existing, df], ignore_index=True)
    df.to_excel(AUDIT_FILE, index=False, engine="openpyxl")

    # Guardar en CSV
    if os.path.exists(AUDIT_CSV_FILE):
        df_existing_csv = pd.read_csv(AUDIT_CSV_FILE)
        df = pd.concat([df_existing_csv, df], ignore_index=True)
    df.to_csv(AUDIT_CSV_FILE, index=False)

    st.success(f"✅ Auditoría guardada en: {AUDIT_FILE}")

# **FUNCIÓN PARA GUARDAR IMAGEN COMO PDF**
def save_image_as_pdf(image_path, pdf_path):
    try:
        img = Image.open(image_path).convert("RGB")
        img.save(pdf_path, "PDF", resolution=100.0)
    except Exception as e:
        st.error(f"❌ Error al convertir la imagen a PDF: {e}")

# **INTERFAZ EN STREAMLIT**
st.title("📂 Registro de Visitas y Auditoría")

# **AUTENTICACIÓN**
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state["authenticated"]:
    st.info("🔐 Introduce el código TOTP generado en tu App de Autenticador.")
    user_totp = st.text_input("Código TOTP", max_chars=6, type="password")
    if st.button("Verificar Código"):
        if verify_totp(user_totp):
            st.session_state["authenticated"] = True
            st.success("✅ Autenticación completada con éxito.")
            st.rerun()
        else:
            st.error("🚫 Código incorrecto. Intenta de nuevo.")
else:
    st.success("✅ Sesión iniciada correctamente.")
    
    # **ENTRADA DE DATOS**
    actividad = st.text_input("📌 Ingrese la actividad:")
    fecha_actividad = st.date_input("📅 Seleccione la fecha de la actividad:")
    metas = ["Efectuar 3 Informes trimestrales", "Supervisión en campo", "Capacitación docente"]
    meta_seleccionada = st.selectbox("🎯 Seleccione la meta atendida:", metas)
    
    # **GUARDADO DE AUDITORÍA**
    if st.button("Guardar Registro de Auditoría"):
        data = {
            "Fecha": fecha_actividad.strftime("%Y-%m-%d"),
            "Actividad": actividad,
            "Meta": meta_seleccionada
        }
        save_to_audit(data)
    
    # **CARGAR Y PROCESAR IMÁGENES**
    st.subheader("📸 Tomar foto del documento y convertirlo en PDF (Opcional)")
    captured_photo = st.camera_input("Capturar documento")
    if captured_photo:
        img_path = os.path.join(VISIT_STORAGE_PATH, f"{actividad}_{fecha_actividad.strftime('%Y-%m-%d')}.jpg")
        pdf_path = img_path.replace(".jpg", ".pdf")

        with open(img_path, "wb") as f:
            f.write(captured_photo.getbuffer())

        save_image_as_pdf(img_path, pdf_path)
        st.success(f"✅ Documento convertido a PDF y guardado en: {pdf_path}")

        # 🔄 **Forzar la sincronización con OneDrive**
        time.sleep(3)  # Espera para asegurar que OneDrive detecte el archivo
        os.system(f'start "" "{VISIT_STORAGE_PATH}"')  # Abre la carpeta para verificar

    # **SUBIR IMÁGENES DESDE GALERÍA**
    uploaded_files = st.file_uploader("📎 Seleccionar hasta 3 fotos desde la galería", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    if uploaded_files:
        for i, file in enumerate(uploaded_files, 1):
            img_path = os.path.join(EVIDENCE_STORAGE_PATH, f"{actividad}_{fecha_actividad.strftime('%Y-%m-%d')}_{i:02}.jpg")
            with open(img_path, "wb") as f:
                f.write(file.getbuffer())

        st.success(f"✅ Evidencias guardadas en: {EVIDENCE_STORAGE_PATH}")

        # 🔄 **Forzar la sincronización con OneDrive**
        time.sleep(3)
        os.system(f'start "" "{EVIDENCE_STORAGE_PATH}"')

    # **BOTÓN PARA TERMINAR PROCESO**
    if st.button("Terminar Proceso"):
        st.success("✅ Proceso finalizado. Puede registrar una nueva actividad si lo desea.")
