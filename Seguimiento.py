import streamlit as st
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
BASE_STORAGE_PATH = "C:/Users/sup11/OneDrive/Attachments/Documentos/Interfaces de phyton/Proyecto almacenamiento interactivo/Visitas"

# **FUNCIONES PARA AUTENTICACIÓN**
def generate_totp():
    totp = pyotp.TOTP(SECRET_KEY)
    return totp.now()

def verify_totp(user_code):
    totp = pyotp.TOTP(SECRET_KEY)
    return totp.verify(user_code)

# **FUNCIÓN PARA OBTENER TOKEN DE AUTENTICACIÓN**
def get_access_token():
    app = PublicClientApplication(CLIENT_ID, authority=AUTHORITY)
    result = app.acquire_token_by_client_credentials(SCOPES, CLIENT_SECRET)
    return result.get("access_token", None)

# **FUNCIÓN PARA SUBIR ARCHIVOS A ONEDRIVE**
def upload_to_onedrive(file_path, activity_name):
    access_token = get_access_token()
    if not access_token:
        return False

    filename = os.path.basename(file_path)
    upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/Visitas/{activity_name}/{filename}:/content"

    with open(file_path, "rb") as file:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/octet-stream",
        }
        response = requests.put(upload_url, headers=headers, data=file)

    return response.status_code in [200, 201]

# **FUNCIÓN PARA GUARDAR IMÁGENES COMO PDF**
def save_images_as_pdf(images, pdf_path):
    img_list = [Image.open(img).convert("RGB") for img in images]
    img_list[0].save(pdf_path, save_all=True, append_images=img_list[1:])

# **INTERFAZ EN STREAMLIT**
st.set_page_config(page_title="Registro de Visitas", layout="wide")
st.title("📂 Registro de Visitas y Subida a OneDrive")

# **AUTENTICACIÓN**
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.info("🔐 Introduce el código TOTP generado en tu App de Autenticador.")
    user_totp = st.text_input("Código TOTP", max_chars=6, type="password")

    if st.button("Verificar Código"):
        if verify_totp(user_totp):
            st.session_state["authenticated"] = True
            st.success("✅ Autenticación completada con éxito.")
            st.experimental_rerun()
        else:
            st.error("🚫 Código incorrecto. Intenta de nuevo.")

else:
    st.success("✅ Sesión iniciada correctamente.")

    # **ENTRADA DE DATOS**
    actividad = st.text_input("📌 Ingrese la actividad:")
    fecha_actividad = st.date_input("📅 Seleccione la fecha de la actividad:")
    año_actividad = fecha_actividad.strftime("%Y")
    fecha_str = fecha_actividad.strftime("%Y-%m-%d")

    # **NOMENCLATURA Y CARPETA**
    folder_name = f"{actividad}_{fecha_str}_{año_actividad}"
    save_folder = os.path.join(BASE_STORAGE_PATH, folder_name)
    os.makedirs(save_folder, exist_ok=True)

    # **SUBIR ARCHIVOS**
    st.subheader("📎 Cargar archivos de evidencia")
    uploaded_files = st.file_uploader("Selecciona hasta 3 imágenes", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    if uploaded_files and len(uploaded_files) <= 3:
        image_paths = []
        for i, uploaded_file in enumerate(uploaded_files, 1):
            image_path = os.path.join(save_folder, f"{actividad}_{fecha_str}_{año_actividad}_imagen{i}.jpg")
            with open(image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            image_paths.append(image_path)

        st.success(f"✅ Imágenes guardadas en: {save_folder}")

        # **GENERAR PDF SI SELECCIONÓ IMÁGENES**
        if st.button("📄 Convertir imágenes en PDF"):
            pdf_path = os.path.join(save_folder, f"{actividad}_{fecha_str}_{año_actividad}.pdf")
            save_images_as_pdf(image_paths, pdf_path)
            st.success(f"✅ PDF generado: {pdf_path}")

            # **SUBIR PDF A ONEDRIVE**
            if st.button("📤 Subir PDF a OneDrive"):
                if upload_to_onedrive(pdf_path, actividad):
                    st.success(f"✅ PDF subido a OneDrive: {pdf_path}")
                else:
                    st.error("🚫 Error al subir el archivo a OneDrive.")

        # **SUBIR IMÁGENES A ONEDRIVE**
        if st.button("📤 Subir imágenes a OneDrive"):
            for image in image_paths:
                if upload_to_onedrive(image, actividad):
                    st.success(f"✅ {os.path.basename(image)} subido a OneDrive.")
                else:
                    st.error(f"🚫 Error al subir {os.path.basename(image)} a OneDrive.")

    elif len(uploaded_files) > 3:
        st.error("🚫 Solo puedes seleccionar hasta 3 imágenes.")
