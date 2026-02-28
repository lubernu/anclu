import streamlit as st
import pandas as pd
import numpy as np

# Configuración básica
st.set_page_config(page_title="Paso 2: Filtros - Anclu", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("ventas_anclu.csv", low_memory=False)
    # Conversión de fecha
    df['fec_registro'] = pd.to_datetime(df['fec_registro'], errors='coerce')
    df = df.dropna(subset=['fec_registro'])
    
    # --- NUEVO EN PASO 2: Extracción de periodos ---
    df['Año'] = df['fec_registro'].dt.year
    df['Mes_Num'] = df['fec_registro'].dt.month
    
    meses_es = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 
        7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    df['Mes'] = df['Mes_Num'].map(meses_es)
    
    # Limpieza básica (mantenemos lo del paso 1)
    df['Marca'] = df['Marca'].fillna('SIN MARCA').astype(str).str.upper().str.strip()
    df['TipoProducto'] = df['TipoProducto'].fillna('OTROS').astype(str).str.strip()
    return df

df = load_data()

# --- NUEVO EN PASO 2: Sidebar con Filtros ---
st.sidebar.title("🎛️ Panel de Control")

# 1. Filtro de Año
anios_disponibles = sorted(df['Año'].unique(), reverse=True)
selected_year = st.sidebar.selectbox("Selecciona el Año", options=anios_disponibles)

# 2. Filtro de Mes (Solo muestra meses que existen en ese año)
df_year = df[df['Año'] == selected_year]
meses_disponibles = df_year.sort_values('Mes_Num')['Mes'].unique()
selected_month = st.sidebar.selectbox("Selecciona el Mes", options=meses_disponibles)

# --- APLICACIÓN DEL FILTRO ---
df_selection = df[(df['Año'] == selected_year) & (df['Mes'] == selected_month)].copy()

# --- PANEL PRINCIPAL ---
st.title(f"📊 Análisis de {selected_month} {selected_year}")

# Verificación de que el filtro funciona
st.write(f"Has seleccionado el periodo: **{selected_month} de {selected_year}**")
st.write(f"Cantidad de registros encontrados para este periodo: `{len(df_selection)}`")

# Mostramos una pequeña muestra de los datos filtrados
st.write("### Muestra de datos filtrados:")
st.dataframe(df_selection[['fec_registro', 'centro_costo', 'vendedor', 'TipoProducto', 'Marca']].head(10))

# Verificamos si hay datos de más de un día para el siguiente paso
dias_con_datos = df_selection['fec_registro'].dt.date.nunique()
st.info(f"Este mes tiene datos en `{dias_con_datos}` días diferentes.")
