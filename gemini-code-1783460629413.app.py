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
    tasa_act
