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

# --- KPI CARDS ---
# --- CÁLCULO MES ANTERIOR ---
def get_mes_anterior(year, mes_num):
    if mes_num == 1:
        return year - 1, 12
    return year, mes_num - 1

año_ant, mes_ant_num = get_mes_anterior(selected_year, df[df['Mes'] == selected_month]['Mes_Num'].iloc[0])

df_anterior = df[
    (df['Año'] == año_ant) &
    (df['Mes_Num'] == mes_ant_num) &
    (df['centro_costo'].isin(selected_centro))
].copy()

# Métricas actuales
total_act     = len(df_selection)
post_act      = len(df_selection[df_selection['Producto'] == 'Postpagos'])
equip_act     = len(df_selection[df_selection['Producto'] == 'Equipos'])
asesores_act  = df_selection['vendedor'].nunique()

# Métricas mes anterior
total_ant    = len(df_anterior)
post_ant     = len(df_anterior[df_anterior['Producto'] == 'Postpagos'])
equip_ant    = len(df_anterior[df_anterior['Producto'] == 'Equipos'])
asesores_ant = df_anterior['vendedor'].nunique()

def delta_html(actual, anterior):
    """Genera el HTML del indicador de cambio"""
    if anterior == 0:
        return '<div class="delta neutral">— Sin datos anteriores</div>'
    diff = actual - anterior
    pct  = (diff / anterior) * 100
    if diff > 0:
        return f'<div class="delta positivo">▲ +{diff:,} &nbsp;(+{pct:.1f}% vs mes ant.)</div>'
    elif diff < 0:
        return f'<div class="delta negativo">▼ {diff:,} &nbsp;({pct:.1f}% vs mes ant.)</div>'
    else:
        return '<div class="delta neutral">= Sin cambio vs mes ant.</div>'

# --- ESTILOS ---
st.markdown("""
<style>
.card-container {
    display: flex;
    gap: 16px;
    margin-bottom: 20px;
}
.card {
    background: linear-gradient(135deg, #1e3a5f, #2d6a9f);
    border-radius: 16px;
    padding: 20px 24px;
    flex: 1;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    border-left: 5px solid #00CC96;
    color: white;
}
.card .label {
    font-size: 12px;
    color: #a8d0f0;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.card .value {
    font-size: 36px;
    font-weight: 800;
    color: #ffffff;
    line-height: 1;
    margin-bottom: 10px;
}
.card .icon {
    font-size: 22px;
    margin-bottom: 6px;
}
.delta {
    font-size: 12px;
    font-weight: 600;
    padding: 4px 8px;
    border-radius: 20px;
    display: inline-block;
}
.delta.positivo {
    background-color: rgba(0, 204, 150, 0.2);
    color: #00CC96;
}
.delta.negativo {
    background-color: rgba(239, 85, 59, 0.2);
    color: #EF553B;
}
.delta.neutral {
    background-color: rgba(168, 208, 240, 0.15);
    color: #a8d0f0;
}
.card.total    { border-left-color: #00CC96; }
.card.post     { border-left-color: #636EFA; }
.card.equip    { border-left-color: #EF553B; }
.card.asesores { border-left-color: #FECB52; }
</style>
""", unsafe_allow_html=True)

# --- TARJETAS ---
st.markdown(f"""
<div class="card-container">
    <div class="card total">
        <div class="icon">🛒</div>
        <div class="label">Ventas Totales</div>
        <div class="value">{total_act:,}</div>
        {delta_html(total_act, total_ant)}
    </div>
    <div class="card post">
        <div class="icon">📱</div>
        <div class="label">Postpagos</div>
        <div class="value">{post_act:,}</div>
        {delta_html(post_act, post_ant)}
    </div>
    <div class="card equip">
        <div class="icon">📦</div>
        <div class="label">Equipos</div>
        <div class="value">{equip_act:,}</div>
        {delta_html(equip_act, equip_ant)}
    </div>
    <div class="card asesores">
        <div class="icon">👥</div>
        <div class="label">Asesores</div>
        <div class="value">{asesores_act:,}</div>
        {delta_html(asesores_act, asesores_ant)}
    </div>
</div>
""", unsafe_allow_html=True)

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
st.markdown("---")
st.subheader(f"🔡Archivo Detallado")
st.dataframe(df_selection)





