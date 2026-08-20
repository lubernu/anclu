import streamlit as st
import pandas as pd
import numpy as np

# 1. Configuración de página
st.set_page_config(page_title="Dashboard Primera Llamada Anclu", layout="wide")

@st.cache_data
def load_data():
    columnas_rp = ['DISTRIBUIDOR','PRODUCTO','PRIM_LLAMADA_ACTIVACION', 'MIN','IMEI']
    columnas_ventas = ['centro_costo','vendedor','fec_registro','telefono','imei','TipoProducto','Marca']
    
    df_ventas = pd.read_csv("ventas_anclu.csv", low_memory=False, dtype='str', usecols=columnas_ventas)
    df_rp = pd.read_csv("archivo_Prepago_Anclu.txt", sep=';', low_memory=False, usecols=columnas_rp, dtype='str')
    df_rp_antiguo = pd.read_csv("Archivo_Prepago_Anclu_Antiguo.txt", sep='\t', low_memory=False, dtype='str')
    
    # Limpieza estricta de fechas
    df_ventas['fec_registro'] = pd.to_datetime(df_ventas['fec_registro'], errors='coerce')
    df_ventas = df_ventas.dropna(subset=['fec_registro'])

    # Limpieza de textos
    df_ventas['Marca'] = df_ventas['Marca'].fillna('SIN MARCA').astype(str).str.upper().str.strip()
    df_ventas['TipoProducto'] = df_ventas['TipoProducto'].fillna('OTROS').astype(str).str.strip()

    # Clasificación lógica
    condicion = df_ventas['TipoProducto'].isin(['Kit Contado', 'Reposición', 'Kit Cuotas'])
    df_ventas['Producto'] = np.where(condicion, 'Equipos', 'Postpagos')  

    df_ventas = df_ventas[df_ventas['TipoProducto'] == 'Kit Contado']     
    return df_ventas, df_rp

# Cargar datos
df_ventas_total, df_rp = load_data()
df_ventas = df_ventas_total[df_ventas_total['fec_registro'] >= pd.to_datetime('2026-01-01')]

# 🔄 Cruce de archivos
resultado = df_ventas.merge(
    df_rp[['IMEI', 'MIN','PRIM_LLAMADA_ACTIVACION']],
    left_on='imei', right_on='IMEI', how='left'
)

Fact_sin_llamada = resultado[resultado['PRIM_LLAMADA_ACTIVACION'].isna()].reset_index(drop=True)
Fact_Sin_primer_preactivar = Fact_sin_llamada[Fact_sin_llamada['MIN'].isna()].reset_index(drop=True)
Fact_Por_llamar = Fact_sin_llamada[Fact_sin_llamada['MIN'].notna()].reset_index(drop=True)

resultado1 = df_rp.merge(
    df_ventas_total[['imei','telefono','vendedor']],
    left_on='IMEI', right_on='imei', how='left'
)
rp_primer_llamada = resultado1[resultado1['PRIM_LLAMADA_ACTIVACION'].notna()].reset_index(drop=True)
rp_sin_facturar = rp_primer_llamada[rp_primer_llamada['imei'].isna()].reset_index(drop=True)
rp_sin_facturar = rp_sin_facturar[rp_sin_facturar['PRODUCTO']== 'KIT PREPAGO CONTADO'].reset_index(drop=True)

# 📊 CÁLCULO DE KPIs
kpi_sin_preactivar = len(Fact_Sin_primer_preactivar)
kpi_por_llamar = len(Fact_Por_llamar)
kpi_sin_llamada = len(Fact_sin_llamada)
kpi_rp_sin_facturar = len(rp_sin_facturar)

# 🎨 ESTILOS CSS PROFESIONALES
st.markdown("""
<style>
    .header-box {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 20px;
        text-align: center;
    }
    .kpi-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 20px 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        text-align: center;
        border-left: 5px solid #2196F3;
        transition: transform 0.2s;
    }
    .kpi-card:hover { transform: translateY(-4px); }
    .kpi-icon { font-size: 26px; margin-bottom: 6px; }
    .kpi-title { font-size: 13px; color: #666; font-weight: 600; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px; }
    .kpi-value { font-size: 28px; font-weight: 800; color: #1a1a1a; }
    .section-title { font-size: 18px; font-weight: 600; color: #333; margin: 24px 0 12px 0; border-left: 4px solid #2a5298; padding-left: 10px; }
</style>
""", unsafe_allow_html=True)

# 🖼️ HEADER
st.markdown('<div class="header-box"><h1 style="margin:0;">🚀 Dashboard Primera Llamada - Anclu</h1><p style="margin:8px 0 0; opacity:0.9;">Monitoreo de primer llamada y gestión de equipos</p></div>', unsafe_allow_html=True)

# 📈 TARJETAS KPI
col1, col2, col3, col4, col5 = st.columns(5)
kpis = [
    ("🚫", "Sin Preactivar", kpi_sin_preactivar, "#FF9800"),
    ("📞", "Por Primera Llamada", kpi_por_llamar, "#4CAF50"),
    ("⚠️", "Total Sin Llamada", kpi_sin_llamada, "#F44336"),
    ("📄", "1ra Llamada S/Fact", kpi_rp_sin_facturar, "#9C27B0")
]

for i, (icon, title, value, color) in enumerate(kpis):
    with [col1, col2, col3, col4, col5][i]:
        st.markdown(f'''
        <div class="kpi-card" style="border-left-color: {color};">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value:,}</div>
        </div>
        ''', unsafe_allow_html=True)

st.divider()

# 📑 TABLAS ORGANIZADAS POR PESTAÑAS
tab1, tab2, tab3, tab4 = st.tabs([
    "🚫 Sin Preactivar", 
    "📞 Por Primera Llamada", 
    "⚠️ Total Sin Llamada", 
    "📄 1ra Llamada Sin Facturar"
])

with tab1:
    st.dataframe(Fact_Sin_primer_preactivar, use_container_width=True, hide_index=True, height=400)
with tab2:
    st.dataframe(Fact_Por_llamar, use_container_width=True, hide_index=True, height=400)
with tab3:
    st.dataframe(Fact_sin_llamada, use_container_width=True, hide_index=True, height=400)
with tab4:
    st.dataframe(rp_sin_facturar, use_container_width=True, hide_index=True, height=400)
