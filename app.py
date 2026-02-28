import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

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

# --- SIDEBAR ---
st.sidebar.title("🎛️ Filtros")
selected_year = st.sidebar.selectbox("Año", options=sorted(df['Año'].unique(), reverse=True))
df_year = df[df['Año'] == selected_year]
selected_month = st.sidebar.selectbox("Mes", options=df_year.sort_values('Mes_Num')['Mes'].unique())

# Filtro aplicado
df_selection = df[(df['Año'] == selected_year) & (df['Mes'] == selected_month)].copy()

# --- PANEL PRINCIPAL ---
st.title(f"📊 Dashboard: {selected_month} {selected_year}")

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("📌 Participación por Producto")
    
    # FORMA REFORZADA: Contamos con Pandas primero
    # Usamos una columna que siempre tenga datos (cc_vendedor) para contar filas
    df_participacion = df_selection.groupby('TipoProducto')['cc_vendedor'].count().reset_index()
    df_participacion.columns = ['TipoProducto', 'Cantidad_Real']
    
    if not df_participacion.empty:
        # Ahora le pasamos a Plotly la columna 'Cantidad_Real'
        fig_pie = px.pie(df_participacion, 
                         values='Cantidad_Real', 
                         names='TipoProducto', 
                         hole=0.5,
                         color_discrete_sequence=px.colors.qualitative.Safe)
        
        # Obligamos a mostrar el valor entero y el porcentaje
        fig_pie.update_traces(textinfo='value+percent', textfont_size=14)
        st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.subheader("🏆 Top 10 Marcas")
    
    # Filtramos 'TRAIDO'
    df_solo_marcas = df_selection[df_selection['Marca'] != 'TRAIDO'].copy()
    
    # FORMA REFORZADA: Contamos con Pandas primero
    df_ranking = df_solo_marcas.groupby('Marca')['cc_vendedor'].count().reset_index()
    df_ranking.columns = ['Marca', 'Unidades_Vendidas']
    df_ranking = df_ranking.sort_values('Unidades_Vendidas', ascending=True).tail(10)
    
    if not df_ranking.empty:
        # Usamos 'Unidades_Vendidas' para el eje X
        fig_bar = px.bar(df_ranking, 
                         x='Unidades_Vendidas', 
                         y='Marca', 
                         orientation='h',
                         text='Unidades_Vendidas',
                         color='Unidades_Vendidas',
                         color_continuous_scale='Blues')
        
        fig_bar.update_layout(yaxis_title=None, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
