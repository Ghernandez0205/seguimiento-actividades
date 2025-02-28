import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime
from PIL import Image

# **CONFIGURACIÓN DE RUTAS (OneDrive)**
BASE_STORAGE_PATH = r"C:\Users\sup11\OneDrive\Attachments\Documentos\Interfaces de phyton\Proyecto almacenamiento interactivo"
VISIT_STORAGE_PATH = os.path.join(BASE_STORAGE_PATH, "Visitas")
EVIDENCE_STORAGE_PATH = os.path.join(BASE_STORAGE_PATH, "Evidencia fotografica")

# **Verificar y Crear Directorios si No Existen**
for path in [BASE_STORAGE_PATH, VISIT_STORAGE_PATH, EVIDENCE_STORAGE_PATH]:
    os.makedirs(path, exist_ok=True)

# **CONFIGURACIÓN DE STREAMLIT**
st.set_page_config(page_title="Registro de Visitas", layout="wide")
st.title("📂 Registro de Visitas y Auditoría")

# **ENTRADA DE DATOS**
actividad = st.text_input("📌 Ingrese la actividad:")
fecha_actividad = st.date_input("📅 Seleccione la fecha de la actividad:")

# **GUARDADO DE AUDITORÍA**
if st.button("Guardar Registro de Auditoría"):
    audit_data = {
        "Fecha": fecha_actividad.strftime("%Y-%m-%d"),
        "Actividad": actividad
    }
    df = pd.DataFrame([audit_data])
    audit_file = os.path.join(BASE_STORAGE_PATH, "registro_auditoria.xlsx")

    # Guardar en Excel
    if os.path.exists(audit_file):
        df_existing = pd.read_excel(audit_file, engine="openpyxl")
        df = pd.concat([df_existing, df], ignore_index=True)
    df.to_excel(audit_file, index=False, engine="openpyxl")
    st.success(f"✅ Auditoría guardada en: {audit_file}")

# **CARGAR Y PROCESAR IMÁGENES**
st.subheader("📸 Tomar foto del documento y convertirlo en PDF (Opcional)")
captured_photo = st.camera_input("Capturar documento")
if captured_photo:
    img_path = os.path.join(VISIT_STORAGE_PATH, f"{actividad}_{fecha_actividad.strftime('%Y-%m-%d')}.jpg")
    
    try:
        with open(img_path, "wb") as f:
            f.write(captured_photo.getbuffer())

        # Verificar que se haya guardado
        if os.path.exists(img_path):
            st.success(f"✅ Archivo guardado en: {img_path}")
        else:
            st.error(f"❌ ERROR: El archivo no se guardó en {img_path}")
    
    except Exception as e:
        st.error(f"❌ Error al guardar el archivo: {e}")

# **SUBIR IMÁGENES DESDE GALERÍA**
uploaded_files = st.file_uploader("📎 Seleccionar hasta 3 fotos desde la galería", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
if uploaded_files:
    for i, file in enumerate(uploaded_files, 1):
        img_path = os.path.join(EVIDENCE_STORAGE_PATH, f"{actividad}_{fecha_actividad.strftime('%Y-%m-%d')}_{i:02}.jpg")
        try:
            with open(img_path, "wb") as f:
                f.write(file.getbuffer())

            # Verificar que se haya guardado
            if os.path.exists(img_path):
                st.success(f"✅ Imagen guardada en: {img_path}")
            else:
                st.error(f"❌ ERROR: No se guardó la imagen en {img_path}")
        
        except Exception as e:
            st.error(f"❌ Error al guardar imagen: {e}")

# **BOTÓN PARA TERMINAR PROCESO**
if st.button("Terminar Proceso"):
    st.success("✅ Proceso finalizado. Puede registrar una nueva actividad si lo desea.")
