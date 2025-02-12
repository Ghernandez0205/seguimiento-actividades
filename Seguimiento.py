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

# Configuración de la aplicación como cliente público
app = PublicClientApplication(CLIENT_ID, authority=AUTHORITY, token_cache=None)

if "token" not in st.session_state:
    st.session_state["token"] = None
    st.session_state["token_expiration"] = datetime.now()
    st.session_state["user_email"] = None
    st.session_state["user_id"] = None
    st.session_state["totp_verified"] = False

def authenticate():
    """Autenticación usando Device Code Flow para Streamlit Cloud."""
    st.write("Intentando autenticar...")
    try:
        flow = app.initiate_device_flow(SCOPES)
        if "user_code" in flow:
            st.write("🔗 Ve a [https://microsoft.com/devicelogin](https://microsoft.com/devicelogin) e ingresa este código:")
            st.code(flow['user_code'])
            result = app.acquire_token_by_device_flow(flow)
            if "access_token" in result:
                st.session_state["token"] = result["access_token"]
                st.session_state["token_expiration"] = datetime.now() + timedelta(hours=1)
                
                # Obtener información del usuario autenticado
                user_info = requests.get("https://graph.microsoft.com/v1.0/me", 
                                        headers={"Authorization": f"Bearer {st.session_state['token']}"})
                user_data = user_info.json()
                st.session_state["user_email"] = user_data.get("mail")
                st.session_state["user_id"] = user_data.get("id")
                
                # Validar que sea el usuario autorizado
                if st.session_state["user_email"] != AUTHORIZED_EMAIL or st.session_state["user_id"] != AUTHORIZED_USER_ID:
                    st.error("🚫 Acceso denegado: Solo el usuario autorizado puede usar esta aplicación.")
                    st.session_state["token"] = None
                    st.session_state["user_email"] = None
                    st.session_state["user_id"] = None
                else:
                    st.session_state["totp_verified"] = False  # Siempre deshabilitar TOTP hasta verificarlo
                    st.experimental_rerun()
            else:
                st.error("❌ Error en la autenticación: " + str(result))
        else:
            st.error("Error al obtener el código de autenticación.")
    except Exception as e:
        st.error(f"Error en la autenticación: {e}")

# Cerrar sesión automáticamente si el token expira
if st.session_state.get("token") and datetime.now() > st.session_state.get("token_expiration"):
    st.session_state["token"] = None
    st.session_state["totp_verified"] = False
    st.warning("⚠️ Tu sesión ha expirado. Vuelve a autenticarse.")

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

