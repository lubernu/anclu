import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 1. Configuración de página
st.set_page_config(page_title="Ventas Anclu | Dashboard Profesional", layout="wide")

@st.cache_data
def load_data():
    # Cargamos con low_memory=False para evitar errores de tipo de dato en la nube
    df = pd.read_csv("ventas_anclu.csv", low_memory=False)
    
    # Limpieza de fechas: forzamos formato datetime
    df['fec_registro'] = pd.to_datetime(df['fec_registro'], errors='coerce')
    df = df.dropna(subset=['fec_registro']) # Quitamos filas sin fecha
    
    # Extraemos tiempo
    df['Año'] = df['fec_registro'].dt.year
    df['Mes_Num'] = df['fec_registro'].dt.month
    
    meses_es = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 
        7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    df['Mes'] = df['Mes_Num'].map(meses_es)
    
    # Limpieza profunda de Marca (Quitar nulos, espacios y pasar a Mayúsculas)
    df['Marca'] = df['Marca'].fillna('SIN MARCA').astype(str).str.strip().str.upper()
    
    # Clasificación de Producto
    condicion = df['TipoProducto'].isin(['Kit Contado', 'Reposición', 'Kit Cuotas'])
    df['Producto'] = np.where(condicion, 'Equipos', 'Postpagos')
    
    return df

df = load_data()

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.title("🎛️ Filtros de Control")
with st.sidebar:
    anios = sorted(df['Año'].unique(), reverse=True)
    selected_year = st.selectbox("Año Fiscal", options=anios)
    
    df_year = df[df['Año'] == selected_year]
    meses = df_year.sort_values('Mes_Num')['Mes'].unique()
    selected_month = st.selectbox("Selecciona Mes", options=meses)
    
    centros = sorted(df['centro_costo'].unique())
    selected_centro = st.multiselect("Centros de Costo", options=centros, default=centros)

# --- APLICAR FILTROS ---
df_selection = df[
    (df['Año'] == selected_year) & 
    (df['Mes'] == selected_month) & 
    (df['centro_costo'].isin(selected_centro))
].copy()

# --- CABECERA ---
st.title("🚀 Dashboard de Gestión de Ventas")
st.markdown(f"🗓️ **Viendo datos de:** {selected_month} {selected_year}")

# KPIs
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Ventas", f"{len(df_selection):,}")
m2.metric("Postpagos", f"{len(df_selection[df_selection['Producto']=='Postpagos']):,}")
m3.metric("Equipos", f"{len(df_selection[df_selection['Producto']=='Equipos']):,}")
m4.metric("Vendedores Activos", len(df_selection['vendedor'].unique()))

st.markdown("---")

# --- GRÁFICOS: PARTICIPACIÓN Y TOP MARCAS ---
col_pie, col_bar = st.columns([1, 1.2])

with col_pie:
    st.subheader("📊 Participación por Tipo")
    # Agrupamos para asegurar que Plotly vea los totales
    resumen_prod = df_selection.groupby('TipoProducto').size().reset_index(name='Unidades')
    fig_pie = px.pie(resumen_prod, values='Unidades', names='TipoProducto', 
                     hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_pie.update_traces(textinfo='value+percent')
    st.plotly_chart(fig_pie, use_container_width=True)

with col_bar:
    st.subheader("🏆 Top 10 Marcas (Sin 'TRAIDO')")
    # Filtro estricto para excluir 'TRAIDO'
    df_marcas = df_selection[df_selection['Marca'] != 'TRAIDO'].copy()
    
    # Agrupamos y contamos unidades
    resumen_marcas = df_marcas.groupby('Marca').size().reset_index(name='Ventas')
    resumen_marcas = resumen_marcas.sort_values('Ventas', ascending=True).tail(10) # Las 10 más altas
    
    fig_marcas = px.bar(resumen_marcas, x='Ventas', y='Marca', orientation='h',
                        text='Ventas', color='Ventas', color_continuous_scale='Blues')
    fig_marcas.update_layout(showlegend=False, yaxis_title=None, xaxis_title="Unidades")
    st.plotly_chart(fig_marcas, use_container_width=True)

# --- GRÁFICO DE TENDENCIA DIARIA ---
st.subheader("📈 Tendencia Diaria de Ventas")

if not df_selection.empty:
    # 1. Normalizamos la fecha a solo DIA para agrupar correctamente
    df_trend = df_selection.copy()
    df_trend['fecha_dia'] = df_trend['fec_registro'].dt.date
    
    # 2. Agrupamos y contamos
    df_trend = df_trend.groupby('fecha_dia').size().reset_index(name='Ventas')
    
    # 3. ORDENAR POR FECHA (Vital para que la línea no sea recta o cruzada)
    df_trend = df_trend.sort_values('fecha_dia')
    
    # 4. Crear gráfico
    fig_trend = px.area(df_trend, x='fecha_dia', y='Ventas', 
                        line_shape='spline', markers=True,
                        color_discrete_sequence=['#00CC96'])
    
    # 5. Forzamos al eje X a ser temporal para que no salte días
    fig_trend.update_xaxes(type='date', tickformat="%d %b")
    st.plotly_chart(fig_trend, use_container_width=True)
else:
    st.warning("No hay datos para la selección actual.")

# --- TABLAS DE DETALLE ---
st.markdown("---")
st.subheader("📋 Resumen por Asesor y Punto de Venta")
c_v, c_p = st.columns([0.6, 0.4])

with c_v:
    st.markdown("**Ventas por Vendedor**")
    tabla_v = pd.crosstab(df_selection['vendedor'], df_selection['TipoProducto'])
    st.dataframe(tabla_v.style.background_gradient(cmap='Blues', axis=None), use_container_width=True)

with c_p:
    st.markdown("**Ventas por Centro de Costo**")
    tabla_p = pd.crosstab(df_selection['centro_costo'], df_selection['TipoProducto'])
    st.dataframe(tabla_p.style.background_gradient(cmap='Greens', axis=None), use_container_width=True)
