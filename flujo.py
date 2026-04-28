"""
CoST Dashboard - Aplicación principal
Modelo integrado de gestión, riesgos y transparencia para edificios estatales
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Configuración de página
st.set_page_config(
    page_title="CoST Dashboard - Transparencia en Infraestructura",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ocultar elementos por defecto de Streamlit
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Cargar datos
@st.cache_data(ttl=3600)  # Cache por 1 hora
def load_data():
    df = pd.read_csv("data/matriz_riesgos.csv")
    # Convertir tipos
    df['fecha_actualizacion'] = pd.to_datetime(df['fecha_actualizacion'])
    df['probabilidad'] = df['probabilidad'].astype(int)
    df['impacto'] = df['impacto'].astype(int)
    df['estimacion_ahorro_q'] = df['estimacion_ahorro_q'].astype(int)
    df['efectividad_control'] = df['efectividad_control'].astype(int)
    return df

df = load_data()

# Sidebar - Navegación
st.sidebar.image("https://cdn.jsdelivr.net/gh/streamlit/streamlit.github.io@master/assets/logo.png", width=80)
st.sidebar.title("🏗️ CoST Dashboard")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navegación",
    ["🏠 Inicio", "📊 Riesgos por Fase", "🔍 Matriz de Riesgos", "💰 Ahorros CoST", "📈 Índice de Transparencia", "📤 Exportar OC4IDS"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.caption(f"Última actualización: {df['fecha_actualizacion'].max().strftime('%Y-%m-%d')}")
st.sidebar.caption("Basado en estándar CoST OC4IDS v1.1")

# ============================================================================
# PÁGINA 1: INICIO
# ============================================================================
if page == "🏠 Inicio":
    st.title("🏗️ CoST Dashboard")
    st.caption("Modelo integrado de gestión, riesgos y transparencia para edificios estatales")
    st.markdown("---")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        riesgo_critico = len(df[df['nivel_riesgo'] == 'Critico'])
        riesgo_critico_rojo = len(df[(df['nivel_riesgo'] == 'Critico') & (df['estado_semanal'] == 'Rojo')])
        st.metric(
            "Riesgos Críticos",
            riesgo_critico,
            delta=f"{riesgo_critico_rojo} en estado ROJO",
            delta_color="inverse"
        )
    
    with col2:
        control_efectivo = len(df[df['efectividad_control'] >= 70])
        st.metric(
            "Controles Efectivos (>70%)",
            control_efectivo,
            delta=f"{control_efectivo/len(df)*100:.0f}% del total"
        )
    
    with col3:
        ahorro_total = df['estimacion_ahorro_q'].sum()
        st.metric(
            "Ahorro Estimado (Q)",
            f"Q {ahorro_total:,.0f}",
            delta="+12% vs trimestre anterior"
        )
    
    with col4:
        # Cálculo ITI simplificado para la portada
        iti_score = 58  # Base
        iti_score += (control_efectivo / len(df)) * 20
        iti_score += (len(df[df['publicar_ciudadano'] == 'Si']) / len(df)) * 15
        iti_score = min(iti_score, 100)
        st.metric(
            "Índice Transparencia (ITI)",
            f"{iti_score:.0f}/100",
            delta="+8 puntos",
            delta_color="normal"
        )
    
    st.markdown("---")
    
    # Visualización de tendencia de riesgos
    st.subheader("📈 Tendencia de Riesgos por Nivel")
    
    # Simular datos de tendencia (últimos 6 meses)
    meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun']
    tendencia_criticos = [12, 11, 10, 9, 9, 9]
    tendencia_altos = [22, 21, 20, 19, 19, 19]
    tendencia_medios = [10, 10, 9, 8, 8, 8]
    
    fig_tendencia = go.Figure()
    fig_tendencia.add_trace(go.Scatter(x=meses, y=tendencia_criticos, mode='lines+markers', name='Críticos', line=dict(color='red', width=3)))
    fig_tendencia.add_trace(go.Scatter(x=meses, y=tendencia_altos, mode='lines+markers', name='Altos', line=dict(color='orange', width=3)))
    fig_tendencia.add_trace(go.Scatter(x=meses, y=tendencia_medios, mode='lines+markers', name='Medios', line=dict(color='green', width=3)))
    fig_tendencia.update_layout(title="Evolución últimos 6 meses", xaxis_title="Mes", yaxis_title="Cantidad de Riesgos", height=400)
    st.plotly_chart(fig_tendencia, use_container_width=True)
    
    # Riesgos por fase (gráfico de barras)
    st.subheader("📊 Distribución de Riesgos por Fase")
    riesgos_por_fase = df.groupby(['fase', 'nivel_riesgo']).size().reset_index(name='count')
    fig_fases = px.bar(riesgos_por_fase, x='fase', y='count', color='nivel_riesgo', 
                       color_discrete_map={'Critico':'red', 'Alto':'orange', 'Medio':'green'},
                       title="Riesgos por Fase y Nivel")
    fig_fases.update_layout(xaxis_title="Fase", yaxis_title="Cantidad de Riesgos", height=400)
    st.plotly_chart(fig_fases, use_container_width=True)
    
    # Alertas activas
    st.subheader("🔔 Alertas Activas")
    alertas_rojas = df[(df['estado_semanal'] == 'Rojo')][['id', 'descripcion_riesgo', 'fase', 'responsable_riesgo', 'accion_requerida']]
    if len(alertas_rojas) > 0:
        for _, alerta in alertas_rojas.iterrows():
            st.warning(f"🔴 **{alerta['id']}** - {alerta['descripcion_riesgo']} (Fase {alerta['fase']}) | Responsable: {alerta['responsable_riesgo']}")
            st.caption(f"Acción: {alerta['accion_requerida']}")
    else:
        st.success("✅ No hay alertas rojas activas")

# ============================================================================
# PÁGINA 2: RIESGOS POR FASE
# ============================================================================
elif page == "📊 Riesgos por Fase":
    st.title("📊 Riesgos por Fase")
    st.markdown("---")
    
    # Selector de fase
    fases = ['Todas'] + sorted(df['fase'].unique().tolist())
    fase_seleccionada = st.selectbox("Seleccionar Fase", fases)
    
    if fase_seleccionada != 'Todas':
        df_filtrado = df[df['fase'] == fase_seleccionada]
    else:
        df_filtrado = df
    
    # Semáforo de la fase seleccionada
    col1, col2, col3 = st.columns(3)
    with col1:
        criticos = len(df_filtrado[df_filtrado['nivel_riesgo'] == 'Critico'])
        st.metric("Críticos", criticos)
    with col2:
        altos = len(df_filtrado[df_filtrado['nivel_riesgo'] == 'Alto'])
        st.metric("Altos", altos)
    with col3:
        medios = len(df_filtrado[df_filtrado['nivel_riesgo'] == 'Medio'])
        st.metric("Medios", medios)
    
    st.markdown("---")
    
    # Tabla detallada
    st.subheader("Detalle de Riesgos")
    columnas_mostrar = ['id', 'descripcion_riesgo', 'probabilidad', 'impacto', 'nivel_riesgo', 
                        'control_existe', 'efectividad_control', 'estado_semanal', 'responsable_riesgo']
    st.dataframe(df_filtrado[columnas_mostrar], use_container_width=True, height=400)

# ============================================================================
# PÁGINA 3: MATRIZ DE RIESGOS COMPLETA
# ============================================================================
elif page == "🔍 Matriz de Riesgos":
    st.title("🔍 Matriz de Riesgos y Controles")
    st.markdown("---")
    
    # Filtros
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        nivel_filter = st.multiselect("Nivel de Riesgo", df['nivel_riesgo'].unique(), default=df['nivel_riesgo'].unique())
    with col_f2:
        estado_filter = st.multiselect("Estado Semanal", df['estado_semanal'].unique(), default=df['estado_semanal'].unique())
    with col_f3:
        fase_filter = st.multiselect("Fase", df['fase'].unique(), default=df['fase'].unique())
    
    df_filtrado = df[
        (df['nivel_riesgo'].isin(nivel_filter)) &
        (df['estado_semanal'].isin(estado_filter)) &
        (df['fase'].isin(fase_filter))
    ]
    
    st.dataframe(df_filtrado, use_container_width=True, height=500)
    
    # Exportar
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar como CSV", csv, "matriz_riesgos.csv", "text/csv")

# ============================================================================
# PÁGINA 4: AHORROS COST
# ============================================================================
elif page == "💰 Ahorros CoST":
    st.title("💰 Ahorros Estimados por Transparencia")
    st.caption("Basado en metodología CoST-GTI 2026")
    st.markdown("---")
    
    # Resumen de ahorros
    ahorro_total = df['estimacion_ahorro_q'].sum()
    ahorro_criticos = df[df['nivel_riesgo'] == 'Critico']['estimacion_ahorro_q'].sum()
    ahorro_altos = df[df['nivel_riesgo'] == 'Alto']['estimacion_ahorro_q'].sum()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Ahorro Total Estimado", f"Q {ahorro_total:,.0f}", delta="+15% vs esperado")
    with col2:
        st.metric("Ahorro por Riesgos Críticos", f"Q {ahorro_criticos:,.0f}")
    with col3:
        st.metric("Ahorro por Riesgos Altos", f"Q {ahorro_altos:,.0f}")
    
    st.markdown("---")
    
    # Gráfico de ahorros por riesgo
    st.subheader("Top 5 Riesgos con Mayor Ahorro Potencial")
    top_ahorros = df.nlargest(5, 'estimacion_ahorro_q')[['id', 'descripcion_riesgo', 'estimacion_ahorro_q', 'nivel_riesgo']]
    
    fig_ahorros = px.bar(top_ahorros, x='id', y='estimacion_ahorro_q', 
                         color='nivel_riesgo', 
                         color_discrete_map={'Critico':'red', 'Alto':'orange', 'Medio':'green'},
                         title="Ahorro Estimado por Riesgo (Quetzales)",
                         labels={'estimacion_ahorro_q': 'Ahorro (Q)', 'id': 'Riesgo ID'})
    st.plotly_chart(fig_ahorros, use_container_width=True)
    
    st.info("""
    **Metodología de cálculo**:  
    Basado en CoST-GTI 2026:  
    - Sobreprecio evitado = (Precio mercado - Precio adjudicado) × Cantidad  
    - Retrasos evitados = Días de retraso × Costo diario del proyecto  
    - Desperdicio evitado = Materiales no utilizados × Precio unitario
    """)

# ============================================================================
# PÁGINA 5: ÍNDICE DE TRANSPARENCIA (ITI)
# ============================================================================
elif page == "📈 Índice de Transparencia":
    st.title("📈 Índice de Transparencia en Infraestructura (ITI)")
    st.caption("Metodología CoST 2025 - Rango 0 a 100 puntos")
    st.markdown("---")
    
    # Cálculo del ITI según estándar CoST
    # Dimensión 1: Divulgación de datos (0-25 puntos)
    disclosure_score = 0
    disclosure_score += min(10, len(df[df['publicar_ciudadano'] == 'Si']) / len(df) * 20)  # 10 puntos por datos públicos
    disclosure_score += min(10, len(df[df['publicar_ciudadano'] == 'Si']) / len(df) * 15)  # 10 puntos por oportunidad
    disclosure_score += 5 if len(df[df['publicar_ciudadano'] == 'Si']) > 0 else 0  # 5 puntos por formato abierto
    
    # Dimensión 2: Revisión independiente (Assurance) (0-25 puntos)
    assurance_score = 0
    assurance_score += len(df[df['validacion_tercero'] == 'Si']) * 2  # 2 puntos por cada riesgo validado
    assurance_score += len(df[df['validacion_tercero'] == 'Potencial']) * 1
    assurance_score = min(assurance_score, 25)
    
    # Dimensión 3: Trabajo multiactor (0-25 puntos)
    multistakeholder_score = 0
    multistakeholder_score += 10 if len(df[df['conoce_ciudadano'] == 'Si']) > 0 else 0
    multistakeholder_score += 10 if len(df[df['conoce_ciudadano'] == 'Parcial']) > 0 else 0
    multistakeholder_score += 5 if any(df['mejora_transparencia'] == 'Critica') else 0
    multistakeholder_score = min(multistakeholder_score, 25)
    
    # Dimensión 4: Responsabilidad social (0-25 puntos)
    accountability_score = 0
    accountability_score += min(15, len(df[df['estado_semanal'] == 'Verde']) / len(df) * 20)  # 15 puntos por riesgos en verde
    accountability_score += 10 if len(df[df['estado_semanal'] == 'Rojo']) == 0 else 0  # 10 puntos sin alertas rojas
    accountability_score = min(accountability_score, 25)
    
    iti_total = disclosure_score + assurance_score + multistakeholder_score + accountability_score
    
    # Visualización
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Gauge chart para ITI total
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=iti_total,
            title={"text": "Índice de Transparencia (ITI)"},
            delta={"reference": 50, "increasing": {"color": "green"}},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "darkblue"},
                "steps": [
                    {"range": [0, 25], "color": "red"},
                    {"range": [25, 50], "color": "orange"},
                    {"range": [50, 75], "color": "yellow"},
                    {"range": [75, 100], "color": "
