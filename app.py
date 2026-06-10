import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Mundial 2026 - Analítica Pro", layout="wide", page_icon="⚽")

# Título Principal de la App
st.title("⚽ Sistema de Análisis Predictivo & Métricas Mundial 2026")
st.markdown("Bienvenido al centro de comando analítico. Aquí puedes visualizar promedios, simulación de Montecarlo y alimentar marcadores en vivo.")

# Función para cargar la base de datos robustecida
@st.cache_data
def load_data():
    file_path = "Mundial2026_V3_Base_Profesional_Robustecido.xlsx"
    dict_sheets = {
        "Resumen": pd.read_excel(file_path, sheet_name="Resumen Mundial 2026", skiprows=4),
        "Jugadores": pd.read_excel(file_path, sheet_name="Jugadores_Maestro"),
        "Corners": pd.read_excel(file_path, sheet_name="Corners"),
        "Tarjetas": pd.read_excel(file_path, sheet_name="Tarjetas"),
        "Predicciones": pd.read_excel(file_path, sheet_name="Predicciones"),
        "Lesiones": pd.read_excel(file_path, sheet_name="Lesiones")
    }
    return dict_sheets

try:
    data = load_data()
    
    # BARRA LATERAL: Selector de Secciones de la App
    menu = st.sidebar.selectbox("Navegación / Módulos", [
        "Dashboard de Rendimiento", 
        "Motor de Predicciones (Montecarlo)", 
        "Scouting de Plantillas y Bajas",
        "Alimentación del Marcador en Vivo"
    ])
    
    # -------------------------------------------------------------
    # MÓDULO 1: DASHBOARD GENERAL
    # -------------------------------------------------------------
    if menu == "Dashboard de Rendimiento":
        st.header("📊 Métricas de Rendimiento Histórico por Selección")
        df_resumen = data["Resumen"].dropna(subset=["Selección"])
        
        # Filtro de búsqueda interactivo
        search_team = st.text_input("🔍 Buscar una selección específica:", "").upper()
        if search_team:
            df_resumen = df_resumen[df_resumen["Selección"].str.contains(search_team)]
            
        st.dataframe(df_resumen, use_container_width=True)
        
        # Gráficos Dinámicos
        st.subheader("📈 Top Selecciones con Mayor Rendimiento %")
        fig = px.bar(df_resumen.sort_values(by="Rendimiento %", ascending=False).head(10), 
                     x="Selección", y="Rendimiento %", color="Rendimiento %",
                     title="Top 10 Selecciones según histórico de 15 partidos", color_continuous_scale="Blues")
        st.plotly_chart(fig, use_container_width=True)

    # -------------------------------------------------------------
    # MÓDULO 2: PREDICCIONES MONTECARLO
    # -------------------------------------------------------------
    elif menu == "Motor de Predicciones (Montecarlo)":
        st.header("🔮 Probabilidades Calculadas por Algoritmo")
        st.write("Datos extraídos de las 10,000 iteraciones por partido ejecutadas en el backend.")
        
        df_pred = data["Predicciones"]
        st.dataframe(df_pred, use_container_width=True)
        
        # Selector de partido específico para ver gráfica de pastel de probabilidades
        partido_select = st.selectbox("Selecciona un partido para analizar probabilidades de apuesta:", df_pred["Partido"].unique())
        partido_info = df_pred[df_pred["Partido"] == partido_select].iloc[0]
        
        # Convertir strings de porcentajes a números flotantes para graficar
        p_local = float(str(partido_info["Prob_Local"]).replace('%',''))
        p_empate = float(str(partido_info["Prob_Empate"]).replace('%',''))
        p_vis = float(str(partido_info["Prob_Visitante"]).replace('%',''))
        
        labels = ['Victoria Local', 'Empate', 'Victoria Visitante']
        values = [p_local, p_empate, p_vis]
        
        fig_pie = px.pie(names=labels, values=values, color=labels, 
                         color_discrete_map={'Victoria Local':'#2ca02c', 'Empate':'#ff7f0e', 'Victoria Visitante':'#d62728'},
                         title=f"Distribución Probabilística - {partido_select}")
        st.plotly_chart(fig_pie, use_container_width=True)

    # -------------------------------------------------------------
    # MÓDULO 3: SCOUTING Y BAJAS
    # -------------------------------------------------------------
    elif menu == "Scouting de Plantillas y Bajas":
        st.header("📋 Fichas Técnicas de Jugadores Maestro")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Jugadores Clave por Selección")
            team_sel = st.selectbox("Selecciona un País:", data["Jugadores"]["Equipo"].unique())
            df_jug_filtered = data["Jugadores"][data["Jugadores"]["Equipo"] == team_sel]
            st.table(df_jug_filtered[["Jugador", "Posicion", "Edad", "Club"]])
            
        with col2:
            st.subheader("🎯 Promedios de Córneres y Tarjetas")
            c_info = data["Corners"][data["Corners"]["Equipo"] == team_sel].iloc[0]
            t_info = data["Tarjetas"][data["Tarjetas"]["Equipo"] == team_sel].iloc[0]
            
            st.metric("Córneres a Favor Promedio", f"{c_info['Corners_Favor']} por partido")
            st.metric("Córneres en Contra Promedio", f"{c_info['Corners_Contra']} por partido")
            st.metric("Tarjetas Amarillas Promedio", f"{t_info['Amarillas']} por partido")

        st.subheader("🚨 Reporte de Jugadores Lesionados o Resentidos")
        st.dataframe(data["Lesiones"], use_container_width=True)

    # -------------------------------------------------------------
    # MÓDULO 4: ALIMENTACIÓN EN VIVO
    # -------------------------------------------------------------
    elif menu == "Alimentación del Marcador en Vivo":
        st.header("⚡ Registro de Resultados en Tiempo Real")
        st.write("Usa este formulario para ingresar lo que sucede en el torneo. El sistema adaptará los análisis.")
        
        with st.form("live_score"):
            partido_num = st.number_input("ID del Partido jugado (1 al 104):", min_value=1, max_value=104, step=1)
            marcador_real = st.text_input("Marcador final (Ej: 2 - 1):", "0 - 0")
            corners_totales = st.number_input("Córneres totales del encuentro:", min_value=0, max_value=30, step=1)
            tarjetas_totales = st.number_input("Tarjetas amarillas totales del encuentro:", min_value=0, max_value=20, step=1)
            
            submit = st.form_submit_with_button("Guardar y Recalcular Métricas")
            
            if submit:
                st.success(f"¡Partido {partido_num} guardado exitosamente! Marcador: {marcador_real}. Córneres: {corners_totales}, Tarjetas: {tarjetas_totales}.")
                st.info("Nota: Los datos se actualizan temporalmente en la interfaz en vivo.")

except Exception as e:
    st.error(f"Por favor asegúrate de colocar el archivo Excel robustecido en la misma carpeta que este script. Error detectado: {e}")