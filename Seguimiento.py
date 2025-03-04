import streamlit as st
import pandas as pd
import os
import requests
import json
from datetime import datetime
from msal import ConfidentialClientApplication

# **CONFIGURACIÓN DE MICROSOFT GRAPH**
TENANT_ID = "2c9053b0-cfd0-484f-bc8f-5c045a175125"
CLIENT_ID = "38597832-95f3-4cde-973e-5af2618665dc"
CLIENT_SECRET = "899f17a0-8b57-4d67-a190-2e48cfdec797"
SCOPES = ["https://graph.microsoft.com/.default"]
GRAPH_API_URL = "https://graph.microsoft.com/v1.0"

# **RUTAS DE ONE DRIVE**
FOLDER_PATHS = {
    "AUDIT": "Proyecto almacenamiento interactivo/Auditorias/",
    "EVIDENCE": "Proyecto almacenamiento interactivo/Evidencia fotografica/",
    "DOCUMENT": "Proyecto almacenamiento interactivo/Visitas/",
    "ZIP": "Proyecto almacenamiento interactivo/Registros_ZIP/"
}

def get_access_token():
    app = ConfidentialClientApplication(CLIENT_ID, CLIENT_SECRET, authority=f"https://login.microsoftonline.com/{TENANT_ID}")
    token_response = app.acquire_token_for_client(scopes=SCOPES)
    return token_response.get("access_token")

def upload_to_onedrive(file, folder, filename):
    access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/octet-stream"
    }
    upload_url = f"{GRAPH_API_URL}/me/drive/root:/{folder}/{filename}:/content"
    response = requests.put(upload_url, headers=headers, data=file.read())
    return response.status_code, response.json()

st.title("📂 Registro de Actividades en OneDrive")
actividad = st.text_input("📌 Ingrese la actividad:")
fecha_actividad = st.date_input("📅 Seleccione la fecha de la actividad:")

documento = st.file_uploader("📎 Subir documento en formato JPG o PNG", type=["jpg", "jpeg", "png"])
uploaded_files = st.file_uploader("📸 Seleccione evidencias", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if st.button("Guardar en OneDrive"):
    if documento:
        status_code, response = upload_to_onedrive(documento, FOLDER_PATHS["DOCUMENT"], f"Visita_{actividad}_{fecha_actividad.strftime('%Y%m%d')}.jpg")
        if status_code == 201:
            st.success("✅ Documento guardado en OneDrive correctamente.")
        else:
            st.error(f"Error subiendo documento: {response}")

    for idx, file in enumerate(uploaded_files):
        status_code, response = upload_to_onedrive(file, FOLDER_PATHS["EVIDENCE"], f"{actividad}_{fecha_actividad.strftime('%Y%m%d')}_evidencia{idx+1}.jpg")
        if status_code == 201:
            st.success(f"✅ Evidencia {idx+1} guardada en OneDrive correctamente.")
        else:
            st.error(f"Error subiendo evidencia {idx+1}: {response}")
