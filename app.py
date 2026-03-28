import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from streamlit_image_comparison import image_comparison
from PIL import Image
import os
import plotly.express as px

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="MangleVision Pro 2026", layout="wide")

# ==========================================
# --- CSS PARA MÁXIMA AMPLITUD (SIN COMPRESIÓN) ---
# ==========================================
st.markdown("""
    <style>
    /* Estética Dark Mode */
    .stApp { background-color: #0e1117; }
    .stMetric { background-color: #1d2127; border-radius: 10px; padding: 15px; border: 1px solid #30363d; }
    
    /* ELIMINAR MÁRGENES PARA QUE NO SE VEA CHICO */
    .block-container { 
        padding-top: 1rem; 
        padding-bottom: 1rem; 
        padding-left: 1rem !important; 
        padding-right: 1rem !important; 
        max-width: 100% !important;
    }

    /* Forzar que el comparador use todo el ancho */
    .stImageComparison {
        width: 100% !important;
        margin: 0 auto;
    }
    
    .stFolium { border-radius: 15px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS ---
@st.cache_data
def get_territorial_data():
    data = {
        'Sector': ['Urdesa Central', 'Puerto Hondo', 'La Puntilla', 'Guasmo Sur', 'Vía a la Costa', 'Malecón 2000', 'Isla Santay', 'Entre Ríos'],
        'Lat': [-2.172, -2.195, -2.142, -2.258, -2.165, -2.191, -2.215, -2.150],
        'Lon': [-79.912, -80.055, -79.865, -79.898, -80.012, -79.878, -79.895, -79.875],
        'Elevacion': [1.2, 0.5, 2.1, 0.8, 3.8, 2.5, 0.6, 1.9],
        'Poblacion': [15000, 2000, 12000, 45000, 8000, 5000, 500, 7000]
    }
    return pd.DataFrame(data)

df = get_territorial_data()

# --- SIDEBAR DINÁMICO ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Escudo_de_Guayaquil.svg/1200px-Escudo_de_Guayaquil.svg.png", width=80)
st.sidebar.header("🕹️ Simulación MangleVision")

nivel_marea = st.sidebar.slider("Nivel de Marea (m)", 0.0, 5.0, 2.0, 0.1)
implementar_manglar = st.sidebar.toggle("🌱 Activar Barrera Viva", value=False)

# Cálculo de impacto
reduccion = 0.75 if implementar_manglar else 1.0
nivel_final = nivel_marea * reduccion
afectados_df = df[df['Elevacion'] < nivel_final]
pob_riesgo = afectados_df['Poblacion'].sum()

st.sidebar.divider()
st.sidebar.metric("Población en Riesgo", f"{pob_riesgo:,}", 
                  delta=f"-{int(pob_riesgo*0.25):,} por manglar" if implementar_manglar else None, 
                  delta_color="inverse")

# --- TITULO PRINCIPAL ---
st.title("🛡️ MangleVision Pro 2026")
tab_mapa, tab_comparador = st.tabs(["🌐 PANEL DINÁMICO", "🖼️ VISUALIZACIÓN DE IMPACTO (XL)"])

# ==========================================
# PESTAÑA 1: MAPA + GRÁFICO
# ==========================================
with tab_mapa:
    col_izq, col_der = st.columns([2, 1])
    
    with col_izq:
        m = folium.Map(location=[-2.18, -79.90], zoom_start=12, tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google')
        for i, row in df.iterrows():
            inundado = nivel_final > row['Elevacion']
            folium.CircleMarker(
                location=[row['Lat'], row['Lon']],
                radius=row['Poblacion']/3000 + 5,
                color="#FF4B4B" if inundado else "#2EB82E",
                fill=True, fill_opacity=0.7,
                popup=f"{row['Sector']}: {row['Elevacion']}m"
            ).add_to(m)
        folium_static(m, width=900)

    with col_der:
        st.write("### Análisis de Población")
        fig = px.bar(df, x='Sector', y='Poblacion', color='Elevacion', 
                     color_continuous_scale='RdYlGn_r', template='plotly_dark')
        st.plotly_chart(fig, use_container_width=True)
        
        st.write("### Sectores en Alerta")
        st.dataframe(afectados_df[['Sector', 'Poblacion']], hide_index=True, use_container_width=True)

# ==========================================
# PESTAÑA 2: COMPARADOR XL (SIN COMPRESIÓN)
# ==========================================
with tab_comparador:
    st.subheader("Simulación Visual de Reforestación")
    
    # IMPORTANTE: Asegúrate que tus fotos se llamen antes.png y despues.png
    if os.path.exists("antes.png") and os.path.exists("despues.png"):
        image_comparison(
            img1=Image.open("antes.png"),
            img2=Image.open("despues.png"),
            label1="ESTADO ACTUAL",
            label2="PROPUESTA MANGLEVISION",
            make_responsive=True, # Esto hace que use todo el ancho del contenedor
            in_memory=True
        )
        st.success("✅ La barrera de manglares reduce la energía del oleaje y protege la infraestructura.")
    else:
        st.error("⚠️ Sube 'antes.png' y 'despues.png' a la carpeta del proyecto.")
