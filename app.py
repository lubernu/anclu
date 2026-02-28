import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. Configuración de página
st.set_page_config(page_title="Paso 3: Consolidación - Anclu", layout="wide")

@st.cache_data
def load_data():
    # Cargamos forzando que no intente adivinar tipos (low_memory=False)
    df = pd.read_csv("ventas_anclu.csv", low_memory=False)
    df['fec_registro'] = pd.to_datetime(df['fec_registro'], errors='coerce')
    df = df.dropna(subset=['fec_registro'])
    
    df['Año'] = df['fec_registro'].dt.year
    df['Mes_Num'] = df['fec_registro'].dt.month
    
    meses_es = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 
                7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}
    df['Mes'] = df['Mes_Num'].map(meses_es)
    
    # Limpieza absoluta de Marca y Producto
    df['Marca'] = df['Marca'].fillna('SIN MARCA').astype(str).str.upper().str.strip()
    df['TipoProducto'] = df['TipoProducto'].fillna('OTROS').astype(str).str.strip()
    
    return df

df = load_data()

# --- FILTROS SIDEBAR ---
st.sidebar.title("🎛️ Filtros")
selected_year = st.sidebar.selectbox("Año", options=sorted(df['Año'].unique(), reverse=True))
df_year = df[df['Año'] == selected_year]
selected_month = st.sidebar.selectbox("Mes", options=df_year.sort_values('Mes_Num')['Mes'].unique())

# Filtro del DataFrame
df_selection = df[(df['Año'] == selected_year) & (df['Mes'] == selected_month)].copy()

st.title(f"📊 Dashboard: {selected_month} {selected_year}")
st.write(f"Registros en este periodo: **{len(df_selection)}**")

# --- PASO 3: GRÁFICOS CON CONTEO MANUAL ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📌 Participación")
    # CONTEO MANUAL: Creamos una tabla de frecuencias
    # value_counts() devuelve los números reales de cada categoría
    tabla_participacion = df_selection['TipoProducto'].value_counts().reset_index()
    tabla_participacion.columns = ['Producto', 'Cantidad']
    
    # Graficamos usando la tabla que YA tiene los números sumados
    fig_pie = px.pie(tabla_participacion, 
                     values='Cantidad', 
                     names='Producto', 
                     hole=0.5,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
    
    # Forzamos a que muestre el valor numérico (la cantidad real)
    fig_pie.update_traces(textinfo='value+percent', textfont_size=15)
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.subheader("🏆 Top 10 Marcas")
    # Filtramos TRAIDO antes de contar
    df_marcas_reales = df_selection[df_selection['Marca'] != 'TRAIDO'].copy()
    
    # CONTEO MANUAL
    tabla_marcas = df_marcas_reales['Marca'].value_counts().reset_index()
    tabla_marcas.columns = ['Marca', 'Ventas']
    tabla_marcas = tabla_marcas.head(10).sort_values('Ventas', ascending=True)
    
    # Graficamos usando la columna 'Ventas' que nosotros calculamos
    fig_bar = px.bar(tabla_marcas, 
                     x='Ventas', 
                     y='Marca', 
                     orientation='h',
                     text='Ventas',
                     color='Ventas',
                     color_continuous_scale='Blues')
    
    fig_bar.update_layout(yaxis_title=None, xaxis_title="Unidades Vendidas")
    st.plotly_chart(fig_bar, use_container_width=True)

# TABLA DE VERIFICACIÓN (Solo para ver si los números coinciden)
with st.expander("Ver tabla de frecuencias (Debug)"):
    st.write("Datos que está recibiendo el gráfico de Marcas:")
    st.table(tabla_marcas.sort_values('Ventas', ascending=False))
