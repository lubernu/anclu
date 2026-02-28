import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ... (Mantenemos la carga de datos y filtros igual que en el mensaje anterior) ...

# --- GRÁFICOS CON ETIQUETAS CORREGIDAS ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📌 Participación")
    tabla_participacion = df_selection['TipoProducto'].value_counts().reset_index()
    tabla_participacion.columns = ['Producto', 'Cantidad']
    
    fig_pie = px.pie(tabla_participacion, 
                     values='Cantidad', 
                     names='Producto', 
                     hole=0.5,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
    
    # CORRECCIÓN DE ETIQUETA: Muestra Producto y Cantidad de forma limpia
    fig_pie.update_traces(
        textinfo='value+percent', 
        hoverinfo='label+value',
        hovertemplate="<b>%{label}</b><br>Cantidad: %{value}<br>Porcentaje: %{percent}"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.subheader("🏆 Top 10 Marcas")
    df_marcas_reales = df_selection[df_selection['Marca'] != 'TRAIDO'].copy()
    
    tabla_marcas = df_marcas_reales['Marca'].value_counts().reset_index()
    tabla_marcas.columns = ['Marca', 'Ventas']
    tabla_marcas = tabla_marcas.head(10).sort_values('Ventas', ascending=True)
    
    fig_bar = px.bar(tabla_marcas, 
                     x='Ventas', 
                     y='Marca', 
                     orientation='h',
                     text='Ventas',
                     color='Ventas',
                     color_continuous_scale='Blues')
    
    # CORRECCIÓN DE ETIQUETA: Limpia el cuadro flotante (hovertemplate)
    fig_bar.update_traces(
        hovertemplate="<b>Marca: %{y}</b><br>Ventas: %{x}<extra></extra>"
    )
    
    fig_bar.update_layout(
        yaxis_title=None, 
        xaxis_title="Unidades Vendidas",
        hovermode="closest"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# --- PASO 4: TENDENCIA DIARIA (A PRUEBA DE ERRORES) ---
st.subheader("📈 Tendencia Diaria de Ventas")

# Agrupamos por fecha limpia
df_trend = df_selection.copy()
df_trend['fecha'] = df_trend['fec_registro'].dt.date
tabla_trend = df_trend.groupby('fecha').size().reset_index(name='Ventas')
tabla_trend = tabla_trend.sort_values('fecha') # Vital para la línea

fig_line = px.line(tabla_trend, x='fecha', y='Ventas', 
                   markers=True, line_shape='spline',
                   color_discrete_sequence=['#00CC96'])

# Configuramos la tendencia para que no salgan cuadros raros
fig_line.update_traces(hovertemplate="<b>Fecha: %{x}</b><br>Ventas: %{y}<extra></extra>")
fig_line.update_layout(hovermode="x unified", xaxis_title=None)

st.plotly_chart(fig_line, use_container_width=True)
