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
    
    # Renombrado flexible
    df = df.rename(columns={
        'Total:  Bonos entregados / Usaron Bonos': 'Bonos_Usados',
        'Clientes que jugaron': 'Jugadores',
        'Tasa de Actividad en juego': 'Tasa_Actividad',
        'Fecha de Envío': 'Fecha',
        'Campaña.1': 'Mensaje_Texto',
        'Mensaje': 'Mensaje_Texto'
    })
    
    # Limpieza estricta de datos (fechas y números)
    if 'Fecha' in df.columns:
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        
    columnas_numericas = ['Total de envíos', 'Bonos_Usados', 'Tasa de efectividad', 'Jugadores', 'Tasa_Actividad']
    for col in columnas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    if 'Total de envíos' in df.columns and 'Fecha' in df.columns:
        df = df.dropna(subset=['Total de envíos', 'Fecha'])
    
    # ---------------------------------------------------------
    # SECCIÓN 1: Filtro Global de Fechas
    # ---------------------------------------------------------
    st.sidebar.header("Filtros de Temporalidad")
    if 'Fecha' in df.columns and not df['Fecha'].empty:
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
    else:
        df_filtered = df.copy()

    # ---------------------------------------------------------
    # SECCIÓN 2: Resumen Ejecutivo Ponderado
    # ---------------------------------------------------------
    st.header("📋 Resumen Ejecutivo Estratégico (Foco: Actividad)")
    
    total_envios = df_filtered['Total de envíos'].sum() if 'Total de envíos' in df_filtered.columns else 0
    total_jugadores = df_filtered['Jugadores'].sum() if 'Jugadores' in df_filtered.columns else 0
    tasa_act_global = (total_jugadores / total_envios) if total_envios > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Volumen Total Impactado", f"{total_envios:,.0f}")
    col2.metric("Total Clientes que Jugaron", f"{total_jugadores:,.0f}")
    col3.metric("Tasa de Actividad Global", f"{(tasa_act_global * 100):.2f}%")
    
    if 'Producto' in df_filtered.columns and 'TIPO' in df_filtered.columns and 'Jugadores' in df_filtered.columns:
        mix_analisis = df_filtered.groupby(['Producto', 'TIPO'])[['Total de envíos', 'Jugadores']].sum().reset_index()
        mix_analisis['Actividad'] = mix_analisis['Jugadores'] / mix_analisis['Total de envíos']
        mix_ganador = mix_analisis.sort_values('Actividad', ascending=False).iloc[0] if not mix_analisis.empty else None
        
        if mix_ganador is not None:
            st.info(
                f"**Diagnóstico de Rendimiento:** En el rango seleccionado, el ecosistema digital movilizó a **{total_jugadores:,.0f} clientes reales a jugar**, logrando una tasa de actividad del **{(tasa_act_global * 100):.2f}%** sobre el total de impactos.\n\n"
                f"💡 **Tracción Principal:** El mix comercial más efectivo para generar juego es **{mix_ganador['Producto']} vía {mix_ganador['TIPO']}**, liderando el retorno con una tasa de actividad del **{(mix_ganador['Actividad']*100):.2f}%**."
            )
    st.divider()

    # ---------------------------------------------------------
    # SECCIÓN 3: Insights y Planificación Próxima Semana
    # ---------------------------------------------------------
    st.header("💡 Insights & Plan de Acción para Próxima Semana")
    
    def analizar_keywords(df_text):
        if 'Mensaje_Texto' not in df_text.columns or df_text.empty:
            return None
        
        df_text['Mensaje_Temp'] = df_text['Mensaje_Texto'].fillna('').astype(str).str.lower()
        
        categorias = {
            'Urgencia / Tiempo (hoy, ahora, ya)': ['hoy', 'ahora', 'ya', 'solo por'],
            'Gratuidad / Regalo (gratis, lleva)': ['gratis', 'regalo', 'regalamos', 'lleva'],
            'Incentivo Económico (saldo, bono)': ['saldo', 'bono', 's/'],
            'Pozo / Millonario (pozo, millones)': ['pozo', 'millones', 'acumulado', 'millonario'],
            'Call To Action (juega aqui, links)': ['http', 'cutt.ly', 'bit.ly', 'link', 'juega aqui']
        }
        
        resultados = []
        for cat, palabras in categorias.items():
            mask = df_text['Mensaje_Temp'].apply(lambda x: any(p in x for p in palabras))
            if mask.sum() > 0 and 'Tasa_Actividad' in df_text.columns:
                tasa_promedio = df_text.loc[mask, 'Tasa_Actividad'].mean()
                resultados.append({'Concepto': cat, 'Tasa Promedio': tasa_promedio, 'Uso': mask.sum()})
                
        return pd.DataFrame(resultados).sort_values('Tasa Promedio', ascending=False) if resultados else None

    ins_col1, ins_col2 = st.columns(2)
    
    with ins_col1:
        st.subheader("📝 Análisis Semántico (Keywords)")
        analisis_kw = analizar_keywords(df_filtered.copy())
        
        if analisis_kw is not None and not analisis_kw.empty:
            mejor_concepto = analisis_kw.iloc[0]
            st.markdown(
                f"* **El Gatillo Ganador:** Textos con conceptos de **{mejor_concepto['Concepto']}** promedian una tasa de actividad superior ({(mejor_concepto['Tasa Promedio']*100):.2f}%).\n"
                f"* **Redirección:** Asegúrate de incluir URLs cortas y llamados a la acción imperativos ('Juega aquí') en los primeros caracteres para reducir la fricción en la lectura rápida.\n"
                f"* **Copy Sugerido:** Mantener la urgencia y el gancho del incentivo económico en las dos primeras líneas del SMS o WhatsApp."
            )
        else:
            st.markdown("* No se detectó suficiente variedad en los textos para el análisis semántico.")

    with ins_col2:
        st.subheader("🗓️ Recomendaciones Próxima Semana")
        # Analizando tendencias recientes (Últimos 14 días del reporte)
        if not df_filtered.empty and 'Fecha' in df_filtered.columns:
            max_date_data = df_filtered['Fecha'].max()
            recent_cutoff = max_date_data - pd.Timedelta(days=14)
            df_recent = df_filtered[df_filtered['Fecha'] >= recent_cutoff]
            
            if not df_recent.empty and 'Jugadores' in df_recent.columns and 'Total de envíos' in df_recent.columns:
                canal_grp_rec = df_recent.groupby('TIPO')[['Total de envíos', 'Jugadores']].sum()
                canal_grp_rec['Tasa'] = canal_grp_rec['Jugadores'] / canal_grp_rec['Total de envíos']
                top_rec_canal = canal_grp_rec.sort_values('Tasa', ascending=False).index[0] if not canal_grp_rec.empty else "N/A"
                
                prod_grp_rec = df_recent.groupby('Producto')[['Total de envíos', 'Jugadores']].sum()
                prod_grp_rec['Tasa'] = prod_grp_rec['Jugadores'] / prod_grp_rec['Total de envíos']
                top_rec_prod = prod_grp_rec.sort_values('Tasa', ascending=False).index[0] if not prod_grp_rec.empty else "N/A"
                
                st.markdown(
                    f"*(Basado en la tracción de los últimos 14 días analizados)*\n"
                    f"* **Foco de Producto:** **{top_rec_prod}** demostró el mayor pico de actividad recientemente. Se recomienda destinar el mayor volumen de envíos a este producto la próxima semana.\n"
                    f"* **Canal Prioritario:** **{top_rec_canal}** está liderando la conversión actual. Úsalo como vía principal para los segmentos VIP o triggers automáticos.\n"
                    f"* **Manejo de Fatiga:** Rotar segmentos en los canales tradicionales (Mail/SMS genérico) para evitar quemar a la base de usuarios. Apoyarse en la automatización."
                )
            else:
                st.write("Faltan datos en las columnas de envíos para generar la recomendación reciente.")
        else:
            st.write("Filtro de fecha vacío.")

    st.divider()

    # ---------------------------------------------------------
    # SECCIÓN 4: Rendimiento de Canales y Productos (Con Drill-down)
    # ---------------------------------------------------------
    st.header("📈 Rendimiento de Actividad: Canales y Productos")
    
    tab1, tab2 = st.tabs(["Canales (TIPO)", "Productos"])
    
    with tab1:
        st.subheader("Tasa de Actividad Promedio por Canal")
        if not df_filtered.empty and 'TIPO' in df_filtered.columns and 'Tasa_Actividad' in df_filtered.columns:
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
            if not df_canal.empty and 'Fecha' in df_canal.columns:
                evolucion_canal = df_canal.groupby('Fecha')['Tasa_Actividad'].mean().reset_index()
                line_canal = alt.Chart(evolucion_canal).mark_line(point=True, color='#10B981').encode(
                    x=alt.X('Fecha:T', title='Fecha de Envío'),
                    y=alt.Y('Tasa_Actividad:Q', axis=alt.Axis(format='%'), title='Tasa de Actividad Promedio'),
                    tooltip=['Fecha:T', alt.Tooltip('Tasa_Actividad', format='.2%', title='Actividad')]
                ).properties(height=250)
                st.altair_chart(line_canal, use_container_width=True)
        
    with tab2:
        st.subheader("Tasa de Actividad Promedio por Producto")
        if not df_filtered.empty and 'Producto' in df_filtered.columns and 'Tasa_Actividad' in df_filtered.columns:
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
            if not df_prod.empty and 'Fecha' in df_prod.columns:
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
    
    if 'Tasa_Actividad' in df_filtered.columns and 'Total de envíos' in df_filtered.columns:
        alertas_df = df_filtered[(df_filtered['Tasa_Actividad'] < 0.01) & (df_filtered['Total de envíos'] >= 500)]
        
        if not alertas_df.empty:
            st.warning(f"Se detectaron **{len(alertas_df)} envíos** masivos que generaron menos del 1% de actividad. Se sugiere pausar y reevaluar la segmentación.")
            alertas_df_clean = alertas_df.sort_values('Tasa_Actividad', ascending=True)
            if 'Fecha' in alertas_df_clean.columns:
                alertas_df_clean['Fecha'] = alertas_df_clean['Fecha'].dt.strftime('%Y-%m-%d')
                
            cols_alerta = ['Fecha', 'Campaña', 'Producto', 'TIPO', 'Total de envíos', 'Jugadores', 'Tasa_Actividad']
            cols_alerta_final = [c for c in cols_alerta if c in alertas_df_clean.columns]
            
            fmt_dict_alert = {'Tasa_Actividad': '{:.2%}', 'Total de envíos': '{:,.0f}', 'Jugadores': '{:,.0f}'}
            fmt_dict_alert = {k: v for k, v in fmt_dict_alert.items() if k in cols_alerta_final}
            
            st.dataframe(alertas_df_clean[cols_alerta_final].style.format(fmt_dict_alert), use_container_width=True)
        else:
            st.success("¡Excelente! No se encontraron campañas masivas con rendimiento inferior al 1.0% en este periodo.")
            
    st.divider()

    # ---------------------------------------------------------
    # SECCIÓN 6: Buscador y Top 10 Campañas Auditadas
    # ---------------------------------------------------------
    st.header("🏆 Top 10 Campañas (Por Actividad de Juego)")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        if 'Producto' in df_filtered.columns:
            f_producto = st.multiselect("Filtrar la tabla por Producto:", df_filtered['Producto'].dropna().unique())
        else: f_producto = []
    with col_f2:
        if 'TIPO' in df_filtered.columns:
            f_canal = st.multiselect("Filtrar la tabla por Canal:", df_filtered['TIPO'].dropna().unique())
        else: f_canal = []
        
    df_top = df_filtered.copy()
    if f_producto and 'Producto' in df_top.columns:
        df_top = df_top[df_top['Producto'].isin(f_producto)]
    if f_canal and 'TIPO' in df_top.columns:
        df_top = df_top[df_top['TIPO'].isin(f_canal)]
        
    if 'Total de envíos' in df_top.columns and 'Tasa_Actividad' in df_top.columns:
        top_10 = df_top[df_top['Total de envíos'] >= 500].sort_values('Tasa_Actividad', ascending=False).head(10)
        
        if 'Fecha' in top_10.columns:
            top_10['Fecha'] = top_10['Fecha'].dt.strftime('%Y-%m-%d')
        
        columnas_deseadas = ['Fecha', 'Campaña', 'Producto', 'TIPO', 'Mensaje_Texto', 'Total de envíos', 'Jugadores', 'Tasa_Actividad']
        columnas_finales = [col for col in columnas_deseadas if col in top_10.columns]
        
        formato_columnas = {
            'Tasa_Actividad': '{:.2%}',
            'Total de envíos': '{:,.0f}',
            'Jugadores': '{:,.0f}'
        }
        formato_final = {k: v for k, v in formato_columnas.items() if k in columnas_finales}
        
        st.dataframe(
            top_10[columnas_finales].style.format(formato_final),
            use_container_width=True
        )
