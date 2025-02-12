import streamlit as st
import pandas as pd
import os
from datetime import datetime
from office365.sharepoint.client_context import ClientContext
from msal import PublicClientApplication
import requests
import cv2
from PIL import Image

# Configuración de la interfaz
st.set_page_config(page_title="Registro Diario de Actividades", layout="wide")

# Configuración de autenticación con MSAL
CLIENT_ID = "38597832-95f3-4cde-973e-5af2618665dc"
TENANT_ID = "common"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["Files.ReadWrite", "User.Read"]  # Permisos para OneDrive

app = PublicClientApplication(CLIENT_ID, authority=AUTHORITY)
st.session_state["token"] = None

# Función para autenticación
def authenticate():
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
    else:
        result = app.acquire_token_interactive(SCOPES)
    
    if "access_token" in result:
        st.session_state["token"] = result["access_token"]
        st.success("Autenticado con éxito")
    else:
        st.error("Error en la autenticación")

# Botón de autenticación
if not st.session_state.get("token"):
    if st.button("Autenticarse con Microsoft"):
        authenticate()
else:
    st.success("Sesión activa")

# SharePoint/OneDrive Configuración
if st.session_state.get("token"):
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    onedrive_url = "https://graph.microsoft.com/v1.0/me/drive/root:/Visitas/"

    # Título
    st.title("Registro Diario de Actividades Laborales")

    # Selección de fecha
    fecha_actividad = st.date_input("Fecha de la actividad", datetime.today())

    # Menú desplegable de actividades
    tipo_actividad = st.selectbox(
        "Selecciona el tipo de actividad",
        [
            "Visita Técnica Pedagógica",
            "Visita Técnico-Administrativa",
            "Jornada Académica",
            "Curso",
            "Taller",
            "Actividad Relevante"
        ]
    )

    # Entrada de sede y notas
    sede_evento = st.text_input("Sede del evento")
    notas_evento = st.text_area("Notas del evento")

    # Horario de la actividad
    hora_inicio = st.time_input("Hora de inicio")
    hora_termino = st.time_input("Hora de término")

    # Captura de imagen desde la cámara
    st.write("Capturar evidencia con cámara")
    camera_image = st.camera_input("Tomar foto")
    
    # Subida de evidencias en PDF
    evidencia_pdf = st.file_uploader("Subir evidencia en PDF", type=["pdf"])

    # Subida de imágenes desde el dispositivo
    evidencia_fotos = st.file_uploader(
        "Subir hasta 3 fotos de evidencia", type=["jpg", "png", "jpeg"], accept_multiple_files=True
    )

    # Crear estructura de carpetas en OneDrive
    mes_actual = datetime.today().strftime("%Y-%m")
    actividad_folder = f"{tipo_actividad}_{fecha_actividad.strftime('%Y-%m-%d')}"
    folder_path = f"Visitas/{mes_actual}/{actividad_folder}"
    
    # Guardado de datos en OneDrive
    def upload_to_onedrive(file, file_name):
        upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{folder_path}/{file_name}:/content"
        response = requests.put(upload_url, headers=headers, data=file.getbuffer())
        if response.status_code == 201:
            st.success(f"{file_name} subido exitosamente a OneDrive")
        else:
            st.error(f"Error al subir {file_name}: {response.text}")
    
    if st.button("Guardar Registro"):
        data = {
            "Fecha": [fecha_actividad.strftime("%Y-%m-%d")],
            "Tipo de Actividad": [tipo_actividad],
            "Sede": [sede_evento],
            "Notas": [notas_evento],
            "Hora Inicio": [hora_inicio.strftime("%H:%M")],
            "Hora Término": [hora_termino.strftime("%H:%M")]
        }
        df = pd.DataFrame(data)
        archivo_excel = "registro_actividades.xlsx"
        df.to_excel(archivo_excel, index=False)
        
        with open(archivo_excel, "rb") as file:
            upload_to_onedrive(file, archivo_excel)
        
        if evidencia_pdf:
            upload_to_onedrive(evidencia_pdf, evidencia_pdf.name)
        
        for idx, foto in enumerate(evidencia_fotos):
            upload_to_onedrive(foto, f"evidencia_{idx+1}.jpg")
        
        st.success("Registro guardado exitosamente en OneDrive y Excel")

