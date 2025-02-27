import streamlit as st
import pandas as pd
import os
import requests
import pyotp
from datetime import datetime
from msal import PublicClientApplication
from fpdf import FPDF
from PIL import Image

# **CONFIGURACIÓN DE AZURE AD**
CLIENT_ID = "38597832-95f3-4cde-973e-5af2618665dc"
TENANT_ID = "2c9053b0-cfd0-484f-bc8f-5c045a175125"
CLIENT_SECRET = "TU_SECRETO_DE_CLIENTE"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["Files.ReadWrite", "User.Read"]

# **CONFIGURACIÓN DE AUTENTICACIÓN (TOTP)**
SECRET_KEY = "JBSWY3DPEHPK3PXP"

# **RUTA DE GUARDADO**
BASE_STORAGE_PATH = "C:/Users/sup11/OneDrive/Attachments/Documentos/Interfaces de phyton/Proyecto almacenamiento interactivo"
VISIT_STORAGE_PATH = os.path.join(BASE_STORAGE_PATH, "Visitas")
AUDIT_FILE = os.path.join(BASE_STORAGE_PATH, "registro_auditoria.xlsx")

# **LISTA DE METAS**
METAS = [
    "Efectuar 3 Informes trimestrales del Programa de mejora de la supervisión",
    "Realizar 12 Informes de Actividades Relevantes",
    "Realizar seguimiento a la implementación de los planes de asesoría",
    "Realizar 10 jornadas académicas para fortalecer la comunicación interna",
    "Implementar acciones de actualización en asesoría y comunicación asertiva",
    "Promover la participación de los PCD y ECAEF en los CTE",
    "Implementar estrategias en el Consejo Técnico Escolar",
    "Acompañar la implementación del Plan y Programas de Estudio",
    "Aplicar asesoría en Educación Física en educación básica",
    "Lograr la participación del 100% de docentes en el CTE",
    "Asesorar al 100% de docentes con y sin perfil profesional",
    "Intervención en el CTE y talleres intensivos de formación continua",
    "Actualizar sobre la propuesta curricular 2022",
    "Realizar visitas de asesoría a docentes de secundaria",
    "Ejecutar estrategias en proyectos de educación física estatales",
    "Diseñar estrategias de actividad física y cuidado de la salud",
    "Fortalecer estrategias académicas en el 100% de escuelas",
    "Implementar las etapas de los Juegos Deportivos Escolares"
]

# **FUNCIÓN PARA AUTENTICACIÓN**
def verify_totp(user_code):
    totp = pyotp.TOTP(SECRET_KEY)
    return totp.verify(user_code)

# **FUNCIÓN PARA OBTENER TOKEN**
def get_access_token():
    app = PublicClientApplication(CLIENT_ID, authority=AUTHORITY)
    result = app.acquire_token_by_client_credentials(SCOPES, CLIENT_SECRET)
    return result.get("access_token", None)

# **FUNCIÓN PARA GUARDAR EN EXCEL**
def save_to_excel(data):
    df = pd.DataFrame([data])
    if os.path.exists(AUDIT_FILE):
        df_existing = pd.read_excel(AUDIT_FILE)
        df = pd.concat([df_existing, df], ignore_index=True)
    df.to_excel(AUDIT_FILE, index=False)

# **FUNCIÓN PARA GENERAR PDF**
def save_image_as_pdf(image_path, pdf_path):
    img = Image.open(image_path).convert("RGB")
    img.save(pdf_path, "PDF", resolution=100.0)

# **INTERFAZ EN STREAMLIT**
st.set_page_config(page_title="Registro de Visitas", layout="wide")
st.title("📂 Registro de Visitas y Auditoría")

# **AUTENTICACIÓN**
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state["authenticated"] = False

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
    meta_seleccionada = st.selectbox("🎯 Seleccione la meta atendida:", METAS)
    
    # **GUARDADO DE AUDITORÍA**
    if st.button("Guardar Registro de Auditoría"):
        data = {
            "Fecha": fecha_actividad.strftime("%Y-%m-%d"),
            "Actividad": actividad,
            "Meta": meta_seleccionada
        }
        save_to_excel(data)
        st.success("✅ Registro guardado en auditoría.")
    
    # **CARGAR Y PROCESAR IMÁGENES**
    st.subheader("📸 Tomar foto del documento y convertirlo en PDF")
    captured_photo = st.camera_input("Capturar documento")
    if captured_photo:
        img_path = os.path.join(VISIT_STORAGE_PATH, f"{actividad}_{fecha_actividad.strftime('%Y-%m-%d')}_documento.jpg")
        with open(img_path, "wb") as f:
            f.write(captured_photo.getbuffer())
        pdf_path = img_path.replace(".jpg", ".pdf")
        save_image_as_pdf(img_path, pdf_path)
        st.success(f"✅ Documento convertido a PDF: {pdf_path}")
    
    # **SUBIR ARCHIVOS A ONEDRIVE (OPCIONAL)**

