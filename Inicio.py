import streamlit as st
import pandas as pd
import plotly.express as px

def main():
    st.set_page_config(page_title="Análisis de Datos", page_icon="📊")
    
    st.title("Proyecto Final: Análisis de Datos")
    st.subheader("Daniela Monge")
    
    st.markdown("""
    ## Introducción
    
    El siguiente dashboard presenta un análisis detallado como parte del proyecto final del curso.
                
    ### Objetivo del Proyecto
    Realizar un análisis exhaustivo utilizando técnicas de visualización de datos 
    y análisis estadístico para obtener insights significativos.
    
    ### Metodología
    - Recolección de datos
    - Limpieza y preparación 
    - Análisis exploratorio
    - Visualización de resultados
    """)
    
    # Información del proyecto
    st.sidebar.header("Daniela Monge")
    st.sidebar.info("Proyecto Final | Curso de Análisis de Datos 2024")

if __name__ == "__main__":
    main()