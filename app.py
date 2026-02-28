import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 1. Configuración de página
st.set_page_config(page_title="Ventas Anclu | BI", layout="wide")

@st.cache_data
def load_data():
    # El warning se quita con low_memory=False y forzamos que lea todo bien
    df = pd.read_csv("ventas_anclu.csv", low_memory=False)
    
    # LIMPIEZA CRÍTICA DE FECHAS
    df['fec_registro'] = pd.to_datetime(df['fec_registro'], errors='coerce')
    df = df.dropna(subset=['fec_registro']) # Eliminamos filas con fechas rotas
    
    df['Año'] = df['fec_registro'].dt.year
    df['Mes_Num'] = df['fec_registro'].dt.month
    
    meses_es = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 
                7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}
    df['Mes'] = df['Mes_Num'].map(meses_es)
    
    # LIMPIEZA DE MARCAS Y PRODUCTOS
    df['Marca'] = df['Marca'].fillna('SIN MARCA').astype(str).str.upper().str.strip()
    df['TipoProducto'] = df['TipoProducto'].fillna('OTROS').astype(str).str.strip()
    
    # Clasificación de Producto
    condicion = df['TipoProducto'].isin(['Kit Contado', 'Reposición', 'Kit Cuotas'])
    df['Producto'] = np.where(condicion, 'Equipos', 'Postpagos')
    
    return df

df = load_data()

# --- SIDEBAR ---
st.sidebar.title("🎛️ Filtros")
with st.sidebar:
    selected_year = st.selectbox("Año", options=sorted(df['Año'].unique(), reverse=True))
    df_year = df[df['Año'] == selected_year]
    selected_month = st.selectbox("Mes", options=df_year.sort_values('Mes_Num')['Mes'].unique())
    selected_centro = st.multiselect("Centro de Costo", options=sorted(df['centro_costo'].unique()), default=df['centro_costo'].unique())

# FILTRADO
df_selection = df[(df['Año'] == selected_year) & 
                  (df['Mes'] == selected_month) & 
                  (df['centro_costo'].isin(selected_centro))].copy()

# --- DASHBOARD ---
st.title("🚀 Dashboard de Ventas")

# KPIs
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Ventas", len(df_selection))
c2.metric("Postpagos", len(df_selection[df_selection['Producto'] == 'Postpagos']))
c3.metric("Equipos", len(df_selection[df_selection['Producto'] == 'Equipos']))
c4.metric("Vendedores", len(df_selection['vendedor'].unique()))

st.markdown("---")

col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.subheader("📊 Participación")
    # FORZAMOS CONTEO REAL
    fig_pie = px.pie(df_selection, names='TipoProducto', hole=0.5,
                     color_discrete_sequence=px.colors.qualitative.Safe)
    fig_pie.update_traces(textinfo='value+percent') # 'value' muestra las unidades
    st.plotly_chart(fig_pie, use_container_width=True)

with col_right:
    st.subheader("🏆 Top Marcas")
    df_marcas = df_selection[df_selection['Marca'] != 'TRAIDO'].copy()
    # Agrupamos manualmente para asegurar que el eje X sea numérico
    marcas_count = df_marcas['Marca'].value_counts().reset_index()
    marcas_count.columns = ['Marca', 'Unidades']
    marcas_count = marcas_count.head(10).sort_values('Unidades', ascending=True)
    
    fig_brands = px.bar(marcas_count, x='Unidades', y='Marca', orientation='h',
                        text='Unidades', color='Unidades', color_continuous_scale='Blues')
    st.plotly_chart(fig_brands, use_container_width=True)

# TENDENCIA (Solución definitiva al gráfico lineal raro)
st.subheader("📈 Tendencia Diaria")
df_selection['fecha_solo_dia'] = df_selection['fec_registro'].dt.normalize() # Quita horas/minutos
df_trend = df_selection.groupby('fecha_solo_dia').size().reset_index(name='Ventas')

fig_trend = px.area(df_trend, x='fecha_solo_dia', y='Ventas', line_shape='spline')
fig_trend.update_xaxes(dtick="D1", tickformat="%d %b") # Fuerza a mostrar días
st.plotly_chart(fig_trend, use_container_width=True)

# TABLAS
st.subheader("📈 Detalle por Vendedor y PDV")
col_v, col_p = st.columns([0.6, 0.4])
with col_v:
    t_vendedor = pd.crosstab(df_selection['vendedor'], df_selection['TipoProducto'])
    st.dataframe(t_vendedor.style.background_gradient(cmap='Blues', axis=None), use_container_width=True)
with col_p:
    t_pdv = pd.crosstab(df_selection['centro_costo'], df_selection['TipoProducto'])
    st.dataframe(t_pdv.style.background_gradient(cmap='Greens', axis=None), use_container_width=True)
