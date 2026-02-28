import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. Configuración de página
st.set_page_config(page_title="Dashboard Anclu | Final", layout="wide")

@st.cache_data
def load_data():
    # Carga segura
    df = pd.read_csv("ventas_anclu.csv", low_memory=False)
    # Conversión estricta de fechas
    df['fec_registro'] = pd.to_datetime(df['fec_registro'], errors='coerce')
    df = df.dropna(subset=['fec_registro'])
    
    # Extraer tiempos
    df['Año'] = df['fec_registro'].dt.year
    df['Mes_Num'] = df['fec_registro'].dt.month
    meses_es = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 
                7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}
    df['Mes'] = df['Mes_Num'].map(meses_es)
    
    # Limpieza de textos
    df['Marca'] = df['Marca'].fillna('SIN MARCA').astype(str).str.upper().str.strip()
    df['TipoProducto'] = df['TipoProducto'].fillna('OTROS').astype(str).str.strip()
    return df

df = load_data()

# --- SIDEBAR (FILTROS) ---
st.sidebar.title("🎛️ Filtros")
with st.sidebar:
    selected_year = st.selectbox("Año", options=sorted(df['Año'].unique(), reverse=True))
    df_year = df[df['Año'] == selected_year]
    selected_month = st.selectbox("Mes", options=df_year.sort_values('Mes_Num')['Mes'].unique())
    
    centros_lista = sorted(df['centro_costo'].unique())
    selected_centro = st.multiselect("Centro de Costo", options=centros_lista, default=centros_lista)

# --- FILTRADO DE DATOS (Aquí se define df_selection) ---
df_selection = df[
    (df['Año'] == selected_year) & 
    (df['Mes'] == selected_month) & 
    (df['centro_costo'].isin(selected_centro))
].copy()

st.title(f"🚀 Dashboard de Ventas: {selected_month} {selected_year}")

# --- BLOQUE DE GRÁFICOS ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Participación")
    # Tabla de frecuencia manual para evitar errores de conteo en la nube
    tabla_prod = df_selection['TipoProducto'].value_counts().reset_index()
    tabla_prod.columns = ['Producto', 'Cantidad']
    
    fig_pie = px.pie(tabla_prod, values='Cantidad', names='Producto', hole=0.5,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_pie.update_traces(textinfo='value+percent', hovertemplate="<b>%{label}</b><br>Cant: %{value}")
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.subheader("🏆 Top 10 Marcas")
    # Filtro de marca y conteo manual
    df_m = df_selection[df_selection['Marca'] != 'TRAIDO'].copy()
    tabla_m = df_m['Marca'].value_counts().reset_index()
    tabla_m.columns = ['Marca', 'Ventas']
    tabla_m = tabla_m.head(10).sort_values('Ventas', ascending=True)
    
    fig_bar = px.bar(tabla_m, x='Ventas', y='Marca', orientation='h', text='Ventas',
                     color='Ventas', color_continuous_scale='Blues')
    fig_bar.update_traces(hovertemplate="<b>%{y}</b><br>Ventas: %{x}<extra></extra>")
    st.plotly_chart(fig_bar, use_container_width=True)

# --- BLOQUE DE TENDENCIA (SOLUCIÓN DEFINITIVA) ---
st.subheader("📈 Tendencia Diaria de Ventas")

if not df_selection.empty:
    # Agrupamos por fecha (normalizada a día) y contamos
    df_trend = df_selection.copy()
    df_trend['fecha'] = df_trend['fec_registro'].dt.normalize()
    tabla_trend = df_trend.groupby('fecha').size().reset_index(name='Ventas')
    
    # ORDENAMIENTO CRITICO: Sin esto la línea sale recta o cruzada
    tabla_trend = tabla_trend.sort_values('fecha')
    
    fig_line = px.area(tabla_trend, x='fecha', y='Ventas', 
                       markers=True, line_shape='spline',
                       color_discrete_sequence=['#00CC96'])
    
    # Ajuste de ejes para que Plotly entienda que es una línea de tiempo
    fig_line.update_xaxes(type='date', tickformat="%d %b")
    fig_line.update_layout(hovermode="x unified")
    st.plotly_chart(fig_line, use_container_width=True)
else:
    st.info("No hay datos para mostrar la tendencia.")

# --- TABLAS DE DETALLE ---
st.markdown("---")
t1, t2 = st.columns([0.6, 0.4])
with t1:
    st.write("**Resumen Vendedores**")
    st.dataframe(pd.crosstab(df_selection['vendedor'], df_selection['TipoProducto']).style.background_gradient(cmap='Blues', axis=None))
with t2:
    st.write("**Resumen PDV**")
    st.dataframe(pd.crosstab(df_selection['centro_costo'], df_selection['TipoProducto']).style.background_gradient(cmap='Greens', axis=None))
