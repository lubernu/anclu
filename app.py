import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 1. Configuración de página y estilo
st.set_page_config(page_title="Ventas Anclu | Business Intelligence", layout="wide")

# Estilo CSS para mejorar la apariencia de las métricas
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; color: #1f77b4; }
    .main { background-color: #f8f9fa; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    # RUTA RELATIVA PARA GITHUB
    df = pd.read_csv("ventas_anclu.csv")
    
    # Procesamiento de fechas
    df['fec_registro'] = pd.to_datetime(df['fec_registro'])
    df['Año'] = df['fec_registro'].dt.year
    df['Mes_Num'] = df['fec_registro'].dt.month
    
    meses_es = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    df['Mes'] = df['Mes_Num'].map(meses_es)
    
    # Limpieza de Marca y Valores
    df['Marca'] = df['Marca'].fillna('SIN MARCA').str.upper()
    df['valor_plan_'] = pd.to_numeric(df['valor_plan_'], errors='coerce').fillna(0)

    # Clasificación de Producto
    condicion = df['TipoProducto'].isin(['Kit Contado', 'Reposición', 'Kit Cuotas'])
    df['Producto'] = np.where(condicion, 'Equipos', 'Postpagos')

    return df

df = load_data()

# --- 1. FILTROS DESPLEGABLES (Sidebar) ---
st.sidebar.title("🎛️ Filtros de Control")

with st.sidebar:
    # Año (Selección única)
    list_anios = sorted(df['Año'].unique(), reverse=True)
    selected_year = st.selectbox("Año Fiscal", options=list_anios)
    
    # Mes (Selección única o múltiple - usando selectbox para orden)
    df_year = df[df['Año'] == selected_year]
    list_meses = df_year.sort_values('Mes_Num')['Mes'].unique()
    selected_month = st.selectbox("Mes", options=list_meses, index=0)

    # Centro de Costo (Multiselect que actúa como desplegable)
    list_centros = sorted(df['centro_costo'].unique())
    selected_centro = st.multiselect("Centro de Costo", options=list_centros, default=list_centros)

# Aplicar filtros
df_selection = df.query(
    "Año == @selected_year & Mes == @selected_month & centro_costo == @selected_centro"
)

# --- PANEL PRINCIPAL ---
st.title("🚀 Dashboard de Gestión de Ventas")
st.markdown(f"**Periodo Actual:** {selected_month} de {selected_year}")

# Cálculo de métricas
cantPost = (df_selection['Producto'] == 'Postpagos').sum()
cantEquip = (df_selection['Producto'] == 'Equipos').sum()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Ventas", f"{len(df_selection):,}")
m2.metric("Postpagos", f"{cantPost:,}")
m3.metric("Equipos", f"{cantEquip:,}")
m4.metric("Vendedores Activos", len(df_selection['vendedor'].unique()))

st.markdown("---")

# --- 2. PARTICIPACIÓN Y TOP MARCAS ---
col_prod, col_brand = st.columns([1, 1.2])

with col_prod:
    st.subheader("📊 Participación por Producto")
    # Usamos reset_index() y contamos una columna específica que sabemos que no tiene nulos
    prod_counts = df_selection.groupby('TipoProducto')['vendedor'].count().reset_index(name='Cantidad')
    
    fig_pie = px.pie(prod_counts, 
                     values='Cantidad', 
                     names='TipoProducto', 
                     hole=0.5, 
                     color_discrete_sequence=px.colors.qualitative.Safe)
    
    fig_pie.update_traces(textinfo='value+percent', textfont_size=12)
    st.plotly_chart(fig_pie, use_container_width=True)
    
with col_brand:
    st.subheader("🏆 Top Marcas Vendidas")
    df_marcas = df_selection[df_selection['Marca'] != 'TRAIDO'].copy()
    # Contamos sobre la columna 'vendedor' para asegurar que sume unidades
    top_marcas = df_marcas.groupby('Marca')['vendedor'].count().reset_index(name='Unidades')
    top_marcas = top_marcas.sort_values('Unidades', ascending=True).tail(10)
    
    fig_brands = px.bar(top_marcas, 
                        x='Unidades', 
                        y='Marca', 
                        orientation='h',
                        color='Unidades', 
                        color_continuous_scale='Blues',
                        text='Unidades')
    
    fig_brands.update_layout(showlegend=False, yaxis_title=None)
    st.plotly_chart(fig_brands, use_container_width=True)
    
# --- 3. TENDENCIA DIARIA CORREGIDA ---
st.subheader("📈 Tendencia Diaria de Ventas")

# Agrupamos por día asegurando que no haya huecos o errores de línea
df_timeline = df_selection.copy()
df_timeline['fecha_dia'] = df_timeline['fec_registro'].dt.date
df_timeline = df_timeline.groupby('fecha_dia').size().reset_index(name='Ventas')
df_timeline = df_timeline.sort_values('fecha_dia')

fig_time = px.area(
    df_timeline, 
    x='fecha_dia', 
    y='Ventas', 
    line_shape='spline',
    color_discrete_sequence=['#00CC96']
)

fig_time.update_layout(
    xaxis_title="Día del Mes",
    yaxis_title="Cantidad de Registros",
    hovermode="x unified"
)
st.plotly_chart(fig_time, use_container_width=True)

# --- 4. TABLAS DE RENDIMIENTO ---
st.subheader("📈 Análisis por Vendedor y PDV")

# Tablas de contingencia
conteo_vendedor = pd.crosstab(df_selection['vendedor'], df_selection['TipoProducto'])
conteo_pdv = pd.crosstab(df_selection['centro_costo'], df_selection['TipoProducto'])

# Aplicar estilos (Requiere matplotlib en requirements.txt)
styled_vendedor = conteo_vendedor.style.background_gradient(cmap='Blues', axis=None).format(precision=0)
styled_pdv = conteo_pdv.style.background_gradient(cmap='Greens', axis=None).format(precision=0)

col1, col2 = st.columns([0.6, 0.4])
with col1:
    st.markdown("**Desempeño por Vendedor**")
    st.dataframe(styled_vendedor, use_container_width=True)
with col2:
    st.markdown("**Desempeño por Centro de Costo**")
    st.dataframe(styled_pdv, use_container_width=True)

# Vista Detallada
with st.expander("🔍 Ver Detallado General de Transacciones"):
    st.dataframe(df_selection, use_container_width=True)

