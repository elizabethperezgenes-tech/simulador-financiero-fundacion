
import streamlit as st
import pandas as pd
import plotly.express as px
import statsmodels.api as sm

st.set_page_config(
    page_title="Simulador Financiero",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Simulador Financiero")
st.subheader("Fundación Amigos de la Salud - Montería")

st.markdown("""
**Herramienta de análisis financiero y simulación de escenarios**
basada en información histórica y un modelo econométrico.
""")

# Cargar base de datos
@st.cache_data
def cargar_datos():
    return pd.read_csv("datos/estados_financieros.csv")

try:
    df = cargar_datos()
except Exception as e:
    st.error(f"No se pudo cargar la base de datos: {e}")
    st.stop()

df = df.sort_values("anio").reset_index(drop=True)

# Menú de navegación
tab1, tab2, tab3, tab4 = st.tabs([
    "Diagnóstico histórico",
    "Indicadores financieros",
    "Modelo econométrico",
    "Simulador de escenarios"
])

# --------------------------------------------------
# 1. DIAGNÓSTICO HISTÓRICO
# --------------------------------------------------

with tab1:
    st.header("Diagnóstico financiero histórico")

    st.write(
        "Información financiera expresada en millones de pesos colombianos."
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    fig = px.line(
        df,
        x="anio",
        y=["ingresos", "costos"],
        markers=True,
        title="Evolución de ingresos y costos"
    )
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.bar(
        df,
        x="anio",
        y="excedente_neto",
        title="Excedente neto histórico"
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.download_button(
        "Descargar base histórica",
        df.to_csv(index=False).encode("utf-8"),
        "estados_financieros.csv",
        "text/csv"
    )

# --------------------------------------------------
# 2. INDICADORES FINANCIEROS
# --------------------------------------------------

with tab2:
    st.header("Indicadores financieros")

    datos = df.dropna(subset=[
        "activos_totales",
        "pasivos_totales"
    ]).copy()

    datos["endeudamiento"] = (
        datos["pasivos_totales"] /
        datos["activos_totales"] * 100
    )

    datos["participacion_cartera"] = (
        datos["cuentas_por_cobrar"] /
        datos["activos_corrientes"] * 100
    )

    datos["participacion_efectivo"] = (
        datos["efectivo"] /
        datos["activos_corrientes"] * 100
    )

    datos["margen_neto"] = (
        datos["excedente_neto"] /
        datos["ingresos"] * 100
    )

    st.subheader("Evolución de indicadores")

    indicadores = st.selectbox(
        "Selecciona el indicador",
        [
            "endeudamiento",
            "participacion_cartera",
            "participacion_efectivo",
            "margen_neto"
        ],
        format_func=lambda x: {
            "endeudamiento": "Endeudamiento (%)",
            "participacion_cartera": "Cartera sobre activos corrientes (%)",
            "participacion_efectivo": "Efectivo sobre activos corrientes (%)",
            "margen_neto": "Margen neto (%)"
        }[x]
    )

    grafico = px.line(
        datos,
        x="anio",
        y=indicadores,
        markers=True,
        title="Comportamiento del indicador seleccionado"
    )

    st.plotly_chart(grafico, use_container_width=True)

    st.dataframe(
        datos[[
            "anio",
            "endeudamiento",
            "participacion_cartera",
            "participacion_efectivo",
            "margen_neto"
        ]].style.format("{:.2f}"),
        use_container_width=True
    )

    st.info(
        "La razón corriente no se calcula porque no tenemos "
        "identificados los pasivos corrientes. La participación "
        "del efectivo y de la cartera se expresa sobre los activos corrientes."
    )

# --------------------------------------------------
# 3. MODELO ECONOMÉTRICO
# --------------------------------------------------

with tab3:
    st.header("Modelo econométrico")

    st.markdown("""
    **Modelo de regresión lineal simple**

    Variable dependiente: costos.

    Variable independiente: ingresos.

    Ecuación: Costos = β₀ + β₁(Ingresos) + ε
    """)

    modelo_df = df.dropna(
        subset=["ingresos", "costos"]
    ).copy()

    if len(modelo_df) >= 3:
        X = sm.add_constant(modelo_df["ingresos"])
        y = modelo_df["costos"]

        modelo = sm.OLS(y, X).fit()

        st.subheader("Resultados de la estimación")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Observaciones",
            len(modelo_df)
        )

        col2.metric(
            "R²",
            f"{modelo.rsquared:.4f}"
        )

        col3.metric(
            "Coeficiente β₁",
            f"{modelo.params.iloc[1]:.4f}"
        )

        st.write("**Coeficientes estimados**")
        st.dataframe(
            pd.DataFrame({
                "Parámetro": ["Intercepto (β₀)", "Ingresos (β₁)"],
                "Estimación": modelo.params.values
            }),
            hide_index=True
        )

        predicciones = modelo.predict(X)

        comparacion = pd.DataFrame({
            "Año": modelo_df["anio"],
            "Costos reales": y,
            "Costos estimados": predicciones
        })

        fig = px.scatter(
            comparacion,
            x="Costos reales",
            y="Costos estimados",
            text="Año",
            title="Costos reales frente a costos estimados"
        )

        st.plotly_chart(fig, use_container_width=True)

        with st.expander("Ver resultados estadísticos completos"):
            st.text(modelo.summary().as_text())

        st.warning(
            "La estimación es exploratoria: se basa en una muestra "
            "muy pequeña. El R² no demuestra causalidad ni garantiza "
            "la precisión de las proyecciones."
        )

    else:
        st.error("No hay suficientes observaciones para estimar el modelo.")

# --------------------------------------------------
# 4. SIMULADOR DE ESCENARIOS
# --------------------------------------------------

with tab4:
    st.header("Simulador de escenarios financieros")

    modelo_df = df.dropna(
        subset=["ingresos", "costos"]
    ).copy()

    if len(modelo_df) >= 3:

        X = sm.add_constant(modelo_df["ingresos"])
        y = modelo_df["costos"]
        modelo = sm.OLS(y, X).fit()

        base = df.dropna(
            subset=["ingresos", "costos"]
        ).iloc[-1]

        st.write(
            f"Periodo base: **{int(base['anio'])}**"
        )

        col1, col2 = st.columns(2)

        with col1:
            crecimiento = st.slider(
                "Crecimiento anual de ingresos (%)",
                -20, 50, 5
            )

            aumento_gastos = st.slider(
                "Variación anual de gastos (%)",
                -20, 50, 3
            )

        with col2:
            periodos = st.selectbox(
                "Horizonte de proyección",
                [1, 2, 3, 4, 5]
            )

            escenario = st.selectbox(
                "Escenario",
                ["Personalizado", "Optimista", "Moderado", "Pesimista"]
            )

        if escenario == "Optimista":
            crecimiento = 10
            aumento_gastos = 2
        elif escenario == "Moderado":
            crecimiento = 5
            aumento_gastos = 3
        elif escenario == "Pesimista":
            crecimiento = -5
            aumento_gastos = 8

        st.write(
            f"Supuestos aplicados: ingresos {crecimiento}% y "
            f"gastos {aumento_gastos}% anual."
        )

        # Gastos de referencia del último año disponible
        admin = base["gastos_administrativos"]
        operativo = base["gastos_operativos"]
        financiero = base["gastos_financieros"]
        otros = base["otros_gastos"]

        gastos_base = sum(
            0 if pd.isna(v) else v
            for v in [admin, operativo, financiero, otros]
        )

        resultados = []

        for anio in range(1, periodos + 1):

            ingreso = base["ingresos"] * (
                1 + crecimiento / 100
            ) ** anio

            costo = float(
                modelo.predict(
                    pd.DataFrame({
                        "const": [1],
                        "ingresos": [ingreso]
                    })[["const", "ingresos"]]
                ).iloc[0]
            )

            gasto = gastos_base * (
                1 + aumento_gastos / 100
            ) ** anio

            excedente_bruto = ingreso - costo
            excedente_estimado = excedente_bruto - gasto

            resultados.append({
                "Año proyectado": int(base["anio"]) + anio,
                "Ingresos": ingreso,
                "Costos estimados": costo,
                "Excedente bruto": excedente_bruto,
                "Gastos estimados": gasto,
                "Excedente estimado": excedente_estimado
            })

        proyeccion = pd.DataFrame(resultados)

        st.subheader("Resultados de la simulación")

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Ingresos proyectados",
            f"$ {proyeccion.iloc[-1]['Ingresos']:,.2f} millones"
        )

        c2.metric(
            "Costos estimados",
            f"$ {proyeccion.iloc[-1]['Costos estimados']:,.2f} millones"
        )

        c3.metric(
            "Excedente estimado",
            f"$ {proyeccion.iloc[-1]['Excedente estimado']:,.2f} millones"
        )

        st.dataframe(
            proyeccion.style.format({
                columna: "{:,.2f}"
                for columna in proyeccion.select_dtypes(
                    include="number"
                ).columns
            }),
            use_container_width=True
        )

        grafico = px.line(
            proyeccion,
            x="Año proyectado",
            y=[
                "Ingresos",
                "Costos estimados",
                "Excedente estimado"
            ],
            markers=True,
            title="Proyección financiera"
        )

        st.plotly_chart(grafico, use_container_width=True)

        st.download_button(
            "Descargar proyección",
            proyeccion.to_csv(index=False).encode("utf-8"),
            "proyeccion_financiera.csv",
            "text/csv"
        )

        st.caption(
            "Las proyecciones son estimaciones exploratorias. "
            "Los gastos se proyectan aplicando una tasa constante "
            "al gasto agregado del último periodo disponible."
        )

    else:
        st.error("No hay datos suficientes para simular escenarios.")

st.divider()

st.caption(
    "Proyecto académico | Fundación Amigos de la Salud | Montería, Colombia"
)
