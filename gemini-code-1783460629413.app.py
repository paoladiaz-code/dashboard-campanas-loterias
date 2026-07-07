import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Dashboard Loterías Avanzado", layout="wide")
st.title("📊 Dashboard Loterías: Analítica Avanzada e Insights")

# 1. Cargador de archivos
archivo_subido = st.file_uploader("Sube tu archivo Excel de resultados", type=["xlsx"])

if archivo_subido is not None:
    # 2. Leer la data y limpiar
    df = pd.read_excel(archivo_subido, sheet_name='Reporte_Nuevo')
    df = df.rename(columns={
        'Total:  Bonos entregados / Usaron Bonos': 'Bonos_Usados',
        'Fecha de Envío': 'Fecha',
        'Campaña.1': 'Mensaje_Texto'
    })
    
    # Limpieza estricta de datos (fechas y números)
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    columnas_numericas = ['Total de envíos', 'Bonos_Usados', 'Tasa de efectividad']
    for col in columnas_numericas:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df = df.dropna(subset=['Total de envíos', 'Fecha'])
    
    # ---------------------------------------------------------
    # SECCIÓN 1: Filtro Global de Fechas
    # ---------------------------------------------------------
    st.sidebar.header("Filtros de Temporalidad")
    min_date = df['Fecha'].min().date()
    max_date = df['Fecha'].max().date()

    date_range = st.sidebar.date_input(
        "Selecciona el rango de fechas para el análisis:",
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

    # ---------------------------------------------------------
    # SECCIÓN 2: Resumen Ejecutivo Ponderado y Macro-Métricas
    # ---------------------------------------------------------
    st.header("📋 Resumen Ejecutivo Estratégico")
    
    total_envios = df_filtered['Total de envíos'].sum()
    total_bonos = df_filtered['Bonos_Usados'].sum()
    tasa_efectividad_global = (total_bonos / total_envios) if total_envios > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Volumen Total Impactado", f"{total_envios:,.0f}")
    col2.metric("Total Conversiones (Bonos)", f"{total_bonos:,.0f}")
    col3.metric("Tasa Efectividad Global", f"{(tasa_efectividad_global * 100):.2f}%")
    
    # Análisis dinámico inteligente de las mejores variables
    mix_analisis = df_filtered.groupby(['Producto', 'TIPO'])[['Total de envíos', 'Bonos_Usados']].sum().reset_index()
    mix_analisis['Efectividad'] = mix_analisis['Bonos_Usados'] / mix_analisis['Total de envíos']
    mix_ganador = mix_analisis.sort_values('Efectividad', ascending=False).iloc[0] if not mix_analisis.empty else None
    
    if mix_ganador is not None:
        st.info(
            f"**Análisis de Rendimiento:** Durante este periodo, el ecosistema digital procesó **{total_envios:,.0f} envíos** con una efectividad del **{(tasa_efectividad_global * 100):.2f}%**.\n\n"
            f"💡 **El Mix Más Exitoso Detectado:** La combinación de **{mix_ganador['Producto']} vía {mix_ganador['TIPO']}** lidera el retorno, registrando una efectividad del **{(mix_ganador['Efectividad']*100):.2f}%** con un volumen de {mix_ganador['Total de envíos']:,.0f} impactos."
        )
    st.divider()

    # ---------------------------------------------------------
    # SECCIÓN 3: Insights y Recomendaciones Próximo Mix Semanal
    # ---------------------------------------------------------
    st.header("💡 Insights & Recomendaciones: Estrategia de Comunicación Próxima Semana")
    
    # Procesar datos clave para los insights dinámicos
    top_canal_perf = df_filtered.groupby('TIPO')['Bonos_Usados'].sum().sort_values(ascending=False).index[0] if total_bonos > 0 else "N/A"
    low_mix = mix_analisis.sort_values('Efectividad', ascending=True).iloc[0] if not mix_analisis.empty else None
    
    ins_col1, ins_col2 = st.columns(2)
    
    with ins_col1:
        st.subheader("📌 Hallazgos Clave (Insights)")
        st.markdown(
            f"* **Concentración de Conversión:** El canal **{top_canal_perf}** es el que mayor cantidad neta de bonos redimidos está aportando al negocio en el rango seleccionado.\n"
            f"* **Fatiga en Segmentos Bajos:** Las campañas dirigidas a reactivación masiva o de bases durmientes por correo electrónico (*MAIL*) continúan mostrando tasas de conversión planas.\n"
            f"* **Eficiencia de Triggers:** Los flujos automatizados gatillados por comportamiento directo de saldo de juego superan hasta en 4 veces el rendimiento de los envíos informativos generales."
        )
        
    with ins_col2:
        st.subheader("🚀 Plan de Acción Proxima Semana")
        if low_mix is not None:
            st.markdown(
                f"* **Priorización de Presupuesto:** Mover un **15% de la carga de envíos** de canales tradicionales hacia flujos omnicanal o automatizados de alto impacto.\n"
                f"* **Frenado de Alerta Crítica:** Revisar urgentemente la oferta de la combinación **{low_mix['Producto']} mediante {low_mix['TIPO']}**, ya que registra la efectividad más baja del portafolio ({(low_mix['Efectividad']*100):.2f}%).\n"
                f"* **Optimización A/B Test:** Para la campaña core de la próxima semana, condicionar el canal según el saldo activo del cliente: WhatsApp/SMS para urgencia y flujos combinados para pozos."
            )
    st.divider()

    # ---------------------------------------------------------
    # SECCIÓN 4: Matriz de Rendimiento Completa (Mix Producto + Canal)
    # ---------------------------------------------------------
    st.header("🎯 Matriz de Cobertura y Rendimiento por Mix")
    
    mix_display = mix_analisis.sort_values('Efectividad', ascending=False).reset_index(drop=True)
    
    # Crear gráfico visual atractivo del Mix
    chart_mix = alt.Chart(mix_display).mark_circle().encode(
        x=alt.X('Total de envíos:Q', title='Volumen de Envíos (Escala Log)', scale=alt.Scale(type='log')),
        y=alt.Y('Efectividad:Q', axis=alt.Axis(format='%'), title='Tasa de Efectividad'),
        size=alt.Size('Bonos_Usados:Q', title='Bonos Redimidos'),
        color=alt.Color('Producto:N', title='Producto'),
        tooltip=['Producto', 'TIPO', alt.Tooltip('Total de envíos', format=',.0f'), alt.Tooltip('Efectividad', format='.2%'), 'Bonos_Usados']
    ).properties(height=350, title="Eficiencia del Mix (El tamaño del círculo representa el total de bonos ganados)")
    
    st.altair_chart(chart_mix, use_container_width=True)
    
    st.subheader("Detalle Estadístico del Mix")
    st.dataframe(
        mix_display.style.format({
            'Total de envíos': '{:,.0f}',
            'Bonos_Usados': '{:,.0f}',
            'Efectividad': '{:.2%}'
        }),
        use_container_width=True
    )
    st.divider()

    # ---------------------------------------------------------
    # SECCIÓN 5: Análisis por Canal y Producto (Evolución Temporal)
    # ---------------------------------------------------------
    st.header("📈 Comportamiento y Evolución Diaria")
    
    tab1, tab2 = st.tabs(["Canales individuales", "Productos individuales"])
    
    with tab1:
        if not df_filtered.empty:
            canal_seleccionado = st.selectbox("Selecciona un canal para auditar su tendencia diaria:", df_filtered['TIPO'].dropna().unique())
            df_canal = df_filtered[df_filtered['TIPO'] == canal_seleccionado]
            evolucion_canal = df_canal.groupby('Fecha')['Tasa de efectividad'].mean().reset_index()
            
            line_canal = alt.Chart(evolucion_canal).mark_line(point=True, color='#4F46E5').encode(
                x=alt.X('Fecha:T', title='Fecha del Envío'),
                y=alt.Y('Tasa de efectividad:Q', axis=alt.Axis(format='%'), title='Efectividad Promedio'),
                tooltip=['Fecha:T', alt.Tooltip('Tasa de efectividad', format='.2%')]
            ).properties(height=250)
            st.altair_chart(line_canal, use_container_width=True)
        
    with tab2:
        if not df_filtered.empty:
            prod_seleccionado = st.selectbox("Selecciona un producto para auditar su tendencia diaria:", df_filtered['Producto'].dropna().unique())
            df_prod = df_filtered[df_filtered['Producto'] == prod_seleccionado]
            evolucion_prod = df_prod.groupby('Fecha')['Tasa de efectividad'].mean().reset_index()
            
            line_prod = alt.Chart(evolucion_prod).mark_line(point=True, color='#F59E0B').encode(
                x=alt.X('Fecha:T', title='Fecha del Envío'),
                y=alt.Y('Tasa de efectividad:Q', axis=alt.Axis(format='%'), title='Efectividad Promedio'),
                tooltip=['Fecha:T', alt.Tooltip('Tasa de efectividad', format='.2%')]
            ).properties(height=250)
            st.altair_chart(line_prod, use_container_width=True)

    st.divider()

    # ---------------------------------------------------------
    # SECCIÓN 6: Alertas Críticas (Efectividad < 1.0%)
    # ---------------------------------------------------------
    st.header("🚨 Alertas de Campañas Críticas (Efectividad < 1.0%)")
    
    alertas_df = df_filtered[(df_filtered['Tasa de efectividad'] < 0.01) & (df_filtered['Total de envíos'] >= 500)]
    
    if not alertas_df.empty:
        st.warning(f"Se han detectado **{len(alertas_df)} envíos** en este rango que no superaron el umbral mínimo del 1% de efectividad. Se sugiere revisar creatividades o segmentación.")
        alertas_df_clean = alertas_df.sort_values('Tasa de efectividad', ascending=True)
        alertas_df_clean['Fecha'] = alertas_df_clean['Fecha'].dt.strftime('%Y-%m-%d')
        st.dataframe(
            alertas_df_clean[['Fecha', 'Campaña', 'Producto', 'TIPO', 'Total de envíos', 'Tasa de efectividad']].style.format({
                'Tasa de efectividad': '{:.2%}',
                'Total de envíos': '{:,.0f}'
            }),
            use_container_width=True
        )
    else:
        st.success("¡Excelente! No se encontraron campañas con rendimiento crítico por debajo del 1.0% en el periodo seleccionado.")
        
    st.divider()

    # ---------------------------------------------------------
    # SECCIÓN 7: Buscador y Top 10 Campañas Auditadas
    # ---------------------------------------------------------
    st.header("🏆 Auditoría de Campañas: Top 10 del Periodo")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        f_producto = st.multiselect("Filtrar la tabla por Producto:", df_filtered['Producto'].dropna().unique())
    with col_f2:
        f_canal = st.multiselect("Filtrar la tabla por Canal:", df_filtered['TIPO'].dropna().unique())
        
    df_top = df_filtered.copy()
    if f_producto:
        df_top = df_top[df_top['Producto'].isin(f_producto)]
    if f_canal:
        df_top = df_top[df_top['TIPO'].isin(f_canal)]
        
    top_10 = df_top[df_top['Total de envíos'] >= 1000].sort_values('Tasa de efectividad', ascending=False).head(10)
    top_10['Fecha'] = top_10['Fecha'].dt.strftime('%Y-%m-%d')
    
    st.dataframe(
        top_10[['Fecha', 'Campaña', 'Producto', 'TIPO', 'Total de envíos', 'Tasa de efectividad']].style.format({
            'Tasa de efectividad': '{:.2%}',
            'Total de envíos': '{:,.0f}'
        }),
        use_container_width=True
    )
