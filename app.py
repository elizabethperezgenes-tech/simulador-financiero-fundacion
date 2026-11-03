
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
# --------------------------------------------------
# INDICADORES FINANCIEROS
# --------------------------------------------------

with tab2:
    st.header("Indicadores financieros")

    datos = df.dropna(subset=[
        "activos_totales",
        "pasivos_totales",
        "activos_corrientes",
        "efectivo",
        "ingresos",
        "excedente_neto"
    ]).copy()

    datos["anio"] = pd.to_numeric(datos["anio"], errors="coerce")

    # 1. Indicadores de endeudamiento y rentabilidad
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

    # 2. Indicadores de liquidez
    # Se excluye 2020 porque no tenemos identificado
    # el pasivo corriente de ese año.

    datos["pasivos_base_liquidez"] = float("nan")

    mascara_liquidez = datos["anio"] >= 2022

    datos.loc[mascara_liquidez, "pasivos_base_liquidez"] = (
        datos.loc[mascara_liquidez, "pasivos_totales"]
    )

    datos["razon_corriente"] = (
        datos["activos_corrientes"] /
        datos["pasivos_base_liquidez"]
    )

    datos["prueba_acida"] = (
        (datos["activos_corrientes"] - datos["inventarios"]) /
        datos["pasivos_base_liquidez"]
    )

    datos["razon_efectivo"] = (
        datos["efectivo"] /
        datos["pasivos_base_liquidez"]
    )

    datos["capital_trabajo"] = (
        datos["activos_corrientes"] -
        datos["pasivos_base_liquidez"]
    )

    # 3. Selector de indicadores
    st.subheader("Evolución de indicadores")

    opciones = {
        "endeudamiento": "Endeudamiento (%)",
        "participacion_cartera": "Cartera sobre activos corrientes (%)",
        "participacion_efectivo": "Efectivo sobre activos corrientes (%)",
        "margen_neto": "Margen neto (%)",
        "razon_corriente": "Razón corriente (veces)",
        "prueba_acida": "Prueba ácida (veces)",
        "razon_efectivo": "Razón de efectivo (veces)",
        "capital_trabajo": "Capital de trabajo (millones COP)"
    }

    indicador = st.selectbox(
        "Selecciona el indicador",
        list(opciones.keys()),
        format_func=lambda x: opciones[x]
    )

    # 4. Gráfico
    grafico = px.line(
        datos,
        x="anio",
        y=indicador,
        markers=True,
        title=opciones[indicador]
    )

    grafico.update_layout(
        xaxis_title="Año",
        yaxis_title=opciones[indicador]
    )

    st.plotly_chart(grafico, use_container_width=True)

    # 5. Tabla de indicadores
    st.subheader("Tabla histórica de indicadores")

    columnas = [
        "anio",
        "endeudamiento",
        "participacion_cartera",
        "participacion_efectivo",
        "margen_neto",
        "razon_corriente",
        "prueba_acida",
        "razon_efectivo",
        "capital_trabajo"
    ]

    tabla = datos[columnas].copy()

    tabla.columns = [
        "Año",
        "Endeudamiento (%)",
        "Cartera / Activo corriente (%)",
        "Efectivo / Activo corriente (%)",
        "Margen neto (%)",
        "Razón corriente",
        "Prueba ácida",
        "Razón de efectivo",
        "Capital de trabajo (millones)"
    ]

    st.dataframe(
        tabla.style.format({
            "Endeudamiento (%)": "{:.2f}",
            "Cartera / Activo corriente (%)": "{:.2f}",
            "Efectivo / Activo corriente (%)": "{:.2f}",
            "Margen neto (%)": "{:.2f}",
            "Razón corriente": "{:.2f}",
            "Prueba ácida": "{:.2f}",
            "Razón de efectivo": "{:.4f}",
            "Capital de trabajo (millones)": "{:,.2f}"
        }, na_rep="No disponible"),
        use_container_width=True
    )

    # 6. Aclaración metodológica
    st.warning(
        "Nota metodológica: para 2022 y 2023 se utiliza el pasivo "
        "de corto plazo reportado en los estados financieros. "
        "Para 2024 y 2025 se utiliza el pasivo total como aproximación, "
        "ya que los estados financieros no presentan una separación "
        "explícita entre pasivos corrientes y no corrientes. "
        "Por esta razón, los indicadores de liquidez de estos dos años "
        "son aproximados. El año 2020 se excluye de estos indicadores "
        "por no contar con una clasificación verificable del pasivo."
    )

# --------------------------------------------------

# --------------------------------------------------
# 3. MODELO ECONOMÉTRICO
# --------------------------------------------------

with tab3:
    st.header("Modelo econométrico")

    st.markdown("""
    **Modelo de regresión lineal simple**

    Variable dependiente: costos.

    Variable independiente: ingresos.

    Método de estimación: mínimos cuadrados ordinarios (MCO).
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

        st.divider()

        st.subheader("Coeficientes estimados")

        tabla_coef = pd.DataFrame({
            "Parámetro": modelo.params.index,
            "Coeficiente": modelo.params.values,
            "Error estándar": modelo.bse.values,
            "Estadístico t": modelo.tvalues.values,
            "Valor p": modelo.pvalues.values,
            "IC inferior 95%": modelo.conf_int()[0].values,
            "IC superior 95%": modelo.conf_int()[1].values
        })

        st.dataframe(
            tabla_coef.style.format({
                "Coeficiente": "{:,.4f}",
                "Error estándar": "{:,.4f}",
                "Estadístico t": "{:,.4f}",
                "Valor p": "{:.4f}",
                "IC inferior 95%": "{:,.4f}",
                "IC superior 95%": "{:,.4f}"
            }),
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Ecuación estimada")

        beta0 = modelo.params.iloc[0]
        beta1 = modelo.params.iloc[1]

        st.latex(
            rf"\widehat{{Costos}} = {beta0:,.2f} "
            rf"+ {beta1:.4f}(Ingresos)"
        )

        st.divider()

        st.subheader("Valores reales frente a estimados")

        predicciones = modelo.predict(X)
        residuos = modelo.resid

        comparacion = pd.DataFrame({
            "Año": modelo_df["anio"],
            "Costos reales": y.values,
            "Costos estimados": predicciones.values
        })

        fig = px.scatter(
            comparacion,
            x="Costos reales",
            y="Costos estimados",
            text="Año",
            title="Costos reales frente a costos estimados"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.subheader("Análisis de residuos")

        residuos_df = pd.DataFrame({
            "Año": modelo_df["anio"],
            "Residuo": residuos.values,
            "Valor estimado": predicciones.values
        })

        fig_residuos = px.scatter(
            residuos_df,
            x="Valor estimado",
            y="Residuo",
            text="Año",
            title="Distribución de los residuos"
        )

        fig_residuos.add_hline(y=0)

        st.plotly_chart(
            fig_residuos,
            use_container_width=True
        )

        st.dataframe(
            residuos_df.style.format({
                "Residuo": "{:,.4f}",
                "Valor estimado": "{:,.4f}"
            }),
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Indicadores de diagnóstico")

        col4, col5 = st.columns(2)

        col4.metric(
            "Error estándar de la regresión",
            f"{modelo.mse_resid ** 0.5:,.2f}"
        )

        col5.metric(
            "Durbin-Watson",
            f"{sm.stats.stattools.durbin_watson(residuos):.4f}"
        )

        with st.expander("Ver resumen estadístico completo"):
            st.text(modelo.summary().as_text())

        st.warning("""
        **Limitación metodológica:** la estimación utiliza cinco
        observaciones anuales. Por tanto, los valores p, los intervalos
        de confianza y las pruebas de diagnóstico deben interpretarse
        con mucha cautela. No permiten establecer conclusiones
        estadísticas sólidas con una muestra tan pequeña.
        """)

    else:
        st.error(
            "No existen suficientes observaciones para estimar el modelo."
        )


# --------------------------------------------------

# --------------------------------------------------
# 4. SIMULADOR DE ESCENARIOS
# --------------------------------------------------

with tab4:
    st.header("Simulador de escenarios financieros")

    modelo_df = df.dropna(
        subset=["ingresos", "costos"]
    ).copy()

    if len(modelo_df) >= 3:

        # Estimación econométrica
        X = sm.add_constant(modelo_df["ingresos"])
        y = modelo_df["costos"]
        modelo = sm.OLS(y, X).fit()

        base = modelo_df.sort_values("anio").iloc[-1]

        st.write(
            f"Periodo financiero base: **{int(base['anio'])}**"
        )

        st.markdown(
            "Modifica los supuestos para observar cómo "
            "podrían evolucionar los resultados financieros."
        )

        # Selección de escenario
        escenario = st.selectbox(
            "Selecciona el escenario",
            ["Personalizado", "Optimista", "Moderado", "Pesimista"]
        )

        supuestos = {
            "Optimista": {
                "crecimiento": 10,
                "gastos": 2,
                "cartera": 10
            },
            "Moderado": {
                "crecimiento": 5,
                "gastos": 3,
                "cartera": 5
            },
            "Pesimista": {
                "crecimiento": -5,
                "gastos": 8,
                "cartera": 0
            },
            "Personalizado": {
                "crecimiento": 5,
                "gastos": 3,
                "cartera": 5
            }
        }

        valores = supuestos[escenario]

        col1, col2 = st.columns(2)

        with col1:
            crecimiento = st.slider(
                "Variación anual de ingresos (%)",
                -20, 50,
                valores["crecimiento"]
            )

            aumento_gastos = st.slider(
                "Variación anual de gastos (%)",
                -20, 50,
                valores["gastos"]
            )

        with col2:
            mejora_cartera = st.slider(
                "Reducción anual de cuentas por cobrar (%)",
                0, 30,
                valores["cartera"]
            )

            periodos = st.selectbox(
                "Horizonte de proyección (años)",
                [1, 2, 3, 4, 5],
                index=1
            )

        st.divider()

        # Valores financieros de referencia
        def obtener_valor(columna):
            valor = base.get(columna, 0)
            return float(valor) if pd.notna(valor) else 0.0

        ingresos_base = obtener_valor("ingresos")
        efectivo_base = obtener_valor("efectivo")
        cartera_base = obtener_valor("cuentas_por_cobrar")
        inventario_base = obtener_valor("inventarios")

        gastos_base = sum(
            obtener_valor(columna)
            for columna in [
                "gastos_administrativos",
                "gastos_operativos",
                "gastos_financieros",
                "otros_gastos"
            ]
        )

        # Proporciones históricas de cartera e inventarios
        proporcion_cartera = (
            cartera_base / ingresos_base
            if ingresos_base > 0 else 0
        )

        proporcion_inventario = (
            inventario_base / ingresos_base
            if ingresos_base > 0 else 0
        )

        # Simulación
        resultados = []


        cartera_anterior = cartera_base
        inventario_anterior = inventario_base

        for anio in range(1, periodos + 1):

            ingreso = ingresos_base * (
                1 + crecimiento / 100
            ) ** anio

            datos_prediccion = pd.DataFrame({
                "const": [1],
                "ingresos": [ingreso]
            })

            costo = float(
                modelo.predict(datos_prediccion).iloc[0]
            )

            gasto = gastos_base * (
                1 + aumento_gastos / 100
            ) ** anio

            excedente_bruto = ingreso - costo
            excedente_neto = excedente_bruto - gasto

            # Proyección de cuentas por cobrar
            cartera = (
                ingreso
                * proporcion_cartera
                * (1 - mejora_cartera / 100) ** anio
            )

            # Proyección de inventarios
            inventario = (
                ingreso * proporcion_inventario
            )
                # Variación simplificada estimada del efectivo
            variacion_cartera = (
                cartera_anterior - cartera
            )

            variacion_inventario = (
                inventario_anterior - inventario
            )

            variacion_efectivo = (
                excedente_neto
                + variacion_cartera
                + variacion_inventario
            )

            resultados.append({
                "Año proyectado": int(base["anio"]) + anio,
                "Ingresos": ingreso,
                "Costos estimados": costo,
                "Gastos estimados": gasto,
                "Excedente bruto": excedente_bruto,
                "Excedente neto": excedente_neto,
                "Cuentas por cobrar": cartera,
                "Inventarios": inventario,
                "Variación estimada de efectivo": variacion_efectivo
            })

            
            cartera_anterior = cartera
            inventario_anterior = inventario

        proyeccion = pd.DataFrame(resultados)

        # Resultados principales
        st.subheader("Resultados de la simulación")

        ultimo = proyeccion.iloc[-1]

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Ingresos proyectados",
            f"$ {ultimo['Ingresos']:,.2f} millones"
        )

        col2.metric(
            "Excedente neto",
            f"$ {ultimo['Excedente neto']:,.2f} millones"
        )

        col3.metric(
            "Variación estimada de efectivo",
            f"$ {ultimo['Variación estimada de efectivo']:,.2f} millones"
        )
        st.divider()

        # Tabla de resultados
        st.subheader("Proyección financiera detallada")

                formatos = {
            columna: "{:,.2f}"
            for columna in proyeccion.select_dtypes(
                include="number"
            ).columns
        }

        formatos["Año proyectado"] = "{:.0f}"

        st.dataframe(
            proyeccion.style.format(formatos),
            use_container_width=True,
            hide_index=True
        )

        # Gráfico de resultados
        st.subheader("Evolución de ingresos, costos y excedentes")

        grafico = px.line(
            proyeccion,
            x="Año proyectado",
            y=[
                "Ingresos",
                "Costos estimados",
                "Excedente neto"
            ],
            markers=True,
            title="Proyección de resultados financieros"
        )

        st.plotly_chart(
            grafico,
            use_container_width=True
        )

        # Gráfico de variación del efectivo y cartera
        st.subheader("Evolución de la variación del efectivo y las cuentas por cobrar")

        grafico_liquidez = px.line(
            proyeccion,
            x="Año proyectado",
            y=[
                "Variación estimada de efectivo",
                "Cuentas por cobrar"
            ],
            markers=True,
            title="Variación estimada de efectivo y evolución de cartera"
        )

        st.plotly_chart(
            grafico_liquidez,
            use_container_width=True
        )
        st.download_button(
            "Descargar proyección financiera",
            proyeccion.to_csv(
                index=False
            ).encode("utf-8"),
            "proyeccion_financiera.csv",
            "text/csv"
        )

        st.divider()

        st.subheader("Interpretación y limitaciones")

        st.write(
            f"El escenario seleccionado es **{escenario}**, "
            f"con una variación anual de ingresos del "
            f"**{crecimiento}%**, una variación de gastos del "
            f"**{aumento_gastos}%** y una reducción anual "
            f"de la proporción de cartera del "
            f"**{mejora_cartera}%**."
        )

        st.info(
    "La variación estimada de efectivo es una aproximación "
    "simplificada que considera el excedente neto y los cambios "
    "en cuentas por cobrar e inventarios. No representa un saldo "
    "de caja ni un estado de flujo de efectivo proyectado, "
    "pues no incorpora todas las entradas y salidas de dinero."
)

        st.warning(
            "Las proyecciones son exploratorias. El modelo "
            "econométrico cuenta con cinco observaciones anuales. "
            "Además, no se dispone de una clasificación verificada "
            "de pasivos corrientes para calcular el capital de "
            "trabajo neto o proyectar una razón corriente confiable."
        )

    else:
        st.error(
            "No hay suficientes datos para simular escenarios."
        )

st.divider()

st.caption(
    "Proyecto académico | Fundación Amigos de la Salud | "
    "Montería, Colombia"
)

