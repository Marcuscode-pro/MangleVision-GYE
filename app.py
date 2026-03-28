import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from streamlit_image_comparison import image_comparison
from PIL import Image, ImageOps
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="MangleVision Pro 2026", layout="wide")

# ==========================================
# --- CSS PARA HACER EL COMPARADOR GIGANTE ---
# ==========================================
st.markdown("""
    <style>
    /* Estilo general para métricas y dashboard */
    .reportview-container { background: #0e1117; }
    .stMetric { background-color: #1d2127; border-radius: 10px; padding: 15px; border: 1px solid #30363d; }
    
    /* MODIFICACIÓN PRINCIPAL: Usamos padding mínimo para maximizar el ancho */
    .block-container { 
        padding-top: 1rem; 
        padding-bottom: 1rem; 
        padding-left: 1rem !important;  /* Casi sin margen izquierdo */
        padding-right: 1rem !important; /* Casi sin margen derecho */
    }
    
    /* Estilo para el mapa Folium */
    .stFolium { 
        border-radius: 15px; 
        overflow: hidden; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.1); 
        margin-left: auto; margin-right: auto; /* Centrar el mapa */
    }
    
    /* Estilo para el contenedor del comparador de imágenes */
    .stImageComparison {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2); /* Sombra más fuerte para impacto */
        margin-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ MangleVision: Sistema de Resiliencia Costera")
st.markdown("### Diagnóstico, Propuesta de Restauración y Simulación de Impacto")

# --- CREACIÓN DE PESTAÑAS ---
tab_mapa, tab_comparador = st.tabs(["🌐 1. Mapa de Riesgo Dinámico", "🖼️ 2. Propuesta Antes/Después (GIGANTE)"])

# --- SIDEBAR: VARIABLES DEL MODELO (Global para el dashboard) ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Escudo_de_Guayaquil.svg/1200px-Escudo_de_Guayaquil.svg.png", width=80)
st.sidebar.header("🕹️ Panel de Simulación")

nivel_marea = st.sidebar.slider("Nivel de Agua/Marea (m)", 0.0, 5.0, 2.0, 0.1)
implementar_manglar = st.sidebar.toggle("🌱 Implementar Barrera de Manglar", value=False)

st.sidebar.divider()
capa_riesgo = st.sidebar.checkbox("Mostrar Riesgo Hídrico", value=True)
capa_restauracion = st.sidebar.checkbox("Mostrar Zonas de Restauración", value=True)

# ==========================================
# PESTAÑA 1: TU CÓDIGO DE MAPA DE RIESGO
# ==========================================
with tab_mapa:
    def get_territorial_data():
        data = {
            'Sector': ['Urdesa Central', 'Puerto Hondo', 'La Puntilla', 'Guasmo Sur', 'Vía a la Costa (Bajo)', 'Malecón 2000', 'Isla Santay', 'Entre Ríos'],
            'Lat': [-2.172, -2.195, -2.142, -2.258, -2.165, -2.191, -2.215, -2.150],
            'Lon': [-79.912, -80.055, -79.865, -79.898, -80.012, -79.878, -79.895, -79.875],
            'Elevacion': [1.2, 0.5, 2.1, 0.8, 3.8, 2.5, 0.6, 1.9],
            'Distancia_Agua_m': [10, 5, 20, 15, 500, 5, 2, 25],
            'Estado_Ecologico': ['Degradado', 'Sano', 'Desaparecido', 'Degradado', 'N/A', 'Desaparecido', 'Sano', 'Desaparecido'],
            'Poblacion': [15000, 2000, 12000, 45000, 8000, 5000, 500, 7000]
        }
        return pd.DataFrame(data)

    df = get_territorial_data()

    def calcular_prioridad(row):
        score = 0
        if row['Elevacion'] < 2.0: score += 40
        if row['Distancia_Agua_m'] < 50: score += 30
        if row['Estado_Ecologico'] in ['Degradado', 'Desaparecido']: score += 20
        if row['Poblacion'] > 10000: score += 10
        if score >= 70: return "ALTA", "#FF4B4B"
        if score >= 40: return "MEDIA", "#FFA500"
        return "BAJA", "#2EB82E"

    # Centramos el mapa y lo hacemos ancho
    m = folium.Map(location=[-2.18, -79.90], zoom_start=12, tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google Satélite')

    for i, row in df.iterrows():
        prioridad, color_prioridad = calcular_prioridad(row)
        reducir_impacto = 0.8 if implementar_manglar and row['Distancia_Agua_m'] < 50 else 1.0
        nivel_efectivo = nivel_marea * reducir_impacto
        esta_inundado = nivel_efectivo > row['Elevacion']
        
        if capa_riesgo:
            folium.Circle(
                location=[row['Lat'], row['Lon']],
                radius=row['Poblacion']/50 if esta_inundado else 100,
                color=color_prioridad if esta_inundado else "cyan",
                fill=True, fill_opacity=0.4 if esta_inundado else 0.1,
                tooltip=f"Prioridad: {prioridad}"
            ).add_to(m)

        if capa_restauracion and row['Distancia_Agua_m'] < 100 and row['Estado_Ecologico'] != 'Sano':
            folium.Marker(
                location=[row['Lat'] + 0.002, row['Lon'] + 0.002],
                icon=folium.Icon(color="green", icon="leaf")
            ).add_to(m)

    # Renderizamos el mapa con un ancho grande pero contenido (1200px)
    folium_static(m, width=1200)

    # --- MÉTRICAS (Mantenemos el dashboard técnico) ---
    c1, c2, c3, c4 = st.columns(4)
    total_afectados = df[nivel_marea > df['Elevacion']]['Poblacion'].sum()
    with c1: st.metric("Pob. Riesgo Crítico", f"{total_afectados:,}")
    with c2: st.metric("Reducción Riesgo", f"-{30 if implementar_manglar else 0}%")
    with c3: st.metric("Zonas Aptas", len(df[df['Distancia_Agua_m'] < 100]))
    with c4: st.metric("Marea Actual", f"{nivel_marea}m")

# ==========================================
# PESTAÑA 2: COMPARADOR (¡AHORA GIGANTE!)
# ==========================================
with tab_comparador:
    st.subheader("Visualización de Impacto: Barreras Vivas (Pantalla Completa)")
    st.write("Desliza lentamente para observar el escudo natural protegiendo la urbanización.")
    
    file_antes = "antes.png"
    file_despues = "despues.png"

    if os.path.exists(file_antes) and os.path.exists(file_despues):
        # 1. Cargamos las imágenes como siempre
        img_a = Image.open(file_antes).convert("RGB")
        img_d = Image.open(file_despues).convert("RGB")

        # 2. Forzamos la alineación (por si acaso las capturas saltaron un poco)
        img_d_aligned = ImageOps.fit(img_d, img_a.size, centering=(0.5, 0.5))

        # ==========================================
        # --- SOLUCIÓN: MAXIMIZAR ANCHO ---
        # ==========================================
        # 3. Usamos el componente image_comparison con un ancho MUY grande (ej: 1400px)
        # y make_responsive=True para que ocupe todo el ancho de la ventana del navegador.
        image_comparison(
            img1=img_a,
            img2=img_d_aligned,
            label1="ESTADO ACTUAL",
            label2="PROPUESTA MANGLEVISION",
            width=1400,             # Ancho forzado (grande)
            make_responsive=True,   # Adaptable al 100% de la ventana
            in_memory=True
        )
        
        # Añadimos un panel de conclusión potente debajo del comparador grande
        st.divider()
        st.success("""
        💡 **Conclusión:** Al reforestar los bordes ribereños en sectores como La Puntilla, Isla Santay y Guasmo Sur, 
        transformamos zonas vulnerables en infraestructura verde resiliente, absorbiendo hasta el 40% de la energía de la marea.
        """)
    else:
        st.error("⚠️ No se encuentran los archivos 'antes.png' y 'despues.png'.")