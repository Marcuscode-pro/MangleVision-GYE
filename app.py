import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from streamlit_image_comparison import image_comparison
from PIL import Image
import os
import plotly.express as px

# --- CONFIGURACIÓN DE PÁGINA (¡LAYOUT WIDE ES VITAL!) ---
st.set_page_config(page_title="MangleVision Pro 2026", layout="wide")

# ==========================================
# --- CSS AVANZADO: FUERZA ANCHO MÁXIMO ---
# ==========================================
st.markdown("""
    <style>
    /* 1. Elimina márgenes laterales de la página Streamlit */
    .block-container { 
        padding-top: 1rem; 
        padding-bottom: 1rem; 
        padding-left: 1rem !important; 
        padding-right: 1rem !important; 
        max-width: 100% !important; /* Forza el ancho completo de la ventana */
    }

    /* 2. Estilo para métricas y dashboard */
    .stApp { background-color: #0e1117; color: #fafafa; }
    .stMetric { background-color: #1d2127; border-radius: 10px; padding: 15px; border: 1px solid #30363d; }
    
    /* 3. Estilo para el mapa Folium (centrado) */
    .stFolium { 
        border-radius: 15px; overflow: hidden; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.3); 
        margin: 10px auto; /* Centra el mapa si es más pequeño que el ancho total */
    }

    # ==========================================
    # --- LA SOLUCIÓN DEFINITIVA PARA LA P2 ---
    # ==========================================
    /* 4. Encontramos el contenedor del comparador y lo forzamos a 100% */
    .element-container iframe {
        width: 100% !important;
        height: auto !important;
        min-height: 80vh; /* Altura mínima: 80% de la ventana del navegador */
    }

    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS (Mantenemos tu lógica potente) ---
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

# --- SIDEBAR DINÁMICO (Global para el dashboard) ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Escudo_de_Guayaquil.svg/1200px-Escudo_de_Guayaquil.svg.png", width=80)
st.sidebar.header("🕹️ Simulación MangleVision")

nivel_marea = st.sidebar.slider("Nivel de Marea (m)", 0.0, 5.0, 2.0, 0.1)
implementar_manglar = st.sidebar.toggle("🌱 Activar Barrera Viva", value=False)

# Cálculo dinámico para el Sidebar
reduccion = 0.75 if implementar_manglar else 1.0
pob_total_riesgo = df[df['Elevacion'] < (nivel_marea * reduccion)]['Poblacion'].sum()

st.sidebar.metric("Población en Riesgo", f"{pob_total_riesgo:,}", 
                  delta=f"-{int(pob_total_riesgo*0.3):,}" if implementar_manglar else None, delta_color="inverse")

# --- TITULO PRINCIPAL ---
st.title("🛡️ MangleVision Pro 2026")
tab_mapa, tab_comparador = st.tabs(["🌐 1. Panel Dinámico", "🖼️ 2. Visualización de Impacto (XL)"])

# ==========================================
# PESTAÑA 1: TU CÓDIGO DE MAPA (Sin cambios)
# ==========================================
with tab_mapa:
    col_map, col_info = st.columns([2, 1])
    
    with col_map:
        m = folium.Map(location=[-2.18, -79.90], zoom_start=12, tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google')
        for i, row in df.iterrows():
            nivel_final = nivel_marea * reduccion
            inundado = nivel_final > row['Elevacion']
            folium.CircleMarker(
                location=[row['Lat'], row['Lon']],
                radius=row['Poblacion']/3000 + 5,
                color="#FF4B4B" if inundado else "#2EB82E",
                fill=True, fill_opacity=0.7,
                popup=f"{row['Sector']}: {row['Elevacion']}m"
            ).add_to(m)
        folium_static(m, width=900)

    with col_info:
        st.write("### Análisis de Población")
        fig = px.bar(df, x='Sector', y='Poblacion', color='Elevacion', 
                     color_continuous_scale='RdYlGn_r', template='plotly_dark')
        fig.update_layout(margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# PESTAÑA 2: EL COMPARADOR GIGANTE (FORZADO)
# ==========================================
with tab_comparador:
    st.subheader("Simulación de Reforestación: Guayaquil Resiliente")
    
    # 1. Verificamos que las imágenes existan
    file_antes = "antes.png"
    file_despues = "despues.png"

    if os.path.exists(file_antes) and os.path.exists(file_despues):
        # 2. Cargamos las imágenes como siempre
        img_a = Image.open(file_antes)
        img_d = Image.open(file_despues)

        # ==========================================
        # --- SOLUCIÓN TÉCNICA FINAL ---
        # ==========================================
        # 3. NO forzamos el ancho en el componente de comparación.
        # Solo usamos 'make_responsive=True'. El CSS de arriba se encargará del resto.
        
        image_comparison(
            img1=img_a,
            img2=img_d,
            label1="ESTADO ACTUAL",
            label2="PROPUESTA MANGLEVISION",
            starting_position=50,
            show_labels=True,
            make_responsive=True, # IMPORTANTE: Se adapta al ancho del div principal
            in_memory=True
        )
        
        # Añadimos un panel de conclusión potente debajo del comparador gigante
        st.divider()
        st.success("""
        💡 **Conclusión:** La implementación de estas barreras vivas siguiendo el modelo MangleVision disipa hasta el 40% 
        de la energía hídrica, protegiendo la plusvalía y la infraestructura crítica de la ciudad.
        """)
    else:
        st.error(f"⚠️ Error: No se encontraron los archivos '{file_antes}' y '{file_despues}'.")
