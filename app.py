import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px  # <-- Nueva librería para gráficos

# Configuración básica
st.set_page_config(page_title="Paso 3: Gráficos - Anclu", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("ventas_anclu.csv", low_memory=False)
    df['fec_registro'] = pd.to_datetime(df['fec_registro'], errors='coerce')
    df = df.dropna(subset=['fec_registro'])
    df['Año'] = df['fec_registro'].dt.year
    df['Mes_Num'] = df['fec_registro'].dt.month
    meses_es = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 
                7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}
    df['Mes'] = df['Mes_Num'].map(meses_es)
    df['Marca'] = df['Marca'].fillna('SIN MARCA').astype(str).str.upper().str.strip()
    return df

df = load_data()

# --- SIDEBAR (Filtros del Paso 2) ---
st.sidebar.title("🎛️ Filtros")
selected_year = st.sidebar.selectbox("Año", options=sorted(df['Año'].unique(), reverse=True))
df_year = df[df['Año'] == selected_year]
selected_month = st.sidebar.selectbox("Mes", options=df_year.sort_values('Mes_Num')['Mes'].unique())

# Filtro aplicado
df_selection = df[(df['Año'] == selected_year) & (df['Mes'] == selected_month)].copy()

# --- PANEL PRINCIPAL ---
st.title(f"📊 Dashboard: {selected_month} {selected_year}")

# --- NUEVO EN PASO 3: Layout de 2 Columnas para Gráficos ---
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("📌 Participación por Producto")
    # Agrupamos manualmente para asegurar que los números sean exactos
    counts_prod = df_selection.groupby('TipoProducto').size().reset_index(name='Ventas')
    
    if not counts_prod.empty:
        fig_pie = px.pie(counts_prod, 
                         values='Ventas', 
                         names='TipoProducto', 
                         hole=0.5,
                         color_discrete_sequence=px.colors.qualitative.Safe)
        # Mostramos valor real y porcentaje
        fig_pie.update_traces(textinfo='value+percent')
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.write("No hay datos para este mes.")

with col2:
    st.subheader("🏆 Top 10 Marcas")
    # Filtramos para quitar 'TRAIDO' y que no ensucie el ranking
    df_marcas = df_selection[df_selection['Marca'] != 'TRAIDO'].copy()
    
    # Agrupamos, contamos y ordenamos
    counts_brand = df_marcas.groupby('Marca').size().reset_index(name='Unidades')
    counts_brand = counts_brand.sort_values('Unidades', ascending=True).tail(10)
    
    if not counts_brand.empty:
        fig_bar = px.bar(counts_brand, 
                         x='Unidades', 
                         y='Marca', 
                         orientation='h',
                         text='Unidades', # Muestra el número sobre la barra
                         color='Unidades',
                         color_continuous_scale='Blues')
        
        fig_bar.update_layout(yaxis_title=None, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.write("No hay marcas para mostrar (sin contar 'Traido').")
