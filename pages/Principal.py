import pandas as pd
import sqlite3
import plotly.express as px
import streamlit as st
from datetime import datetime

# Configuración de página con un diseño más profesional
st.set_page_config(
    page_title="Dashboard de Ventas", 
    layout="wide", 
    page_icon="📊"
)

# Paleta de colores profesional
COLOR_PRIMARY = '#2C3E50'  # Azul grisáceo oscuro
COLOR_SECONDARY = '#34495E'  # Azul grisáceo
COLOR_ACCENT = '#3498DB'  # Azul claro
COLOR_BACKGROUND = '#ECF0F1'  # Gris muy claro

# Estilo personalizado
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {COLOR_BACKGROUND};
        color: {COLOR_PRIMARY};
    }}
    .stTitle {{
        color: {COLOR_PRIMARY};
        font-weight: bold;
    }}
    .stSubheader {{
        color: {COLOR_SECONDARY};
    }}
    </style>
""", unsafe_allow_html=True)

# Título del dashboard con estilo
st.title("📊 Panel de Análisis de Ventas")
st.markdown("---")

# Conexión a la base de datos
@st.cache_data
def load_data():
    conn = sqlite3.connect("data/Northwind_small.sqlite")
    
    # Query: Datos de ventas con fecha
    query_sales = """
    SELECT 
        c.Country, 
        strftime('%Y-%m-%d', o.OrderDate) AS OrderDate,
        od.UnitPrice * od.Quantity AS Sales,
        p.ProductName
    FROM [Order] o
    JOIN Customer c ON o.CustomerId = c.Id
    JOIN OrderDetail od ON o.Id = od.OrderId
    JOIN Product p ON od.ProductId = p.Id
    """
    sales_data = pd.read_sql_query(query_sales, conn)
    sales_data['OrderDate'] = pd.to_datetime(sales_data['OrderDate'])

    # Query: Ventas por país
    query_sales_by_country = """
    SELECT c.Country, SUM(od.UnitPrice * od.Quantity) AS TotalSales
    FROM [Order] o
    JOIN Customer c ON o.CustomerId = c.Id
    JOIN OrderDetail od ON o.Id = od.OrderId
    GROUP BY c.Country
    ORDER BY TotalSales DESC;
    """
    sales_by_country = pd.read_sql_query(query_sales_by_country, conn)

    # Query: Productos más vendidos
    query_top_products = """
    SELECT p.ProductName, SUM(od.Quantity) AS TotalQuantity
    FROM Product p
    JOIN OrderDetail od ON p.Id = od.ProductId
    GROUP BY p.ProductName
    ORDER BY TotalQuantity DESC
    LIMIT 10;
    """
    top_products = pd.read_sql_query(query_top_products, conn)

    # Query: Ventas mensuales
    query_monthly_sales = """
    SELECT strftime('%Y-%m', o.OrderDate) AS OrderMonth, 
           SUM(od.UnitPrice * od.Quantity) AS TotalSales
    FROM [Order] o
    JOIN OrderDetail od ON o.Id = od.OrderId
    GROUP BY OrderMonth
    ORDER BY OrderMonth;
    """
    monthly_sales = pd.read_sql_query(query_monthly_sales, conn)

    conn.close()
    return sales_data, sales_by_country, top_products, monthly_sales

# Cargar datos
sales_data, sales_by_country, top_products, monthly_sales = load_data()

# Sidebar con diseño mejorado
st.sidebar.header("🔍 Filtros de Análisis")
st.sidebar.markdown("---")

# Rango de fechas
min_date = sales_data['OrderDate'].min()
max_date = sales_data['OrderDate'].max()

date_range = st.sidebar.date_input(
    "Selecciona Rango de Fechas:", 
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    help="Filtra los datos por un rango de fechas específico"
)

# Filtros interactivos de país
selected_country = st.sidebar.multiselect(
    "Selecciona País(es):", 
    options=sales_by_country["Country"].unique(), 
    default=sales_by_country["Country"].unique(),
    help="Elige los países para filtrar el análisis de ventas"
)

# Filtros de productos
selected_products = st.sidebar.multiselect(
    "Selecciona Producto(s):", 
    options=sales_data["ProductName"].unique(), 
    help="Filtra por productos específicos"
)

# Aplicar filtros
filtered_sales = sales_data[
    (sales_data['OrderDate'].dt.date >= date_range[0]) & 
    (sales_data['OrderDate'].dt.date <= date_range[1]) &
    (sales_data['Country'].isin(selected_country))
]

# Si hay selección de productos, filtrar adicional
if selected_products:
    filtered_sales = filtered_sales[filtered_sales['ProductName'].isin(selected_products)]

# Preparar datos filtrados para gráficos
filtered_sales_by_country = filtered_sales.groupby('Country')['Sales'].sum().reset_index()
filtered_monthly_sales = filtered_sales.groupby(filtered_sales['OrderDate'].dt.to_period('M'))['Sales'].sum().reset_index()
filtered_monthly_sales['OrderMonth'] = filtered_monthly_sales['OrderDate'].astype(str)

filtered_top_products = filtered_sales.groupby('ProductName')['Sales'].sum().reset_index().nlargest(10, 'Sales')

# Diseño del Dashboard con columnas
col1, col2 = st.columns(2)

# Gráfico 1: Ventas por país
with col1:
    st.subheader("🌍 Ventas Totales por País")
    if not filtered_sales_by_country.empty:
        fig1 = px.bar(
            filtered_sales_by_country, 
            x="Country", 
            y="Sales", 
            title="Distribución de Ventas por País",
            labels={"Country": "País", "Sales": "Ventas Totales"},
            color_discrete_sequence=[COLOR_ACCENT]
        )
        fig1.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.warning("No hay datos para mostrar con los filtros actuales")

# Gráfico 2: Productos más vendidos
with col2:
    st.subheader("📦 Productos Más Vendidos")
    if not filtered_top_products.empty:
        fig2 = px.bar(
            filtered_top_products, 
            x="ProductName", 
            y="Sales", 
            title="Top Productos en Ventas",
            labels={"ProductName": "Producto", "Sales": "Ventas Totales"},
            color_discrete_sequence=[COLOR_SECONDARY]
        )
        fig2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("No hay datos para mostrar con los filtros actuales")

# Gráfico 3: Ventas mensuales
st.subheader("📈 Tendencia de Ventas Mensuales")
if not filtered_monthly_sales.empty:
    fig3 = px.line(
        filtered_monthly_sales, 
        x="OrderMonth", 
        y="Sales", 
        title="Evolución de Ventas Mensuales",
        labels={"OrderMonth": "Mes", "Sales": "Ventas Totales"},
        color_discrete_sequence=[COLOR_PRIMARY]
    )
    fig3.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.warning("No hay datos para mostrar con los filtros actuales")

# Sección de información adicional
st.markdown("---")
st.info(f"""
🔬 **Insights del Dashboard:**
- Período seleccionado: {date_range[0]} a {date_range[1]}
- Países analizados: {', '.join(selected_country)}
- Productos específicos: {', '.join(selected_products) if selected_products else 'Todos'}
""")