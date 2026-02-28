import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. Configuración de página
st.set_page_config(page_title="Dashboard Ventas Anclu", layout="wide")

@st.cache_data
def load_data():
    # Carga con parámetros de seguridad para evitar errores de tipo de dato
    df = pd.read_csv("ventas_anclu.csv", low_memory=False)
    
    # Limpieza estricta de fechas
    df['fec_registro'] = pd.to_datetime(df['fec_registro'], errors='coerce')
    df = df.dropna(subset=['fec_registro'])
    
    # Columnas de tiempo
    df['Año'] = df['fec_registro'].dt.year
    df['Mes_Num'] = df['fec_registro'].dt.month
    meses_dict = {1:"Enero", 2:"Febrero", 3:"Marzo", 4:"Abril", 5:"Mayo", 6:"Junio",
                  7:"Julio", 8:"Agosto", 9:"Septiembre", 10:"Octubre", 11:"Noviembre", 12:"Diciembre"}
    df['Mes'] = df['Mes_Num'].map(meses_dict)
    
    # Limpieza de textos para evitar duplicados por espacios o mayúsculas
    df['Marca'] = df['Marca'].fillna('SIN MARCA').astype(str).str.upper().str.strip()
    df['TipoProducto'] = df['TipoProducto'].fillna('OTROS').astype(str).str.strip()
    
    # Clasificación lógica
    condicion = df['TipoProducto'].isin(['Kit Contado', 'Reposición', 'Kit Cuotas'])
    df['Producto'] = np.where(condicion, 'Equipos', 'Postpagos')
    
    return df

# Cargar datos
df = load_data()

# --- FILTROS (Sidebar) ---
st.sidebar.title("🎛️ Filtros")
with st.sidebar:
    list_anios = sorted(df['Año'].unique(), reverse=True)
    selected_year = st.selectbox("Selecciona Año", options=list_anios)
    
    df_y = df[df['Año'] == selected_year]
    list_meses = df_y.sort_values('Mes_Num')['Mes'].unique()
    selected_month = st.selectbox("Selecciona Mes", options=list_meses)
    
# --- FILTRADO FINAL ---
df_selection = df[
    (df['Año'] == selected_year) & 
    (df['Mes'] == selected_month)     
].copy()

# --- PANEL DE CONTROL PRINCIPAL ---
st.title(f"🚀 Dashboard de Ventas: {selected_month} {selected_year}")

# Métricas (KPIs)
m1, m2, m3, m4 = st.columns(4)
m1.metric("Ventas Totales", f"{len(df_selection):,}")
m2.metric("Postpagos", f"{len(df_selection[df_selection['Producto']=='Postpagos']):,}")
m3.metric("Equipos", f"{len(df_selection[df_selection['Producto']=='Equipos']):,}")
m4.metric("Asesores", len(df_selection['vendedor'].unique()))

st.markdown("---")

# --- GRÁFICOS: PARTICIPACIÓN Y TOP MARCAS ---
c1, c2 = st.columns(2)

with c1:
    st.subheader("📊 Participación")
    # Agregación manual para asegurar que Plotly no cuente mal
    df_p = df_selection.groupby('TipoProducto', as_index=False).size()
    df_p.columns = ['Tipo', 'Unidades']
    
    fig_p = px.pie(df_p, values='Unidades', names='Tipo', hole=0.5,
                   color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_p.update_traces(textinfo='value+percent', hovertemplate="<b>%{label}</b><br>Cant: %{value}")
    st.plotly_chart(fig_p, use_container_width=True)

with c2:
    st.subheader("🏆 Top 10 Marcas")
    # Filtro de marca y agregación manual
    df_m = df_selection[df_selection['Marca'] != 'TRAIDO'].copy()
    df_m_count = df_m.groupby('Marca', as_index=False).size()
    df_m_count.columns = ['Marca', 'Ventas']
    df_m_count = df_m_count.nlargest(10, 'Ventas').sort_values('Ventas', ascending=True)
    df_m_count = df_m_count.head(10).sort_values('Ventas', ascending=True)
    
    fig_m = px.bar(df_m_count, x='Ventas', y='Marca', orientation='h', text='Ventas',
                   color='Ventas', color_continuous_scale='Blues')
    # Limpieza total del hover
    fig_m.update_traces(hovertemplate="<b>Marca: %{y}</b><br>Ventas: %{x}<extra></extra>")
    st.plotly_chart(fig_m, use_container_width=True)

# --- GRÁFICO DE TENDENCIA (Solución a la línea recta) ---
st.subheader("📈 Tendencia Diaria de Ventas")

df_t = df_selection.copy()
df_t['fecha_corta'] = df_t['fec_registro'].dt.floor('D')  # Más robusto que .dt.date
df_trend = df_t.groupby('fecha_corta', as_index=False).size()
df_trend.columns = ['Fecha', 'Ventas']
df_trend = df_trend.sort_values('Fecha').reset_index(drop=True)

if not df_trend.empty and len(df_trend) > 1:
    fig_t = px.area(df_trend, x='Fecha', y='Ventas',
                    markers=True,
                    line_shape='linear',  # Sin suavizado artificial
                    color_discrete_sequence=['#00CC96'])
    fig_t.update_layout(
        xaxis=dict(type='date', tickformat='%d/%m', dtick=86400000),  # Un tick por día
        hovermode="x unified",
        xaxis_title=None
    )
    fig_t.update_traces(hovertemplate="Fecha: %{x|%d/%m/%Y}<br>Ventas: %{y}<extra></extra>")
    st.plotly_chart(fig_t, use_container_width=True)
else:
    st.info("No hay datos suficientes para graficar la tendencia.")
# --- TABLAS DE RENDIMIENTO ---
st.markdown("---")
col_vend, col_pdv = st.columns([0.6, 0.4])

with col_vend:
    st.write("**Desempeño por Vendedor**")
    tabla_v = pd.crosstab(df_selection['vendedor'], df_selection['TipoProducto'])
    st.dataframe(tabla_v.style.background_gradient(cmap='Blues', axis=None), use_container_width=True)

with col_pdv:
    st.write("**Desempeño por Punto de Venta**")
    tabla_p = pd.crosstab(df_selection['centro_costo'], df_selection['TipoProducto'])
    st.dataframe(tabla_p.style.background_gradient(cmap='Greens', axis=None), use_container_width=True)
# --- TABLA RESUMEN ---
st.subheader(f"Archivo Detallado")
st.dataframe(df_selection)


