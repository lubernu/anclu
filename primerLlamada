import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. Configuración de página
st.set_page_config(page_title="Dashboard Primer Llamada Anclu", layout="wide")

@st.cache_data
def load_data():
    columnas_rp = ['DISTRIBUIDOR','PRODUCTO','PRIM_LLAMADA_ACTIVACION', 'MIN','IMEI']
    columnas_ventas = ['centro_costo','vendedor','fec_registro','telefono','imei','TipoProducto','Marca' ]
    
    # Carga con parámetros de seguridad para evitar errores de tipo de dato
    df_ventas = pd.read_csv("ventas_anclu.csv", low_memory=False,dtype='str',usecols=columnas_ventas)
    df_rp = pd.read_csv("archivo_Prepago_Anclu.txt", sep=';', low_memory=False, usecols= columnas_rp, dtype='str')

    # Limpieza estricta de fechas
    df_ventas['fec_registro'] = pd.to_datetime(df_ventas['fec_registro'], errors='coerce')
    df_ventas = df_ventas.dropna(subset=['fec_registro'])

    # Limpieza de textos para evitar duplicados por espacios o mayúsculas
    df_ventas['Marca'] = df_ventas['Marca'].fillna('SIN MARCA').astype(str).str.upper().str.strip()
    df_ventas['TipoProducto'] = df_ventas['TipoProducto'].fillna('OTROS').astype(str).str.strip()
    
    # Clasificación lógica
    condicion = df_ventas['TipoProducto'].isin(['Kit Contado', 'Reposición', 'Kit Cuotas'])
    df_ventas['Producto'] = np.where(condicion, 'Equipos', 'Postpagos')  

    df_ventas = df_ventas[df_ventas['TipoProducto'] == 'Kit Contado'] 
    df_ventas = df_ventas[df_ventas['fec_registro'] >= '20260101']

    return df_ventas, df_rp

# Cargar datos
df_ventas, df_rp = load_data()


st.title(f"🚀 Primer Llamada")

# cruce de archivos
resultado = df_ventas.merge(
    df_rp[['IMEI', 'MIN','PRIM_LLAMADA_ACTIVACION']],  # Seleccionas solo la columna que necesitas + la clave
    left_on='imei',   # Columna de tabla1
    right_on='IMEI',  # Columna de tabla2
    how='left')

Fact_sin_llamada = resultado[resultado['PRIM_LLAMADA_ACTIVACION'].isna()].reset_index(drop=True)

Fact_Sin_primer_preactivar= Fact_sin_llamada[Fact_sin_llamada['MIN'].isna()].reset_index(drop=True)
Fact_Por_llamar = Fact_sin_llamada[Fact_sin_llamada['MIN'].notna()].reset_index(drop=True)

st.markdown('### Equipos Facturados 2026 Sin Preactivar')
st.dataframe(Fact_Sin_primer_preactivar)

st.markdown('### Equipos Facturados 2026 Sin Primer Llamada')
st.dataframe(Fact_Por_llamar)

st.markdown('### Equipos Facturados 2026 Sin Primer LLamada General')
st.dataframe(Fact_sin_llamada)

