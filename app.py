import streamlit as st
import pandas as pd
import numpy as np

# Configuración básica
st.set_page_config(page_title="Prueba de Carga - Anclu", layout="wide")

@st.cache_data
def load_data():
    # 1. Cargamos el archivo ignorando errores de memoria y tipos mezclados
    df = pd.read_csv("ventas_anclu.csv", low_memory=False)
    
    # 2. Convertimos la fecha. Si algo falla, lo convierte en 'NaT' (Not a Time)
    df['fec_registro'] = pd.to_datetime(df['fec_registro'], errors='coerce')
    
    # 3. Limpieza de columnas clave
    df['Marca'] = df['Marca'].fillna('SIN MARCA').astype(str).str.upper().str.strip()
    df['TipoProducto'] = df['TipoProducto'].fillna('OTROS').astype(str).str.strip()
    
    # 4. Clasificación básica
    condicion = df['TipoProducto'].isin(['Kit Contado', 'Reposición', 'Kit Cuotas'])
    df['Producto'] = np.where(condicion, 'Equipos', 'Postpagos')
    
    return df

# Ejecución
st.title("🧪 Paso 1: Verificación de Datos")
df = load_data()

# Mostramos información técnica para confirmar que todo está bien
st.write("### Resumen de la carga:")
col1, col2 = st.columns(2)
with col1:
    st.write(f"**Total de filas:** {len(df)}")
    st.write(f"**Columnas detectadas:** {list(df.columns)}")
with col2:
    st.write("**Tipos de datos de columnas clave:**")
    st.write(df[['fec_registro', 'Marca', 'TipoProducto']].dtypes)

st.write("### Vista previa de los datos:")
st.dataframe(df.head(10))
