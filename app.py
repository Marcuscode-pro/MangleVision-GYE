import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from streamlit_image_comparison import image_comparison
from PIL import Image
import os
import plotly.express as px

# --- 1. CONFIGURACIÓN (WIDER LAYOUT) ---
st.set_page_config(page_title="MangleVision Pro 2026", layout="wide")

# --- 2. CSS PARA ELIMINAR COMPRESIÓN ---
st.markdown("""
    <style>
    /* Estilo Dark y Métricas */
    .stApp { background-color: #0e1117; }
    .stMetric { background-color: #1d2127; border-radius: 10px; padding: 15px; border: 1px solid #30363d; }
    
    /* FORZAR ANCHO MÁXIMO (Esto evita que se vea pequeño) */
    .block-container { 
        padding-top: 1rem; 
        padding-bottom: 1rem; 
        padding-left: 2rem !important; 
        padding-right: 2rem !important; 
        max-width: 100% !important;
    }

    /* Quitar bordes del comparador */
    .stImageComparison { border-radius: 15px; overflow: hidden; }
    
    /* Hacer que el iframe del comparador sea alto */
    iframe { min-height: 700px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATOS ESTRATÉGICOS ---
@st.cache_data
def get_territorial_data():
    data = {
        'Sector': ['Urdesa', 'Puerto Hondo', 'La Puntilla', 'Guasmo Sur', 'Vía a la Costa', 'Malecón 2000', 'Isla Santay', 'Entre Ríos'],
        'Lat': [-2.172, -2.195, -2.142, -2.258, -2.165, -2.191, -2.215, -2.150],
        'Lon': [-79.912, -80.055, -79.865, -79.898, -80.012, -79.878, -79.895, -79.875],
        'Elevacion': [1.2, 0.5, 2.1, 0.8, 3.8, 2.5, 0.6, 1.9],
        'Poblacion': [15000, 2000, 12000, 45000, 8000, 5000, 500, 7000]
    }
    return pd.DataFrame(data)

df = get_territorial_data()

# --- 4. SIDEBAR (DASHBOARD DINÁMICO) ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Escudo_de_Guayaquil.svg/1200px-Escudo_de_Guayaquil.svg.png", width=80)
st.sidebar.header("🕹️ Simulación")

nivel_marea = st.sidebar.slider("Nivel de Marea (m)", 0.0, 5.0, 2.0, 0.1)
implementar_manglar = st.sidebar.toggle("🌱 Activar Barrera Viva", value=False)

# Lógica de impacto
reduccion = 0.75 if implementar_manglar else 1.0
nivel_final = nivel_marea * reduccion
afectados_df = df[df['Elevacion'] < nivel_final]
pob_riesgo = afectados_df['Poblacion'].sum()

st.sidebar.divider()
st.sidebar.metric("Población en Riesgo", f"{pob_riesgo:,}", 
                  delta=f"-{int(pob_riesgo*0.25):,} protegidos" if implementar_manglar else None, 
                  delta_color="inverse")

# --- 5. CUERPO PRINCIPAL ---
st.title("🛡️ MangleVision Pro 2026")
tab1, tab2 = st.tabs(["🌐 PANEL DINÁMICO DE RIESGO", "🖼️ VISUALIZACIÓN DE IMPACTO XL"])

# ==========================================
# PESTAÑA 1: EL DASHBOARD COMPLETO
# ==========================================
with tab1:
    col_mapa, col_stats = st.columns([2, 1])
    
    with col_mapa:
        st.subheader("Mapa de Vulnerabilidad")
        m = folium.Map(location=[-2.18, -79.90], zoom_start=12, tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google')
        for i, row in df.iterrows():
            inundado = nivel_final > row['Elevacion']
            folium.CircleMarker(
                location=[row['Lat'], row['Lon']],
                radius=row['Poblacion']/3000 + 5,
                color="#FF4B4B" if inundado else "#2EB82E",
                fill=True, fill_opacity=0.7,
                popup=f"<b>{row['Sector']}</b>"
            ).add_to(m)
        folium_static(m, width=800)

    with col_stats:
        st.subheader("Población Expuesta")
        fig = px.bar(df, x='Sector', y='Poblacion', color='Elevacion', 
                     color_continuous_scale='RdYlGn_r', template='plotly_dark')
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(afectados_df[['Sector', 'Poblacion']], hide_index=True, use_container_width=True)

# ==========================================
# PESTAÑA 2: COMPARADOR (SIN COLUMNAS = MÁXIMO ANCHO)
# ==========================================
with tab2:
    st.subheader("Simulación Visual: El Poder del Manglar")
    
    # Verificamos archivos
    if os.path.exists("antes.png") and os.path.exists("despues.png"):
        # CARGAMOS DIRECTO AL ANCHO DE LA PÁGINA
        image_comparison(
            img1=Image.open("antes.png"),
            img2=Image.open("despues.png"),
            label1="ESTADO ACTUAL",
            label2="PROPUESTA MANGLEVISION",
            width=2000, # Forzamos un número grande
            make_responsive=True # Dejamos que el CSS se encargue de ajustarlo al navegador
        )
    else:
        st.error("🚨 Sube 'antes.png' y 'despues.png' a GitHub.")
