import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Dashboard Loterías Avanzado", layout="wide")
st.title("📊 Dashboard Loterías: Analítica de Actividad e Insights")

# 1. Cargador de archivos
archivo_subido = st.file_uploader("Sube tu archivo Excel de resultados", type=["xlsx"])

if archivo_subido is not None:
    # 2. Leer la data y limpiar
    df = pd.read_excel(archivo_subido, sheet_name='Reporte_Nuevo')
    df = df.rename(columns={
        'Total:  Bonos entregados / Usaron Bonos': 'Bonos_Usados',
        'Clientes que jugaron': 'Jugadores',
        'Tasa de Actividad en juego': 'Tasa_Actividad',
        'Fecha de Envío': 'Fecha',
        'Campaña.1': 'Mensaje_Texto'
    })
    
    # Limpieza estricta de datos (fechas y números)
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    columnas_numericas = ['Total de envíos', 'Bonos_Usados', 'Tasa de efectividad', 'Jugadores', 'Tasa_Actividad']
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
    st.header("📋 Resumen Ejecutivo Estratégico (Foco: Actividad)")
    
    total_envios = df_filtered['Total de envíos'].sum()
    total_jugadores = df_filtered['Jugadores'].sum()
    tasa_act_global = (total_jugadores / total_envios) if total_envios > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Volumen Total Impactado", f"{total_envios:,.0f}")
    col2.metric("Total Clientes que Jugaron", f"{total_jugadores:,.0f}")
    col3.metric("Tasa de Actividad Global", f"{(tasa_act_global * 100):.2f}%")
    
    # Análisis dinámico inteligente
    mix_analisis = df_filtered.groupby(['Producto', 'TIPO'])[['Total de envíos', 'Jugadores']].sum().reset_index()
    mix_analisis['Actividad'] = mix_analisis['Jugadores'] / mix_analisis['Total de envíos']
    mix_ganador = mix_analisis.sort_values('Actividad', ascending=False).iloc[0] if not mix_analisis.empty else None
    
    if mix_ganador is not None:
        st.info(
            f"**Diagnóstico de Rendimiento:** En el rango seleccionado, el ecosistema digital movilizó a **{total_jugadores:,.0f} clientes reales a jugar**, logrando una tasa de actividad del **{(tasa_act_global * 100):.2f}%** sobre el total de impactos.\n\n"
            f"💡 **Tracción Principal:** El mix comercial más efectivo para generar juego es **{mix_ganador['Producto']} vía {mix_ganador['TIPO']}**, liderando el retorno con una tasa de actividad del **{(mix_ganador['Actividad']*100):.2f}%**. Mantener este flujo encendido y optimizado debe ser prioridad número uno."
        )
    st.divider()

    # ---------------------------------------------------------
    # SECCIÓN 3: Insights y Análisis de Mensajes (Keywords)
    # ---------------------------------------------------------
    st.header("💡 Insights & Análisis de Mensajes")
    
    # Función para analizar keywords en los mensajes
    def analizar_keywords(df_text):
        if 'Mensaje_Texto' not in df_text.columns or df_text.empty:
            return None
        
        df_text['Mensaje_Temp'] = df_text['Mensaje_Texto'].fillna('').str.lower()
        
        categorias = {
            'Urgencia / Tiempo': ['hoy', 'ahora', 'ya', 'solo por'],
            'Gratuidad / Regalo': ['gratis', 'regalo', 'regalamos', 'lleva'],
            'Incentivo Económico': ['saldo', 'bono', 's/'],
            'Pozo / Millonario': ['pozo', 'millones', 'acumulado', 'millonario'],
            'Redirección Directa (Links)': ['http', 'cutt.ly', 'bit.ly', 'link', 'juega aqui']
        }
        
        resultados = []
        for cat, palabras in categorias.items():
            mask = df_text['Mensaje_Temp'].apply(lambda x: any(p in x for p in palabras))
            if mask.sum() > 0:
                tasa_promedio = df_text.loc[mask, 'Tasa_Actividad'].mean()
                resultados.append({'Concepto': cat, 'Tasa Promedio': tasa_promedio, 'Uso': mask.sum()})
                
        return pd.DataFrame(resultados).sort_values('Tasa Promedio', ascending=False) if resultados else None

    # Procesar datos clave para los insights dinámicos
    top_canal_perf = df_filtered.groupby('TIPO')['Jugadores'].sum().sort_values(ascending=False).index[0] if total_jugadores > 0 else "N/A"
    
    ins_col1, ins_col2 = st.columns(2)
    
    with ins_col1:
        st.subheader("📌 Patrones de Comportamiento")
        st.markdown(
            f"* **El Canal de Volumen vs. Conversión:** El canal **{top_canal_perf}** es el mayor generador neto de jugadores activos. Sin embargo, se debe vigilar que la masividad no diluya la tasa de actividad porcentual.\n"
            f"* **Triggers de Saldo:** Los clientes con saldo en sus cuentas responden de manera inmediata a las alertas automáticas. Estas campañas de nicho siempre presentarán una Tasa de Actividad superior a los envíos de cluster masivos."
        )
        
    with ins_col2:
        st.subheader("📝 Análisis Semántico (Keywords & Copy)")
        analisis_kw = analizar_keywords(df_filtered)
        
        if analisis_kw is not None and not analisis_kw.empty:
            mejor_concepto = analisis_kw.iloc[0]
            st.markdown(
                f"* **El Gatillo Ganador:** Los mensajes que incluyen conceptos de **{mejor_concepto['Concepto']}** promedian una tasa de actividad del **{(mejor_concepto['Tasa Promedio']*100):.2f}%**.\n"
                f"* **Fricción en la Redirección:** Incluir URLs cortas (*cutt.ly, bit.ly*) y llamados a la acción claros ('Juega aquí') es vital en SMS/WhatsApp para reducir los pasos del cliente hacia la plataforma.\n"
                f"* **Recomendación de Copy:** Para la siguiente semana, estructurar el mensaje priorizando el motivo ganador ({mejor_concepto['Concepto']}) en los primeros 40 caracteres del texto."
            )
        else:
            st.markdown("* No se detectó suficiente variedad en los textos de las campañas filtradas para realizar un análisis semántico. Se recomienda incluir la columna completa de mensajes en futuros reportes.")
            
    st.divider()

    # ---------------------------------------------------------
    # SECCIÓN 4: Rendimiento de Canales y Productos (Con Drill-down)
    # ---------------------------------------------------------
    st.header("📈 Rendimiento de Actividad: Canales y Productos")
    
    tab1, tab2 = st.tabs(["Canales (TIPO)", "Productos"])
    
    with tab1:
        st.subheader("Tasa de Actividad Promedio por Canal")
        if not df_filtered.empty:
            canal_grp = df_filtered.groupby('TIPO')['Tasa_Actividad'].mean().reset_index()
            bar_canal = alt.Chart(canal_grp).mark_bar(color='#10B981').encode(
                x=alt.X('Tasa_Actividad:Q', axis=alt.Axis(format='%'), title='Tasa de Actividad en Juego'),
                y=alt.Y('TIPO:N', sort='-x', title='Canal'),
                tooltip=[alt.Tooltip('TIPO', title='Canal'), alt.Tooltip('Tasa_Actividad', format='.2%', title='Actividad')]
            ).properties(height=300)
            st.altair_chart(bar_canal, use_container_width=True)
            
            st.write("### Evolución Diaria de Actividad por Canal")
            canal_seleccionado = st.selectbox("Selecciona un canal para auditar su tendencia:", df_filtered['TIPO'].dropna().unique())
            
            df_canal = df_filtered[df_filtered['TIPO'] == canal_seleccionado]
            evolucion_canal = df_canal.groupby('Fecha')['Tasa_Actividad'].mean().reset_index()
            
            line_canal = alt.Chart(evolucion_canal).mark_line(point=True, color='#10B981').encode(
                x=alt.X('Fecha:T', title='Fecha de Envío'),
                y=alt.Y('Tasa_Actividad:Q', axis=alt.Axis(format='%'), title='Tasa de Actividad Promedio'),
                tooltip=['Fecha:T', alt.Tooltip('Tasa_Actividad', format='.2%', title='Actividad')]
            ).properties(height=250)
            st.altair_chart(line_canal, use_container_width=True)
        
    with tab2:
        st.subheader("Tasa de Actividad Promedio por Producto")
        if not df_filtered.empty:
            prod_grp = df_filtered.groupby('Producto')['Tasa_Actividad'].mean().reset_index()
            bar_prod = alt.Chart(prod_grp).mark_bar(color='#F59E0B').encode(
                x=alt.X('Tasa_Actividad:Q', axis=alt.Axis(format='%'), title='Tasa de Actividad en Juego'),
                y=alt.Y('Producto:N', sort='-x', title='Producto'),
                tooltip=[alt.Tooltip('Producto', title='Producto'), alt.Tooltip('Tasa_Actividad', format='.2%', title='Actividad')]
            ).properties(height=300)
            st.altair_chart(bar_prod, use_container_width=True)
            
            st.write("### Evolución Diaria de Actividad por Producto")
            prod_seleccionado = st.selectbox("Selecciona un producto para auditar su tendencia:", df_filtered['Producto'].dropna().unique())
            
            df_prod = df_filtered[df_filtered['Producto'] == prod_seleccionado]
            evolucion_prod = df_prod.groupby('Fecha')['Tasa_Actividad'].mean().reset_index()
            
            line_prod = alt.Chart(evolucion_prod).mark_line(point=True, color='#EF4444').encode(
                x=alt.X('Fecha:T', title='Fecha de Envío'),
                y=alt.Y('Tasa_Actividad:Q', axis=alt.Axis(format='%'), title='Tasa de Actividad Promedio'),
                tooltip=['Fecha:T', alt.Tooltip('Tasa_Actividad', format='.2%', title='Actividad')]
            ).properties(height=250)
            st.altair_chart(line_prod, use_container_width=True)

    st.divider()

    # ---------------------------------------------------------
    # SECCIÓN 5: Alertas Críticas (Actividad < 1.0%)
    # ---------------------------------------------------------
    st.header("🚨 Alertas Críticas (Tasa de Actividad < 1.0%)")
    
    alertas_df = df_filtered[(df_filtered['Tasa_Actividad'] < 0.01) & (df_filtered['Total de envíos'] >= 500)]
    
    if not alertas_df.empty:
        st.warning(f"Se detectaron **{len(alertas_df)} envíos** masivos (más de 500 impactos) que generaron menos del 1% de actividad de juego. Se sugiere pausar y reevaluar la segmentación de estas campañas.")
        alertas_df_clean = alertas_df.sort_values('Tasa_Actividad', ascending=True)
        alertas_df_clean['Fecha'] = alertas_df_clean['Fecha'].dt.strftime('%Y-%m-%d')
        st.dataframe(
            alertas_df_clean[['Fecha', 'Campaña', 'Producto', 'TIPO', 'Total de envíos', 'Jugadores', 'Tasa_Actividad']].style.format({
                'Tasa_Actividad': '{:.2%}',
                'Total de envíos': '{:,.0f}',
                'Jugadores': '{:,.0f}'
            }),
            use_container_width=True
        )
    else:
        st.success("¡Excelente! No se encontraron campañas masivas con rendimiento de actividad inferior al 1.0% en el periodo seleccionado.")
        
    st.divider()

    # ---------------------------------------------------------
    # SECCIÓN 6: Buscador y Top 10 Campañas Auditadas
    # ---------------------------------------------------------
    st.header("🏆 Top 10 Campañas (Por Actividad de Juego)")
    
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
        
    # Filtrar min 500 envíos y ordenar por Tasa de Actividad
    top_10 = df_top[df_top['Total de envíos'] >= 500].sort_values('Tasa_Actividad', ascending=False).head(10)
    top_10['Fecha'] = top_10['Fecha'].dt.strftime('%Y-%m-%d')
    
    # Se agrega la columna de Mensaje_Texto para que se pueda auditar el copy ganador
    st.dataframe(
        top_10[['Fecha', 'Campaña', 'Producto', 'TIPO', 'Mensaje_Texto', 'Total de envíos', 'Jugadores', 'Tasa_Actividad']].style.format({
            'Tasa_Actividad': '{:.2%}',
            'Total de envíos': '{:,.0f}',
            'Jugadores': '{:,.0f}'
        }),
        use_container_width=True
    )
