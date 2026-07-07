import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Dashboard Loterías", layout="wide")
st.title("📊 Dashboard Loterías: Análisis Avanzado de Campañas")

# 1. Cargador de archivos
archivo_subido = st.file_uploader("Sube tu archivo Excel de resultados", type=["xlsx"])

if archivo_subido is not None:
    # 2. Leer la data y limpiar
    df = pd.read_excel(archivo_subido, sheet_name='Reporte_Nuevo')
    df = df.rename(columns={
        'Total:  Bonos entregados / Usaron Bonos': 'Bonos_Usados',
        'Fecha de Envío': 'Fecha'
    })
    
    # Limpieza de datos (fechas y números)
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    columnas_numericas = ['Total de envíos', 'Bonos_Usados', 'Tasa de efectividad']
    for col in columnas_numericas:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=['Total de envíos', 'Fecha'])
    
    # ---------------------------------------------------------
    # SECCIÓN 1: Filtro Global de Fechas
    # ---------------------------------------------------------
    st.sidebar.header("Filtros Globales")
    min_date = df['Fecha'].min().date()
    max_date = df['Fecha'].min().date() # Correcting min to max
    max_date = df['Fecha'].max().date()

    date_range = st.sidebar.date_input(
        "Selecciona el rango de fechas:",
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
    # SECCIÓN 2: Resumen Ejecutivo (Dinámico)
    # ---------------------------------------------------------
    st.header("Resumen Ejecutivo Dinámico")
    
    total_envios = df_filtered['Total de envíos'].sum()
    total_bonos = df_filtered['Bonos_Usados'].sum()
    tasa_efectividad_global = (total_bonos / total_envios) if total_envios > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Envíos", f"{total_envios:,.0f}")
    col2.metric("Bonos Redimidos", f"{total_bonos:,.0f}")
    col3.metric("Tasa Efectividad Prom.", f"{(tasa_efectividad_global * 100):.2f}%")
    
    # Texto de análisis dinámico
    st.info(f"**Análisis Ejecutivo:** En el periodo seleccionado, se gestionaron **{total_envios:,.0f} envíos**, logrando la redención de **{total_bonos:,.0f} bonos**. Esto representa una efectividad promedio ponderada del **{(tasa_efectividad_global * 100):.2f}%**. Evalúa las gráficas inferiores para detectar qué canal o producto impulsó este resultado.")
    st.divider()

    # ---------------------------------------------------------
    # SECCIÓN 3: Análisis por Canal y Producto (Con Drill-down)
    # ---------------------------------------------------------
    st.header("Rendimiento: Canales y Productos")
    
    tab1, tab2 = st.tabs(["Canales (TIPO)", "Productos"])
    
    with tab1:
        st.subheader("Efectividad Promedio por Canal")
        # Gráfico General
        canal_grp = df_filtered.groupby('TIPO')['Tasa de efectividad'].mean().reset_index()
        bar_canal = alt.Chart(canal_grp).mark_bar(color='#4F46E5').encode(
            x=alt.X('Tasa de efectividad:Q', axis=alt.Axis(format='%')),
            y=alt.Y('TIPO:N', sort='-x', title='Canal'),
            tooltip=[alt.Tooltip('TIPO', title='Canal'), alt.Tooltip('Tasa de efectividad', format='.2%')]
        ).properties(height=300)
        st.altair_chart(bar_canal, use_container_width=True)
        
        # Drill-down por fechas
        st.write("### Detalle por Fecha (Evolución del Canal)")
        canal_seleccionado = st.selectbox("Selecciona un canal para ver su evolución diaria:", df_filtered['TIPO'].dropna().unique())
        
        df_canal = df_filtered[df_filtered['TIPO'] == canal_seleccionado]
        evolucion_canal = df_canal.groupby('Fecha')['Tasa de efectividad'].mean().reset_index()
        
        line_canal = alt.Chart(evolucion_canal).mark_line(point=True, color='#10B981').encode(
            x=alt.X('Fecha:T', title='Fecha'),
            y=alt.Y('Tasa de efectividad:Q', axis=alt.Axis(format='%'), title='Efectividad Prom.'),
            tooltip=['Fecha:T', alt.Tooltip('Tasa de efectividad', format='.2%')]
        ).properties(height=300)
        st.altair_chart(line_canal, use_container_width=True)
        
    with tab2:
        st.subheader("Efectividad Promedio por Producto")
        # Gráfico General
        prod_grp = df_filtered.groupby('Producto')['Tasa de efectividad'].mean().reset_index()
        bar_prod = alt.Chart(prod_grp).mark_bar(color='#F59E0B').encode(
            x=alt.X('Tasa de efectividad:Q', axis=alt.Axis(format='%')),
            y=alt.Y('Producto:N', sort='-x', title='Producto'),
            tooltip=[alt.Tooltip('Producto', title='Producto'), alt.Tooltip('Tasa de efectividad', format='.2%')]
        ).properties(height=300)
        st.altair_chart(bar_prod, use_container_width=True)
        
        # Drill-down por fechas
        st.write("### Detalle por Fecha (Evolución del Producto)")
        prod_seleccionado = st.selectbox("Selecciona un producto para ver su evolución diaria:", df_filtered['Producto'].dropna().unique())
        
        df_prod = df_filtered[df_filtered['Producto'] == prod_seleccionado]
        evolucion_prod = df_prod.groupby('Fecha')['Tasa de efectividad'].mean().reset_index()
        
        line_prod = alt.Chart(evolucion_prod).mark_line(point=True, color='#EF4444').encode(
            x=alt.X('Fecha:T', title='Fecha'),
            y=alt.Y('Tasa de efectividad:Q', axis=alt.Axis(format='%'), title='Efectividad Prom.'),
            tooltip=['Fecha:T', alt.Tooltip('Tasa de efectividad', format='.2%')]
        ).properties(height=300)
        st.altair_chart(line_prod, use_container_width=True)

    st.divider()

    # ---------------------------------------------------------
    # SECCIÓN 4: Top 10 Campañas (Filtros Independientes)
    # ---------------------------------------------------------
    st.header("🏆 Top 10 Campañas")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        f_producto = st.multiselect("Filtrar por Producto:", df_filtered['Producto'].dropna().unique())
    with col_f2:
        f_canal = st.multiselect("Filtrar por Canal:", df_filtered['TIPO'].dropna().unique())
        
    # Aplicar filtros a la tabla
    df_top = df_filtered.copy()
    if f_producto:
        df_top = df_top[df_top['Producto'].isin(f_producto)]
    if f_canal:
        df_top = df_top[df_top['TIPO'].isin(f_canal)]
        
    # Obtener top 10 (con más de 1000 envíos para evitar sesgos de campañas muy pequeñas)
    top_10 = df_top[df_top['Total de envíos'] >= 1000].sort_values('Tasa de efectividad', ascending=False).head(10)
    
    # Formatear la fecha para que solo muestre YYYY-MM-DD
    top_10['Fecha'] = top_10['Fecha'].dt.strftime('%Y-%m-%d')
    
    st.dataframe(
        top_10[['Fecha', 'Campaña', 'Producto', 'TIPO', 'Total de envíos', 'Tasa de efectividad']].style.format({
            'Tasa de efectividad': '{:.2%}',
            'Total de envíos': '{:,.0f}'
        }),
        use_container_width=True
    )
```eof
¡Listo! He actualizado el código de tu archivo `app.py`. Para ver estos cambios, solo tienes que ir a tu repositorio de GitHub, editar el archivo como lo hicimos antes, y pegar este nuevo código.

Como analista, entiendo perfectamente lo que necesitas. Aquí te explico las mejoras clave que he implementado para subir el nivel del dashboard:

1. **Filtro Global y Resumen Ejecutivo:** Ahora tienes un panel lateral donde puedes seleccionar un rango de fechas. Las tarjetas de arriba ("Total Envíos", "Redimidos", etc.) y el texto resumen se recalcularán automáticamente según lo que selecciones, dándote el resumen ejecutivo que pediste.
2. **"Drill-down" por Fechas (Canales y Productos):** Streamlit (la tecnología que estamos usando) no permite hacer "clic" dentro de un gráfico de barras básico. *Sin embargo*, resolví esto usando selectores desplegables justos debajo del gráfico de barras general. Ahora verás una barra general por Canal, y debajo podrás seleccionar "WHATSAPP" (por ejemplo) para ver un **gráfico de líneas** con su rendimiento exacto día a día. Lo mismo aplica para los productos.
3. **El Top 10 con Filtros:** La tabla final ahora muestra el Top 10 de campañas. He añadido la columna de Fecha y le he puesto dos filtros interactivos exclusivos para esa tabla (Producto y Canal). Así puedes responder preguntas como: *"¿Cuáles son las top 10 mejores campañas de Tinka enviadas solo por SMS en este rango de fechas?"*.

Pruébalo copiando este nuevo código a tu GitHub y cuéntame qué te parece la nueva interfaz.
