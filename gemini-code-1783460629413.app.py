import streamlit as st
import pandas as pd
import altair as alt

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Dashboard Loterías | Inteligencia de Campañas", layout="wide", initial_sidebar_state="expanded")

# --- INYECCIÓN DE CSS (Estilo HTML/Canvas) ---
st.markdown("""
<style>
    /* Estilos globales y tipografía */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    
    /* Ocultar elementos por defecto de Streamlit para un look más limpio */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Estilo de fondo principal */
    .stApp {
        background-color: #f8fafc;
    }

    /* Estilo de las Tarjetas (Cards) de Métricas */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 20px 24px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    /* Etiquetas de Métricas */
    div[data-testid="metric-container"] > div:nth-child(1) {
        color: #64748b;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    
    /* Valores de Métricas */
    div[data-testid="metric-container"] > div:nth-child(2) {
        color: #1e293b;
        font-size: 2rem;
        font-weight: 700;
    }

    /* Títulos de sección */
    h1, h2, h3 {
        color: #0f172a;
        font-weight: 700;
    }
    
    /* Contenedor de Alertas e Insights */
    .insight-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #f59e0b; /* Accent border */
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    .insight-title {
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .insight-text {
        color: #475569;
        font-size: 0.9rem;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)


# --- CABECERA PERSONALIZADA ---
col_logo, col_title = st.columns([1, 10])
with col_title:
    st.markdown("""
        <h1 style='margin-bottom: 0; padding-bottom: 0; color: #1e3a8a;'>Inteligencia de Campañas | Loterías</h1>
        <p style='color: #64748b; margin-top: 0; font-weight: 500;'>Analítica de Actividad, Rendimiento & Insights Ejecutivos</p>
    """, unsafe_allow_html=True)
st.divider()


# --- 1. CARGA DE DATOS ---
with st.sidebar:
    st.markdown("### 📥 Panel de Carga")
    archivo_subido = st.file_uploader("Sube el archivo 'Reporte de campañas Loterias.xlsx'", type=["xlsx"])

if archivo_subido is not None:
    # 2. Leer la data y limpiar
    try:
        df = pd.read_excel(archivo_subido, sheet_name='Reporte_Nuevo')
    except Exception as e:
        st.error(f"Error al leer el archivo. Asegúrate de que tenga una pestaña llamada 'Reporte_Nuevo'. Error técnico: {e}")
        st.stop()
        
    # Renombrado flexible (Prevención de KeyErrors)
    df = df.rename(columns={
        'Total:  Bonos entregados / Usaron Bonos': 'Bonos_Usados',
        'Clientes que jugaron': 'Jugadores',
        'Tasa de Actividad en juego': 'Tasa_Actividad',
        'Fecha de Envío': 'Fecha',
        'Campaña.1': 'Mensaje_Texto',
        'Mensaje': 'Mensaje_Texto'
    })
    
    # Limpieza estricta de datos
    if 'Fecha' in df.columns:
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        
    columnas_numericas = ['Total de envíos', 'Bonos_Usados', 'Tasa de efectividad', 'Jugadores', 'Tasa_Actividad']
    for col in columnas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    if 'Total de envíos' in df.columns and 'Fecha' in df.columns:
        df = df.dropna(subset=['Total de envíos', 'Fecha'])
    
    # ---------------------------------------------------------
    # Filtro Global de Fechas
    # ---------------------------------------------------------
    st.sidebar.markdown("---")
    st.sidebar.header("🗓️ Filtros de Temporalidad")
    if 'Fecha' in df.columns and not df['Fecha'].empty:
        min_date = df['Fecha'].min().date()
        max_date = df['Fecha'].max().date()
    
        date_range = st.sidebar.date_input(
            "Selecciona el rango de análisis:",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
    
        if len(date_range) == 2:
            start_date, end_date = date_range
            mask = (df['Fecha'].dt.date >= start_date) & (df['Fecha'].dt.date <= end_date)
            df_filtered = df.loc[mask]
        else:
            df_filtered = df.copy()
    else:
        df_filtered = df.copy()

    # ---------------------------------------------------------
    # SECCIÓN 1: KPIs Ejecutivos (Estilo Tarjetas)
    # ---------------------------------------------------------
    
    total_envios = df_filtered['Total de envíos'].sum() if 'Total de envíos' in df_filtered.columns else 0
    total_jugadores = df_filtered['Jugadores'].sum() if 'Jugadores' in df_filtered.columns else 0
    tasa_act_global = (total_jugadores / total_envios) if total_envios > 0 else 0
    
    mix_ganador_str = "No calculable"
    if 'Producto' in df_filtered.columns and 'TIPO' in df_filtered.columns and 'Jugadores' in df_filtered.columns:
        mix_analisis = df_filtered.groupby(['Producto', 'TIPO'])[['Total de envíos', 'Jugadores']].sum().reset_index()
        mix_analisis['Actividad'] = mix_analisis['Jugadores'] / mix_analisis['Total de envíos']
        if not mix_analisis.empty:
            mix_top = mix_analisis.sort_values('Actividad', ascending=False).iloc[0]
            mix_ganador_str = f"{mix_top['Producto']} + {mix_top['TIPO']} ({(mix_top['Actividad']*100):.1f}%)"

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Volumen Impactado", f"{total_envios:,.0f}")
    col2.metric("Clientes Activos", f"{total_jugadores:,.0f}")
    col3.metric("Tasa de Actividad", f"{(tasa_act_global * 100):.2f}%")
    col4.metric("Mix Estrella", mix_ganador_str)
    
    st.markdown("<br>", unsafe_allow_html=True)


    # ---------------------------------------------------------
    # SECCIÓN 2: Insights y Plan de Acción (Estilo HTML Cards)
    # ---------------------------------------------------------
    def analizar_keywords(df_text):
        if 'Mensaje_Texto' not in df_text.columns or df_text.empty:
            return None
        
        df_text['Mensaje_Temp'] = df_text['Mensaje_Texto'].fillna('').astype(str).str.lower()
        
        categorias = {
            'Urgencia / Tiempo': ['hoy', 'ahora', 'ya', 'solo por', 'apresurate'],
            'Gratuidad / Regalo': ['gratis', 'regalo', 'regalamos', 'lleva'],
            'Incentivo Económico': ['saldo', 'bono', 's/', 'recarga'],
            'Pozo Millonario': ['pozo', 'millones', 'acumulado', 'millonario', 'premio']
        }
        
        resultados = []
        for cat, palabras in categorias.items():
            mask = df_text['Mensaje_Temp'].apply(lambda x: any(p in x for p in palabras))
            if mask.sum() > 0 and 'Tasa_Actividad' in df_text.columns:
                tasa_promedio = df_text.loc[mask, 'Tasa_Actividad'].mean()
                resultados.append({'Concepto': cat, 'Tasa Promedio': tasa_promedio, 'Uso': mask.sum()})
                
        return pd.DataFrame(resultados).sort_values('Tasa Promedio', ascending=False) if resultados else None

    # Lógica de Insights Rápidos
    top_canal_perf = "N/A"
    if 'TIPO' in df_filtered.columns and 'Jugadores' in df_filtered.columns and total_jugadores > 0:
        top_canal_perf = df_filtered.groupby('TIPO')['Jugadores'].sum().sort_values(ascending=False).index[0]
        
    analisis_kw = analizar_keywords(df_filtered.copy())
    gatillo = "No detectado"
    if analisis_kw is not None and not analisis_kw.empty:
        gatillo = f"{analisis_kw.iloc[0]['Concepto']} ({(analisis_kw.iloc[0]['Tasa Promedio']*100):.1f}%)"

    col_ins1, col_ins2 = st.columns(2)
    with col_ins1:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">🔍 Análisis de Rendimiento & Copy</div>
            <div class="insight-text">
                <b>Canal Líder (Volumen Neto):</b> {top_canal_perf} es la vía principal de tracción de jugadores en este periodo.<br><br>
                <b>El Gatillo Ganador (Keywords):</b> Los mensajes que incluyen palabras sobre <b>{gatillo}</b> generan las tasas de conversión más altas. Priorizar estos conceptos en las dos primeras líneas de SMS o WhatsApp.<br><br>
                <b>Fricción de Redirección:</b> Asegurar siempre el uso de links cortos (cutt.ly) para no interrumpir el flujo visual.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_ins2:
        st.markdown(f"""
        <div class="insight-card" style="border-left-color: #10b981;">
            <div class="insight-title">🚀 Plan de Acción Estratégico</div>
            <div class="insight-text">
                <b>1. Enfoque de Presupuesto:</b> Apoyarse fuertemente en campañas automáticas "Triggers de Saldo", ya que consistentemente superan los envíos genéricos.<br><br>
                <b>2. Prevención de Fatiga:</b> Rotar de inmediato las bases de datos para canales tradicionales (MAIL) para evitar quemar a los usuarios VIP.<br><br>
                <b>3. Próximo Mix:</b> Replicar la arquitectura de la mejor campaña reciente (ver tabla inferior). Combinar urgencia con llamados a la acción rápidos.
            </div>
        </div>
        """, unsafe_allow_html=True)


    # ---------------------------------------------------------
    # SECCIÓN 3: Gráficos Interactivos (Estilo ApexCharts)
    # ---------------------------------------------------------
    st.markdown("### 📊 Rendimiento de Actividad")
    tab_chan, tab_prod = st.tabs(["Análisis por Canal", "Análisis por Producto"])
    
    # Paletas de color corporativas (Tailwind)
    color_canal = '#3b82f6' # Blue 500
    color_prod = '#10b981' # Emerald 500
    
    with tab_chan:
        if not df_filtered.empty and 'TIPO' in df_filtered.columns and 'Tasa_Actividad' in df_filtered.columns:
            # Gráfico de Barras Elegante
            canal_grp = df_filtered.groupby('TIPO')['Tasa_Actividad'].mean().reset_index()
            bar_canal = alt.Chart(canal_grp).mark_bar(color=color_canal, cornerRadiusTopRight=4, cornerRadiusBottomRight=4).encode(
                x=alt.X('Tasa_Actividad:Q', axis=alt.Axis(format='%', grid=True, title='Tasa de Actividad Promedio')),
                y=alt.Y('TIPO:N', sort='-x', title='', axis=alt.Axis(labelFontWeight='bold')),
                tooltip=[alt.Tooltip('TIPO', title='Canal'), alt.Tooltip('Tasa_Actividad', format='.2%', title='Actividad')]
            ).properties(height=300)
            
            st.altair_chart(bar_canal, use_container_width=True)

    with tab_prod:
        if not df_filtered.empty and 'Producto' in df_filtered.columns and 'Tasa_Actividad' in df_filtered.columns:
            prod_grp = df_filtered.groupby('Producto')['Tasa_Actividad'].mean().reset_index()
            bar_prod = alt.Chart(prod_grp).mark_bar(color=color_prod, cornerRadiusTopRight=4, cornerRadiusBottomRight=4).encode(
                x=alt.X('Tasa_Actividad:Q', axis=alt.Axis(format='%', grid=True, title='Tasa de Actividad Promedio')),
                y=alt.Y('Producto:N', sort='-x', title='', axis=alt.Axis(labelFontWeight='bold')),
                tooltip=[alt.Tooltip('Producto', title='Producto'), alt.Tooltip('Tasa_Actividad', format='.2%', title='Actividad')]
            ).properties(height=350)
            
            st.altair_chart(bar_prod, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)


    # ---------------------------------------------------------
    # SECCIÓN 4: Tablas de Datos (Alertas y Top 10)
    # ---------------------------------------------------------
    col_t1, col_t2 = st.columns([1, 2])
    
    with col_t1:
        st.markdown("<h3 style='color: #ef4444;'>🚨 Alertas Críticas (<1%)</h3>", unsafe_allow_html=True)
        if 'Tasa_Actividad' in df_filtered.columns and 'Total de envíos' in df_filtered.columns:
            alertas_df = df_filtered[(df_filtered['Tasa_Actividad'] < 0.01) & (df_filtered['Total de envíos'] >= 500)]
            if not alertas_df.empty:
                alertas_df_clean = alertas_df.sort_values('Tasa_Actividad', ascending=True)
                cols_alerta = ['Campaña', 'TIPO', 'Tasa_Actividad']
                cols_alerta_final = [c for c in cols_alerta if c in alertas_df_clean.columns]
                
                st.dataframe(
                    alertas_df_clean[cols_alerta_final].style.format({'Tasa_Actividad': '{:.2%}'}).background_gradient(cmap='Reds', subset=['Tasa_Actividad']),
                    use_container_width=True, hide_index=True
                )
            else:
                st.info("No hay campañas críticas en este periodo.")

    with col_t2:
        st.markdown("<h3 style='color: #f59e0b;'>🏆 Top 10 Mejores Campañas</h3>", unsafe_allow_html=True)
        
        # Pequeños filtros encima de la tabla
        f_col1, f_col2 = st.columns(2)
        f_prod = f_col1.multiselect("Filtrar Producto:", df_filtered['Producto'].dropna().unique() if 'Producto' in df_filtered.columns else [])
        f_can = f_col2.multiselect("Filtrar Canal:", df_filtered['TIPO'].dropna().unique() if 'TIPO' in df_filtered.columns else [])
        
        df_top = df_filtered.copy()
        if f_prod and 'Producto' in df_top.columns:
            df_top = df_top[df_top['Producto'].isin(f_prod)]
        if f_can and 'TIPO' in df_top.columns:
            df_top = df_top[df_top['TIPO'].isin(f_can)]
            
        if 'Total de envíos' in df_top.columns and 'Tasa_Actividad' in df_top.columns:
            top_10 = df_top[df_top['Total de envíos'] >= 500].sort_values('Tasa_Actividad', ascending=False).head(10)
            if 'Fecha' in top_10.columns:
                top_10['Fecha'] = top_10['Fecha'].dt.strftime('%Y-%m-%d')
            
            columnas_deseadas = ['Fecha', 'Producto', 'TIPO', 'Mensaje_Texto', 'Total de envíos', 'Tasa_Actividad']
            columnas_finales = [col for col in columnas_deseadas if col in top_10.columns]
            
            formato_final = {k: v for k, v in {'Tasa_Actividad': '{:.2%}', 'Total de envíos': '{:,.0f}'}.items() if k in columnas_finales}
            
            # Tabla estilizada
            st.dataframe(
                top_10[columnas_finales].style.format(formato_final).background_gradient(cmap='Greens', subset=['Tasa_Actividad']),
                use_container_width=True, hide_index=True
            )
else:
    # Pantalla de bienvenida amigable cuando no hay archivo
    st.info("👋 ¡Bienvenido! Por favor, sube tu archivo Excel en el menú lateral izquierdo para comenzar el análisis.")
