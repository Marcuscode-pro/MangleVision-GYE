import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from streamlit_image_comparison import image_comparison
from PIL import Image
import os
import plotly.express as px

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="MangleVision GYE", layout="wide")

# --- 2. ADVANCED CSS FOR FULL-WIDTH & DARK THEME ---
st.markdown("""
    <style>
    /* Remove padding and force max width */
    .block-container { 
        padding-top: 1rem !important; 
        padding-bottom: 0rem !important; 
        max-width: 95% !important; 
    }
    .stApp { background-color: #0e1117; }
    
    /* Metric styling */
    [data-testid="stMetric"] {
        background-color: #1d2127;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #30363d;
    }
    
    /* Force Image Comparison to be huge */
    iframe { 
        min-height: 800px !important; 
        width: 100% !important; 
        border: none;
    }
    
    /* Center Tabs */
    .stTabs [data-baseweb="tab-list"] { justify-content: center; gap: 50px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. STRATEGIC DATASET ---
@st.cache_data
def load_territorial_data():
    data = {
        'Sector': ['Urdesa', 'Puerto Hondo', 'La Puntilla', 'Guasmo Sur', 'Via a la Costa', 'Malecon 2000', 'Santay Island', 'Entre Rios'],
        'Lat': [-2.172, -2.195, -2.142, -2.258, -2.165, -2.191, -2.215, -2.150],
        'Lon': [-79.912, -80.055, -79.865, -79.898, -80.012, -79.878, -79.895, -79.875],
        'Elevation': [1.2, 0.5, 2.1, 0.8, 3.8, 2.5, 0.6, 1.9],
        'Population': [15000, 2000, 12000, 45000, 8000, 5000, 500, 7000]
    }
    return pd.DataFrame(data)

df = load_territorial_data()

# --- 4. DYNAMIC SIDEBAR (SIMULATION CONTROLS) ---
st.sidebar.title("🕹️ Control Panel")
# Using a clear icon for the logo fix
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/751/751291.png", width=80)

sea_level = st.sidebar.slider("Sea Level Rise (m)", 0.0, 5.0, 2.0, 0.1)
mangrove_barrier = st.sidebar.toggle("🌱 Activate Nature-Based Shield", value=True)

# Calculation Logic
# Mangroves reduce the impact/effective water height by 30%
impact_factor = 0.7 if mangrove_barrier else 1.0
effective_height = sea_level * impact_factor

at_risk_df = df[df['Elevation'] < effective_height]
total_at_risk = at_risk_df['Population'].sum()

st.sidebar.divider()
st.sidebar.metric(
    label="Population at Risk", 
    value=f"{total_at_risk:,}", 
    delta=f"-{int(total_at_risk*0.3):,} protected" if mangrove_barrier else None, 
    delta_color="inverse"
)

# --- 5. MAIN INTERFACE ---
st.title("🛡️ MangleVision Pro: Coastal Resilience")
tab1, tab2 = st.tabs(["🌐 RISK DASHBOARD", "🖼️ IMPACT VISUALIZATION (XL)"])

# ==========================================
# TAB 1: INTERACTIVE RISK MAP
# ==========================================
with tab1:
    st.subheader("Guayaquil Vulnerability Analysis")
    col_map, col_chart = st.columns([2, 1])
    
    with col_map:
        # Map visualization
        m = folium.Map(location=[-2.18, -79.90], zoom_start=12, tiles='CartoDB dark_matter')
        for i, row in df.iterrows():
            is_flooded = effective_height > row['Elevation']
            color = "#FF4B4B" if is_flooded else "#2EB82E"
            folium.CircleMarker(
                [row['Lat'], row['Lon']], 
                radius=row['Population']/4000 + 5, 
                color=color, 
                fill=True, 
                fill_opacity=0.6,
                popup=f"<b>{row['Sector']}</b><br>Elevation: {row['Elevation']}m"
            ).add_to(m)
        folium_static(m, width=900)
    
    with col_chart:
        st.write("### Exposure by Sector")
        fig = px.bar(df, x='Sector', y='Population', color='Elevation', 
                     color_continuous_scale='RdYlGn_r', template='plotly_dark')
        st.plotly_chart(fig, use_container_width=True)
        
        st.write("### Alert List")
        st.dataframe(at_risk_df[['Sector', 'Population']], hide_index=True, use_container_width=True)

# ==========================================
# TAB 2: BEFORE/AFTER COMPARISON
# ==========================================
with tab2:
    st.subheader("Visual Simulation: The Power of Mangrove Reforestation")
    st.info("Slide to compare current infrastructure vs. MangleVision's proposed green belt.")
    
    # Image Paths (Ensure these names match your files on GitHub)
    img_before = "antes.png"
    img_after = "despues.png"

    if os.path.exists(img_before) and os.path.exists(img_after):
        image_comparison(
            img1=Image.open(img_before),
            img2=Image.open(img_after),
            label1="CURRENT STATE",
            label2="MANGLEVISION PROPOSAL",
            width = 20000,
            make_responsive=True,
            starting_position=50
        )
        st.success("✅ Mangrove barriers dissipate up to 40% of wave energy, protecting urban value.")
    else:
        st.error("🚨 Assets Missing: Please ensure 'antes.png' and 'despues.png' are in your GitHub root.")
        st.write("Current files detected:", os.listdir("."))
