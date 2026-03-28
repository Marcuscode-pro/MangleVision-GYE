import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from streamlit_image_comparison import image_comparison
from PIL import Image
import os
import plotly.express as px

# --- 1. CONFIGURACIÓN DE PÁGINA (ESTRICTO) ---
st.set_page_config(page_title="MangleVision Pro 2026", layout="wide", initial_sidebar_state="collapsed")

# --- 2. CSS DE ALTO IMPACTO ---
# Este bloque elimina CUALQUIER margen de Streamlit Cloud
st.markdown("""
    <style>
    /* Elimina el padding de la aplicación principal */
    .block-container {
        padding: 0rem !important;
        max-width: 100% !important;
    }
    /* Fuerza a los iframes (donde vive el comparador) a ser enormes */
    iframe {
        width: 100vw !important;
        height: 80vh !important;
    }
    /* Ajuste para pantallas retina/oscuro */
    .stApp { background-color: #0e1117; }
    
    /* Estilo para los tabs para que se vean profesionales */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #1d2127;
        border-radius: 10px 10px 0px 0px;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATOS ---
@st.cache_data
def load_data():
    return pd.DataFrame({
        'Sector': ['Urdesa', 'Puerto Hondo', 'La Puntilla', 'Guasmo Sur', 'Vía a la Costa', 'Malecón 2000', 'Isla Santay', 'Entre Ríos'],
        'Lat': [-2.172, -2.195, -2.142, -2.258, -2.165, -2.191, -2.215, -2.150],
        'Lon': [-79.912, -80.055, -79.865, -79.898, -80.012, -79.878, -79.895, -79.875],
        'Elevacion': [1.2, 0.5, 2.1, 0.8, 3.8, 2.5, 0.6, 1.9],
        'Poblacion': [15000, 2000, 12000, 45000, 8000, 5000, 500, 7000]
    })

df = load_data()

# --- 4. SIDEBAR ---
with st.sidebar:
    st.header("🕹️ Simulación")
    nivel_marea = st.slider("Marea (m)", 0.0, 5.0, 2.0)
    manglar = st.toggle("🌱 Barrera de Manglar")
    reduccion = 0.7 if manglar else 1.0

# --- 5. TABS ---
t1, t2 = st.tabs(["🌐 MAPA DE RIESGO", "🖼️ COMPARADOR DE IMPACTO XL"])

with t1:
    st.title("🛡️ MangleVision: Análisis Territorial")
    m = folium.Map(location=[-2.18, -79.90], zoom_start=12, tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google')
    for i, row in df.iterrows():
        inundado = (nivel_marea * reduccion) > row['Elevacion']
        folium.CircleMarker(
            location=[row['Lat'], row['Lon']],
            radius=10, color="#FF4B4B" if inundado else "#2EB82E",
            fill=True, popup=row['Sector']
        ).add_to(m)
    folium_static(m, width=1200)

with t2:
    # --- AQUÍ ESTÁ EL CAMBIO CLAVE ---
    st.write("## Visualización de Resiliencia Costera")
    
    if os.path.exists("antes.png") and os.path.exists("despues.png"):
        # Usamos un contenedor de Streamlit vacío para forzar el layout
        container = st.container()
        with container:
            image_comparison(
                img1=Image.open("antes.png"),
                img2=Image.open("despues.png"),
                label1="SIN PROTECCIÓN",
                label2="CON MANGLARES",
                make_responsive=True, # Deja que el CSS mande
                in_memory=True
            )
    else:
        st.error("Archivos antes.png y despues.png no detectados.")
