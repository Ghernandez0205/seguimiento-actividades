import streamlit as st
import os
import requests
import pyotp
from datetime import datetime
from msal import PublicClientApplication
from fpdf import FPDF  # Para generar PDFs

# **CONFIGURACIÓN DE AZURE AD**
CLIENT_ID = "38597832-95f3-4cde-973e-5af2618665dc"
TENANT_ID = "2c9053b0-cfd0-484f-bc8f-5c045a175125"
CLIENT_SECRET = "TU_SECRETO_DE_CLIENTE"  # 🔴 Reemplázalo con el secreto de cliente generado
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["Files.ReadWrite", "User.Read"]

# **CONFIGURACIÓN DE AUTENTICACIÓN (TOTP)**
SECRET_KEY = "JBSWY3DPEHPK3PXP"  # 🔴 Cambia esto por una clave secreta segura

# **CONFIGURACIÓN DE ONEDRIVE**
ONEDRIVE_UPLOAD_FOLDER = "/Documentos/RegistroActividades/"

# **FUNCION PARA GENERAR CÓDIGO TOTP**
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

    if "access_token" in result:
        return result["access_token"]
    else:
        st.error(f"Error autenticando con Azure: {result.get('error_description', 'Desconocido')}")
        return None

# **FUNCIÓN PARA SUBIR ARCHIVOS A ONEDRIVE**
def upload_to_onedrive(file_path, activity_name):
    access_token = get_access_token()
    if not access_token:
        return False

    filename = os.path.basename(file_path)
    upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:{ONEDRIVE_UPLOAD_FOLDER}{activity_name}_{filename}:/content"

    with open(file_path, "rb") as file:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/octet-stream",
        }
        response = requests.put(upload_url, headers=headers, data=file)

    if response.status_code in [200, 201]:
        st.success(f"✅ Archivo subido a OneDrive: {filename}")
        return True
    else:
        st.error(f"🚫 Error al subir archivo: {response.text}")
        return False

# **FUNCIÓN PARA ESCANEAR Y GUARDAR IMÁGENES COMO PDF**
def save_images_as_pdf(image_list, pdf_path):
    if image_list:
        pdf = FPDF()
        for img_path in image_list:
            pdf.add_page()
            pdf.image(img_path, x=10, y=10, w=190)
        pdf.output(pdf_path, "F")

# **INTERFAZ EN STREAMLIT**
st.set_page_config(page_title="Registro Diario de Actividades", layout="wide")
st.title("📂 Registro de Actividades y Subida a OneDrive")

# **AUTENTICACIÓN: INGRESAR CÓDIGO TOTP**
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.info("🔐 Introduce el código dinámico generado en tu App de Autenticador.")
    user_totp = st.text_input("Código TOTP", max_chars=6, type="password")

    if st.button("Verificar Código"):
        if verify_totp(user_totp):
            st.session_state["authenticated"] = True
            st.success("✅ Autenticación completada con éxito.")
            st.experimental_rerun()
        else:
            st.error("🚫 Código incorrecto. Intenta de nuevo.")

else:
    st.success("✅ Sesión iniciada con autenticación segura.")
    
    activity_name = st.text_input("📌 Nombre de la actividad:")
    uploaded_file = st.file_uploader("📎 Cargar archivo de evidencia", type=["jpg", "jpeg", "png", "pdf"])

    if activity_name and uploaded_file:
        fecha_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        save_folder = "temp_uploads"
        os.makedirs(save_folder, exist_ok=True)

        file_path = os.path.join(save_folder, f"{activity_name}_{fecha_hora}_{uploaded_file.name}")
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"✅ Archivo guardado temporalmente: {file_path}")

        if st.button("📤 Subir a OneDrive"):
            upload_to_onedrive(file_path, activity_name)

    # **OPCIÓN PARA ESCANEAR IMÁGENES Y GENERAR PDF**
    st.subheader("📸 Escanear y Guardar como PDF")
    images = []
    for i in range(3):
        photo = st.camera_input(f"Tomar foto {i+1}")
        if photo:
            fecha_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            img_path = os.path.join(save_folder, f"{activity_name}_{fecha_hora}_{i+1}.jpg")
            with open(img_path, "wb") as f:
                f.write(photo.getbuffer())
            images.append(img_path)

    if images:
        pdf_path = os.path.join(save_folder, f"{activity_name}_{fecha_hora}.pdf")
        save_images_as_pdf(images, pdf_path)
        st.success(f"✅ PDF generado: {pdf_path}")
        if st.button("📤 Subir PDF a OneDrive"):
            upload_to_onedrive(pdf_path, activity_name)

