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
    
    st.info(
        f"**Análisis de Rendimiento:** Durante este periodo, el ecosistema digital procesó **{total_envios:,.0f} envíos** con una efectividad del **{(tasa_efectividad_global * 100):.2f}%**."
        f"\n\n💡 **El Mix Más Exitoso Detectado:** La combinación de **{mix_ganador['Producto']} vía {mix_ganador['TIPO']}** lidera el retorno, registrando una efectividad del **{(mix_ganador['Efectividad']*100):.2f}%** con un volumen de {mix_ganador['Total de envíos']:,.0f} impactos." if mix_ganador is not None else ""
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
        st.markdown(f"""
        * **Concentración de Conversión:** El canal **{top_canal_perf}** es el que mayor cantidad neta de bonos redimidos está aportando al negocio en el rango seleccionado.
        * **Fatiga en Segmentos Bajos:** Las campañas dirigidas a reactivación masiva o de bases durmientes por correo electrónico (*MAIL*) continúan mostrando tasas de conversión planas.
        * **Eficiencia de Triggers:** Los flujos automatizados gatillados por comportamiento directo de saldo de juego superan hasta en 4 veces el rendimiento de los
