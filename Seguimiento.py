import streamlit as st
import os
import time
from PIL import Image

# **La PRIMERA instrucción debe ser set_page_config**
st.set_page_config(page_title="Registro de Visitas", layout="wide")

# **CONFIGURACIÓN DE RUTA BASE EN ONEDRIVE**
BASE_ONEDRIVE_PATH = r"C:\Users\sup11\OneDrive\Attachments\Documentos\Interfaces de phyton\Proyecto almacenamiento interactivo"

# **INTERFAZ STREAMLIT**
st.sidebar.header("📂 Selección de Carpeta")
carpeta_opciones = ["Visitas", "Evidencia fotografica", "Otra Carpeta..."]
carpeta_seleccionada = st.sidebar.selectbox("Seleccione la carpeta de OneDrive:", carpeta_opciones)

# Si el usuario elige "Otra Carpeta...", permite escribir un nombre personalizado
if carpeta_seleccionada == "Otra Carpeta...":
    carpeta_personalizada = st.sidebar.text_input("Ingrese el nombre de la carpeta:")
    if carpeta_personalizada:
        carpeta_seleccionada = carpeta_personalizada

# **No creamos la carpeta automáticamente aquí, solo definimos la ruta**
ONEDRIVE_STORAGE_PATH = os.path.join(BASE_ONEDRIVE_PATH, carpeta_seleccionada)

# **CONFIGURACIÓN DE STREAMLIT**
st.title("📂 Registro de Visitas en OneDrive")

# **BOTÓN PARA CREAR LA CARPETA EN ONEDRIVE**
if st.button("🔄 Crear Carpeta en OneDrive"):
    try:
        if not os.path.exists(ONEDRIVE_STORAGE_PATH):
            os.makedirs(ONEDRIVE_STORAGE_PATH)
            st.success(f"✅ Carpeta creada: {ONEDRIVE_STORAGE_PATH}")
        else:
            st.info(f"📁 La carpeta ya existe en: {ONEDRIVE_STORAGE_PATH}")
    except Exception as e:
        st.error(f"❌ Error al crear la carpeta: {e}")

# **ENTRADA DE DATOS**
actividad = st.text_input("📌 Ingrese la actividad:")
fecha_actividad = st.date_input("📅 Seleccione la fecha de la actividad:")

# **CAPTURAR FOTO Y GUARDAR EN ONEDRIVE**
st.subheader("📸 Tomar foto del documento y guardarlo en OneDrive")
captured_photo = st.camera_input("Capturar documento")

if captured_photo:
    img_path = os.path.join(ONEDRIVE_STORAGE_PATH, f"{actividad}_{fecha_actividad.strftime('%Y-%m-%d')}.jpg")
    
    try:
        with open(img_path, "wb") as f:
            f.write(captured_photo.getbuffer())

        # **Verificar que el archivo realmente se guardó**
        if os.path.exists(img_path):
            st.success(f"✅ Archivo guardado en OneDrive: {img_path}")
            time.sleep(3)  # Esperar para que OneDrive lo sincronice
            os.system(f"attrib +S +H \"{img_path}\"")  # Forzar sincronización

        else:
            st.error(f"❌ ERROR: El archivo no se guardó en {img_path}")

    except Exception as e:
        st.error(f"❌ Error al guardar el archivo: {e}")

# **SUBIR ARCHIVOS DESDE GALERÍA**
uploaded_files = st.file_uploader("📎 Seleccionar hasta 3 fotos desde la galería", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    for i, file in enumerate(uploaded_files, 1):
        img_path = os.path.join(ONEDRIVE_STORAGE_PATH, f"{actividad}_{fecha_actividad.strftime('%Y-%m-%d')}_{i:02}.jpg")
        try:
            with open(img_path, "wb") as f:
                f.write(file.getbuffer())

            # **Verificar que el archivo realmente se guardó**
            if os.path.exists(img_path):
                st.success(f"✅ Imagen guardada en OneDrive: {img_path}")
                time.sleep(3)  # Esperar para que OneDrive lo sincronice
                os.system(f"attrib +S +H \"{img_path}\"")  # Forzar sincronización
            else:
                st.error(f"❌ ERROR: No se guardó la imagen en {img_path}")
        
        except Exception as e:
            st.error(f"❌ Error al guardar imagen: {e}")

# **BOTÓN PARA TERMINAR PROCESO**
if st.button("Terminar Proceso"):
    st.success("✅ Proceso finalizado. Puede registrar una nueva actividad si lo desea.")
