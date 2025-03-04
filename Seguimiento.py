import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime
from msal import PublicClientApplication

# **CONFIGURACIÓN DE MICROSOFT GRAPH**
TENANT_ID = "2c9053b0-cfd0-484f-bc8f-5c045a175125"
CLIENT_ID = "38597832-95f3-4cde-973e-5af2618665dc"
SCOPES = ["https://graph.microsoft.com/.default"]
GRAPH_API_URL = "https://graph.microsoft.com/v1.0"

# **RUTAS EN ONEDRIVE**
FOLDER_PATHS = {
    "AUDIT": "Proyecto almacenamiento interactivo/Auditorias/",
    "EVIDENCE": "Proyecto almacenamiento interactivo/Evidencia fotografica/",
    "DOCUMENT": "Proyecto almacenamiento interactivo/Visitas/",
    "ZIP": "Proyecto almacenamiento interactivo/Registros_ZIP/"
}

def get_access_token():
    app = PublicClientApplication(CLIENT_ID, authority=f"https://login.microsoftonline.com/{TENANT_ID}")
    accounts = app.get_accounts()
    
    if accounts:
        token_response = app.acquire_token_silent(SCOPES, account=accounts[0])
        if "access_token" in token_response:
            st.write("🔹 Token renovado correctamente")
            return token_response["access_token"]
    
    flow = app.initiate_device_flow(scopes=SCOPES)
    if "user_code" not in flow:
        st.error("❌ Error iniciando autenticación interactiva")
        return None
    
    st.write(f"🔹 Ingresa el código en [https://microsoft.com/devicelogin](https://microsoft.com/devicelogin) y usa este código: {flow['user_code']}")
    st.write("📲 Acepta la autenticación en tu aplicación de Microsoft Authenticator")
    
    token_response = app.acquire_token_by_device_flow(flow)
    
    if "access_token" in token_response:
        st.write("🔹 Token generado correctamente")
        return token_response["access_token"]
    
    st.error(f"❌ Error obteniendo token: {token_response}")
    return None
    
    st.write(f"🔹 Ingresa el código en [https://microsoft.com/devicelogin](https://microsoft.com/devicelogin) y usa este código: {flow['user_code']}")
    
    token_response = app.acquire_token_by_device_flow(flow)
    
    if "access_token" in token_response:
        st.write("🔹 Token generado correctamente")
        return token_response["access_token"]
    
    st.error(f"❌ Error obteniendo token: {token_response}")
    return None

def upload_to_onedrive(file, folder, filename):
    access_token = get_access_token()
    if not access_token:
        return None, {"error": "No se pudo obtener el token de autenticación."}
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/octet-stream"
    }
    upload_url = f"{GRAPH_API_URL}/me/drive/root:/{folder}{filename}:/content"
    response = requests.put(upload_url, headers=headers, data=file.read())
    
    if response.status_code == 201:
        file_info = response.json()
        st.success(f"✅ Archivo subido correctamente: [{file_info['name']}]({file_info['webUrl']})")
        return response.status_code, file_info
    else:
        st.error(f"❌ Error subiendo archivo: {response.json()}")
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
