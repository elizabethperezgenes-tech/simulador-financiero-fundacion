
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Simulador Financiero",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Simulador Financiero")
st.subheader("Fundación Amigos de la Salud - Montería")

st.markdown("""
Esta herramienta permite analizar el comportamiento financiero
y proyectar escenarios mediante supuestos modificables.
""")

st.divider()

st.header("1. Datos financieros de referencia")

st.info(
    "Ingresa los valores del periodo base en millones de pesos colombianos. "
    "Utilizaremos los estados financieros históricos para alimentar "
    "el modelo econométrico en una siguiente etapa."
)

col1, col2 = st.columns(2)

with col1:
    ingresos = st.number_input(
        "Ingresos del periodo base (millones COP)",
        min_value=0.0,
        value=0.0
    )

    costos = st.number_input(
        "Costos del periodo base (millones COP)",
        min_value=0.0,
        value=0.0
    )

with col2:
    gastos = st.number_input(
        "Gastos del periodo base (millones COP)",
        min_value=0.0,
        value=0.0
    )

    otros_gastos = st.number_input(
        "Otros gastos del periodo base (millones COP)",
        min_value=0.0,
        value=0.0
    )

st.divider()

st.header("2. Configuración de escenarios")

col3, col4 = st.columns(2)

with col3:
    crecimiento = st.slider(
        "Crecimiento esperado de ingresos (%)",
        min_value=-20,
        max_value=50,
        value=5
    )

    aumento_costos = st.slider(
        "Variación esperada de costos (%)",
        min_value=-20,
        max_value=50,
        value=5
    )

with col4:
    aumento_gastos = st.slider(
        "Variación esperada de gastos (%)",
        min_value=-20,
        max_value=50,
        value=3
    )

    periodos = st.selectbox(
        "Años de proyección",
        [1, 2, 3, 4, 5]
    )

st.divider()

st.header("3. Resultados de la simulación")

if ingresos > 0 and costos > 0:

    resultados = []

    for anio in range(1, periodos + 1):

        ingreso_proyectado = ingresos * (
            1 + crecimiento / 100
        ) ** anio

        costo_proyectado = costos * (
            1 + aumento_costos / 100
        ) ** anio

        gasto_proyectado = gastos * (
            1 + aumento_gastos / 100
        ) ** anio

        otros_proyectados = otros_gastos * (
            1 + aumento_gastos / 100
        ) ** anio

        excedente = (
            ingreso_proyectado
            - costo_proyectado
            - gasto_proyectado
            - otros_proyectados
        )

        resultados.append({
            "Año proyectado": anio,
            "Ingresos": ingreso_proyectado,
            "Costos": costo_proyectado,
            "Gastos": gasto_proyectado,
            "Otros gastos": otros_proyectados,
            "Excedente estimado": excedente
        })

    df = pd.DataFrame(resultados)

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Ingresos proyectados",
        f"$ {df.iloc[-1]['Ingresos']:,.2f} millones"
    )

    c2.metric(
        "Costos proyectados",
        f"$ {df.iloc[-1]['Costos']:,.2f} millones"
    )

    c3.metric(
        "Excedente estimado",
        f"$ {df.iloc[-1]['Excedente estimado']:,.2f} millones"
    )

    st.subheader("Proyección financiera")

    st.dataframe(
        df.style.format({
            "Ingresos": "{:,.2f}",
            "Costos": "{:,.2f}",
            "Gastos": "{:,.2f}",
            "Otros gastos": "{:,.2f}",
            "Excedente estimado": "{:,.2f}"
        }),
        use_container_width=True
    )

    grafico = px.line(
        df,
        x="Año proyectado",
        y=["Ingresos", "Costos", "Excedente estimado"],
        markers=True,
        title="Evolución financiera proyectada"
    )

    st.plotly_chart(grafico, use_container_width=True)

    st.download_button(
        "Descargar resultados en CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="proyeccion_financiera.csv",
        mime="text/csv"
    )

else:
    st.warning(
        "Ingresa los ingresos y costos del periodo base "
        "para generar la simulación."
    )

st.divider()

st.caption(
    "Proyecto académico | Fundación Amigos de la Salud | Montería, Colombia"
)
