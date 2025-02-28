import streamlit as st
import os
import time
from PIL import Image

# **CONFIGURACIÓN DE RUTA EN ONEDRIVE**
BASE_STORAGE_PATH = r"C:\Users\sup11\OneDrive\Attachments\Documentos\Interfaces de phyton\Proyecto almacenamiento interactivo"
VISIT_STORAGE_PATH = os.path.join(BASE_STORAGE_PATH, "Visitas")
EVIDENCE_STORAGE_PATH = os.path.join(BASE_STORAGE_PATH, "Evidencia fotografica")

# **Verificar y Crear Directorios si No Existen**
for path in [VISIT_STORAGE_PATH, EVIDENCE_STORAGE_PATH]:
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

st.set_page_config(page_title="Registro de Visitas", layout="wide")
st.title("📂 Registro de Visitas y Auditoría")

# **ENTRADA DE DATOS**
actividad = st.text_input("📌 Ingrese la actividad:")
fecha_actividad = st.date_input("📅 Seleccione la fecha de la actividad:")

# **CARGAR Y PROCESAR IMÁGENES**
st.subheader("📸 Tomar foto del documento y guardarlo en OneDrive")
captured_photo = st.camera_input("Capturar documento")

if captured_photo:
    img_path = os.path.join(VISIT_STORAGE_PATH, f"{actividad}_{fecha_actividad.strftime('%Y-%m-%d')}.jpg")
    
    try:
        with open(img_path, "wb") as f:
            f.write(captured_photo.getbuffer())

        # **Verificar que el archivo realmente se guardó**
        if os.path.exists(img_path):
            st.success(f"✅ Archivo guardado en OneDrive: {img_path}")

            # **Forzar sincronización de OneDrive**
            time.sleep(3)  # Esperar unos segundos para que OneDrive lo detecte
            os.system("attrib +S +H " + img_path)  # Asegurar que OneDrive lo sincronice

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

            # **Verificar que el archivo realmente se guardó**
            if os.path.exists(img_path):
                st.success(f"✅ Imagen guardada en OneDrive: {img_path}")
                time.sleep(3)  # Esperar para que OneDrive lo sincronice
                os.system("attrib +S +H " + img_path)  # Forzar sincronización
            else:
                st.error(f"❌ ERROR: No se guardó la imagen en {img_path}")
        
        except Exception as e:
            st.error(f"❌ Error al guardar imagen: {e}")

# **BOTÓN PARA TERMINAR PROCESO**
if st.button("Terminar Proceso"):
    st.success("✅ Proceso finalizado. Puede registrar una nueva actividad si lo desea.")
