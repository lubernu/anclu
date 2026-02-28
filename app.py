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
    df = pd.read_csv("ventas_anclu.csv")
    df['fec_registro'] = pd.to_datetime(df['fec_registro'])
    df['Año'] = df['fec_registro'].dt.year
    df['Mes_Num'] = df['fec_registro'].dt.month
    
    meses_es = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    df['Mes'] = df['Mes_Num'].map(meses_es)
    df['Marca'] = df['Marca'].fillna('SIN MARCA').str.upper()
    df['valor_plan_'] = pd.to_numeric(df['valor_plan_'], errors='coerce').fillna(0)

    condicion = df['TipoProducto'].isin(['Kit Contado', 'Reposición', 'Kit Cuotas'])
    df['Producto'] = np.where(condicion, 'Equipos', 'Postpagos')

    return df

df = load_data()

# --- 1. FILTROS DESPLEGABLES (Sidebar) ---
st.sidebar.title("🎛️ Filtros de Control")

# Agrupamos los filtros en un expander si quieres que la sidebar sea aún más limpia
with st.sidebar:
    # Año (Selección única)
    selected_year = st.selectbox("Año Fiscal", options=sorted(df['Año'].unique(), reverse=True))
    
    # Mes (Multiselect pero actúa como desplegable)
    df_year = df[df['Año'] == selected_year]
    list_meses = df_year.sort_values('Mes_Num')['Mes'].unique()
    selected_month = st.selectbox("Meses", options=list_meses, index=0)
    #selected_month = st.multiselect("Meses", options=list_meses, default=list_meses)

# Aplicar filtros
df_selection = df.query(
    "Año == @selected_year & Mes == @selected_month"
)

# --- PANEL PRINCIPAL ---
st.title("🚀 Dashboard de Gestión de Ventas")
st.markdown(f"**Periodo:** {selected_year} | {', '.join(selected_month[:3])}...")

cantPost = (df_selection['Producto'] == 'Postpagos').sum()
cantEquip = (df_selection['Producto'] == 'Equipos').sum()
# Métricas rápidas
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Ventas", f"{len(df_selection):,}")
m2.metric("Postpagos", cantPost)
m3.metric("Equipos", cantEquip)
m4.metric("Vendedores Activos", len(df_selection['vendedor'].unique()))

st.markdown("---")

# --- 2. PARTICIPACIÓN POR TIPO DE PRODUCTO ---
col_prod, col_brand = st.columns([1, 1.2])

with col_prod:
    st.subheader("📊 Participación por Producto")
    # Calculamos el % de participación
    prod_counts = df_selection['TipoProducto'].value_counts().reset_index()
    prod_counts.columns = ['TipoProducto', 'Cantidad']
    prod_counts['%'] = (prod_counts['Cantidad'] / prod_counts['Cantidad'].sum() * 100).round(1)
    
    # Gráfico de Dona para participación
    fig_pie = px.pie(prod_counts, values='Cantidad', names='TipoProducto', 
                     hole=0.5, 
                     color_discrete_sequence=px.colors.qualitative.Safe,
                     hover_data=['%'])
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

# --- 3. TOP MARCAS (SIN "TRAIDO") ---
with col_brand:
    st.subheader("🏆 Top Marcas Vendidas")
    # Filtramos "TRAIDO" según tu solicitud
    df_marcas = df_selection[df_selection['Marca'] != 'TRAIDO']
    
    top_marcas = df_marcas.groupby('Marca').size().reset_index(name='Ventas')
    top_marcas = top_marcas.sort_values('Ventas', ascending=True).tail(10) # Top 10
    
    fig_brands = px.bar(top_marcas, x='Ventas', y='Marca', orientation='h',
                        color='Ventas', color_continuous_scale='Blues',
                        text_auto='.2s')
    fig_brands.update_layout(showlegend=False, yaxis_title=None)
    st.plotly_chart(fig_brands, use_container_width=True)

# Evolución Temporal Corregida
# Reemplaza tu bloque de "Evolución Temporal" con este:
st.subheader("📈 Tendencia Diaria de Ventas")

# Aseguramos que la fecha sea solo día (sin hora) y sumamos
df_timeline = df_selection.copy()
df_timeline['fecha_dia'] = df_timeline['fec_registro'].dt.date
df_timeline = df_timeline.groupby('fecha_dia').size().reset_index(name='Ventas')
df_timeline = df_timeline.sort_values('fecha_dia') # Ordenar cronológicamente

fig_time = px.area(
    df_timeline, 
    x='fecha_dia', 
    y='Ventas', 
    line_shape='spline',
    color_discrete_sequence=['#00CC96']
)
st.plotly_chart(fig_time, use_container_width=True)
# Ventas por asesor y pdv
st.subheader("📈 Vendedores y PDV")

# Crear tablas de contingencia con los datos filtrados
conteo_vendedor_tipo = pd.crosstab(df_selection['vendedor'], df_selection['TipoProducto'])
conteo_pdv = pd.crosstab(df_selection['centro_costo'], df_selection['TipoProducto'])

# Aplicar estilo: gradiente de fondo y formato entero
styled_vendedor = conteo_vendedor_tipo.style.background_gradient(cmap='Blues', axis=None).format(precision=0)
styled_pdv = conteo_pdv.style.background_gradient(cmap='Greens', axis=None).format(precision=0)

# Mostrar en columnas
col1, col2 = st.columns([.6,.4])
with col1:
    st.markdown("**Conteo por Vendedor**")
    st.dataframe(styled_vendedor, use_container_width=True)
with col2:
    st.markdown("**Conteo por Centro de Costo (PDV)**")
    st.dataframe(styled_pdv, use_container_width=True)

# Mostrar el dataframe original filtrado )
st.subheader('Detallado General')

st.dataframe(df_selection)
