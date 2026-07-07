import streamlit as st
import pandas as pd

st.title("📊 Dashboard Loterías: Análisis de Campañas")

# 1. Cargador de archivos (Aquí subes tu Excel)
archivo_subido = st.file_uploader("Sube tu archivo Excel de resultados", type=["xlsx"])

if archivo_subido is not None:
    # 2. Leer la data
    df = pd.read_excel(archivo_subido, sheet_name='Reporte_Nuevo')
    df = df.rename(columns={'Total:  Bonos entregados / Usaron Bonos': 'Bonos_Usados'})
    
    # 3. KPIs Ejecutivos
    st.header("Resumen Ejecutivo")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Envíos", f"{df['Total de envíos'].sum():,.0f}")
    col2.metric("Bonos Redimidos", f"{df['Bonos_Usados'].sum():,.0f}")
    col3.metric("Tasa Efectividad Prom.", f"{(df['Tasa de efectividad'].mean() * 100):.2f}%")
    
    # 4. Análisis por Canal (TIPO)
    st.subheader("Rendimiento por Canal")
    canal_grp = df.groupby('TIPO')['Tasa de efectividad'].mean().sort_values(ascending=False) * 100
    st.bar_chart(canal_grp)
    
    # 5. Top Campañas
    st.subheader("🏆 Top 5 Campañas Exitosas")
    top_camps = df[df['Total de envíos'] > 1000].sort_values('Tasa de efectividad', ascending=False).head(5)
    st.dataframe(top_camps[['Campaña', 'Producto', 'TIPO', 'Tasa de efectividad']])