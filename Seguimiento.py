import streamlit as st
import pandas as pd
import os
import requests
import pyotp
from datetime import datetime
from msal import ConfidentialClientApplication
from fpdf import FPDF
from PIL import Image

# **CONFIGURACIÓN DE AZURE AD**
CLIENT_ID = "38597832-95f3-4cde-973e-5af2618665dc"
TENANT_ID = "2c9053b0-cfd0-484f-bc8f-5c045a175125"
CLIENT_SECRET = "TU_SECRETO_DE_CLIENTE"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["Files.ReadWrite.All", "User.Read", "offline_access"]

# **AUTENTICACIÓN CON MICROSOFT GRAPH**
def get_access_token():
    app = ConfidentialClientApplication(
        CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
    )
    result = app.acquire_token_for_client(scopes=SCOPES)
    return result.get("access_token", None)

def get_folder_id(folder_name):
    """ Obtiene el ID de la carpeta en OneDrive """
    access_token = get_access_token()
    if not access_token:
        st.error("Error: No se pudo obtener el token de acceso.")
        return None

    url = "https://graph.microsoft.com/v1.0/me/drive/root/children"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        folders = response.json().get("value", [])
        for folder in folders:
            if folder["name"] == folder_name:
                return folder["id"]
    st.error(f"Error: No se encontró la carpeta {folder_name}.")
    return None

def upload_to_onedrive(file_path, folder_name, file_name):
    access_token = get_access_token()
    if not access_token:
        st.error("Error: No se pudo obtener el token de acceso.")
        return

    folder_id = get_folder_id(folder_name)
    if not folder_id:
        return

    url = f"https://graph.microsoft.com/v1.0/me/drive/items/{folder_id}:/{file_name}:/content"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    with open(file_path, "rb") as f:
        response = requests.put(url, headers=headers, data=f)
    
    if response.status_code in [200, 201]:
        st.success(f"✅ Archivo subido a OneDrive: {folder_name}/{file_name}")
    else:
        st.error(f"Error al subir archivo: {response.text}")

# **RUTAS DE GUARDADO**
AUDIT_FILE = "registro_auditoria.xlsx"
VISIT_FOLDER = "Visitas"
EVIDENCE_FOLDER = "Evidencia fotografica"
AUDIT_FOLDER = "Auditoria"

# **CONFIGURACIÓN DE STREAMLIT**
st.set_page_config(page_title="Registro de Visitas", layout="wide")

st.title("📂 Registro de Visitas y Auditoría")

# **ENTRADA DE DATOS**
actividad = st.text_input("📌 Ingrese la actividad:")
fecha_actividad = st.date_input("📅 Seleccione la fecha de la actividad:")
metas = ["Efectuar 3 Informes trimestrales", "Supervisión en campo", "Capacitación docente"]
meta_seleccionada = st.selectbox("🎯 Seleccione la meta atendida:", metas)

# **GUARDADO DE AUDITORÍA**
def save_to_audit(data):
    df = pd.DataFrame([data])
    if os.path.exists(AUDIT_FILE):
        df_existing = pd.read_excel(AUDIT_FILE, engine="openpyxl")
        df = pd.concat([df_existing, df], ignore_index=True)
    df.to_excel(AUDIT_FILE, index=False, engine="openpyxl")
    upload_to_onedrive(AUDIT_FILE, AUDIT_FOLDER, "registro_auditoria.xlsx")
    st.success(f"✅ Auditoría guardada y subida a OneDrive.")

if st.button("Guardar Registro de Auditoría"):
    data = {"Fecha": fecha_actividad.strftime("%Y-%m-%d"), "Actividad": actividad, "Meta": meta_seleccionada}
    save_to_audit(data)

# **CAPTURA DE FOTO Y CONVERSIÓN A PDF**
st.subheader("📸 Tomar foto del documento y convertirlo en PDF (Opcional)")
captured_photo = st.camera_input("Capturar documento")
if captured_photo:
    img_path = f"{actividad}_{fecha_actividad.strftime('%Y-%m-%d')}.jpg"
    pdf_path = img_path.replace(".jpg", ".pdf")
    with open(img_path, "wb") as f:
        f.write(captured_photo.getbuffer())
    img = Image.open(img_path).convert("RGB")
    img.save(pdf_path, "PDF", resolution=100.0)
    upload_to_onedrive(pdf_path, VISIT_FOLDER, pdf_path)
    st.success(f"✅ Documento convertido y subido a OneDrive como PDF.")

# **SUBIDA DE FOTOS DESDE GALERÍA**
uploaded_files = st.file_uploader("📎 Seleccionar hasta 3 fotos desde la galería", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
if uploaded_files:
    for i, file in enumerate(uploaded_files, 1):
        file_name = f"{actividad}_{fecha_actividad.strftime('%Y-%m-%d')}_{i:02}.jpg"
        with open(file_name, "wb") as f:
            f.write(file.getbuffer())
        upload_to_onedrive(file_name, EVIDENCE_FOLDER, file_name)
    st.success("✅ Evidencias subidas a OneDrive.")

# **TERMINAR PROCESO**
if st.button("Terminar Proceso"):
    st.success("✅ Proceso finalizado. Puede registrar una nueva actividad si lo desea.")
