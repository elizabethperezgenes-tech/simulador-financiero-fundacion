
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

# --------------------------------------------------
# 1. DIAGNÓSTICO HISTÓRICO
# --------------------------------------------------

with tab1:
    datos_historicos = df.sort_values("anio").copy()

    st.header("Diagnóstico financiero histórico")

    st.write(
        "Información financiera expresada en millones de pesos colombianos."
    )

    # Indicadores principales del último año disponible
    ultimo = datos_historicos.iloc[-1]
    anio = int(ultimo["anio"])

    st.subheader(f"Resumen financiero del año {anio}")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Ingresos",
        f"$ {ultimo['ingresos']:,.2f} millones"
    )

    col2.metric(
        "Costos",
        f"$ {ultimo['costos']:,.2f} millones"
    )

    col3.metric(
        "Excedente neto",
        f"$ {ultimo['excedente_neto']:,.2f} millones"
    )

    col4.metric(
        "Activos totales",
        f"$ {ultimo['activos_totales']:,.2f} millones"
    )

    # Tabla de información histórica
    st.subheader("Estados financieros históricos")

    st.dataframe(
        datos_historicos,
        use_container_width=True,
        hide_index=True
    )

    # Evolución de ingresos y costos
    st.subheader("Evolución de ingresos y costos")

    fig = px.line(
        datos_historicos,
        x="anio",
        y=["ingresos", "costos"],
        markers=True,
        title="Ingresos frente a costos"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # Evolución del excedente neto
    st.subheader("Comportamiento del excedente neto")

    fig2 = px.bar(
        datos_historicos,
        x="anio",
        y="excedente_neto",
        title="Excedente neto histórico"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    # Participación del efectivo y la cartera
    st.subheader("Composición de los activos corrientes")

    datos_historicos["participacion_efectivo"] = (
        datos_historicos["efectivo"]
        / datos_historicos["activos_corrientes"]
    ) * 100

    datos_historicos["participacion_cartera"] = (
        datos_historicos["cuentas_por_cobrar"]
        / datos_historicos["activos_corrientes"]
    ) * 100

    fig3 = px.line(
        datos_historicos,
        x="anio",
        y=["participacion_efectivo", "participacion_cartera"],
        markers=True,
        title="Participación del efectivo y las cuentas por cobrar",
        labels={
            "value": "Participación (%)",
            "anio": "Año",
            "variable": "Indicador",
            "participacion_efectivo": "Efectivo",
            "participacion_cartera": "Cuentas por cobrar"
        }
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

    # Descarga de la base histórica
    st.download_button(
        "Descargar base histórica",
        df.to_csv(index=False).encode("utf-8"),
        "estados_financieros.csv",
        "text/csv"
    )

    # Análisis automático de la evolución financiera
    st.subheader("Análisis automático de la evolución financiera")

    primer_anio = datos_historicos.iloc[0]
    ultimo_anio = datos_historicos.iloc[-1]

    variacion_ingresos = (
        (ultimo_anio["ingresos"] / primer_anio["ingresos"]) - 1
    ) * 100

    variacion_costos = (
        (ultimo_anio["costos"] / primer_anio["costos"]) - 1
    ) * 100

    variacion_efectivo = (
        (ultimo_anio["efectivo"] / primer_anio["efectivo"]) - 1
    ) * 100

    variacion_cartera = (
        (ultimo_anio["cuentas_por_cobrar"] /
         primer_anio["cuentas_por_cobrar"]) - 1
    ) * 100

    st.write(
        f"Entre {int(primer_anio['anio'])} y "
        f"{int(ultimo_anio['anio'])}, los ingresos "
        f"variaron un {variacion_ingresos:.2f} %."
    )

    st.write(
        f"En el mismo periodo, los costos variaron "
        f"un {variacion_costos:.2f} %."
    )

    st.write(
        f"El efectivo presentó una variación del "
        f"{variacion_efectivo:.2f} %."
    )

    st.write(
        f"Las cuentas por cobrar presentaron una variación "
        f"del {variacion_cartera:.2f} %."
    )

    if variacion_costos > variacion_ingresos:
        st.warning(
            "Los costos crecieron más que los ingresos. "
            "Se recomienda revisar la estructura de costos."
        )
    else:
        st.success(
            "Los ingresos crecieron a una tasa igual o superior "
            "a la de los costos."
        )

    if variacion_efectivo < 0:
        st.warning(
            "El efectivo disminuyó durante el periodo analizado. "
            "Es importante fortalecer la disponibilidad de recursos."
        )

    if variacion_cartera > 0:
        st.info(
            "Las cuentas por cobrar aumentaron. "
            "Conviene hacer seguimiento a la recuperación de cartera."
        )

    # Conclusión general del diagnóstico financiero
    st.subheader("Conclusión general del diagnóstico financiero")

    efectivo_2025 = ultimo_anio["efectivo"]
    activos_corrientes_2025 = ultimo_anio["activos_corrientes"]
    cartera_2025 = ultimo_anio["cuentas_por_cobrar"]

    participacion_efectivo_2025 = (
        efectivo_2025 / activos_corrientes_2025
    ) * 100

    participacion_cartera_2025 = (
        cartera_2025 / activos_corrientes_2025
    ) * 100

    st.write(
        "El análisis histórico de la Fundación Amigos de la Salud "
        "durante el periodo 2020-2025 evidencia un crecimiento "
        "de los ingresos y de los costos, con una evolución "
        "favorable de los ingresos frente a los costos."
    )

    st.write(
        f"Sin embargo, se identifica una reducción del efectivo "
        f"del {abs(variacion_efectivo):.2f} % entre 2020 y 2025. "
        f"Para 2025, el efectivo representa apenas el "
        f"{participacion_efectivo_2025:.2f} % de los activos corrientes."
    )

    st.write(
        f"Asimismo, las cuentas por cobrar representan el "
        f"{participacion_cartera_2025:.2f} % de los activos corrientes "
        f"en 2025, lo que evidencia una elevada concentración "
        f"de los recursos en cartera."
    )

    st.warning(
        "En conclusión, el principal aspecto que requiere atención "
        "es la disponibilidad inmediata de efectivo y la gestión "
        "de recuperación de cartera. Se recomienda fortalecer "
        "el seguimiento de los recaudos, la planeación de tesorería "
        "y el control del capital de trabajo."
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
    # 6. Alertas financieras automáticas
    st.subheader("Alertas financieras")

    datos_alertas = datos[
        datos["anio"] >= 2022
    ].sort_values("anio")

    if not datos_alertas.empty:

        ultimo = datos_alertas.iloc[-1]

        st.write(
            f"Análisis correspondiente al año {int(ultimo['anio'])}"
        )

        # Alerta de disponibilidad de efectivo
        if ultimo["participacion_efectivo"] < 1:
            st.warning(
                "ALERTA DE EFECTIVO: la participación del efectivo "
                "en los activos corrientes es inferior al 1 %. "
                "Esto evidencia una disponibilidad inmediata "
                "muy reducida."
            )
        else:
            st.success(
                "La participación del efectivo es superior al 1 %."
            )

        # Alerta de concentración de cartera
        if ultimo["participacion_cartera"] >= 90:
            st.warning(
                "ALERTA DE CARTERA: más del 90 % de los activos "
                "corrientes está concentrado en cuentas por cobrar. "
                "Se recomienda fortalecer la gestión de recaudo."
            )
        else:
            st.info(
                "La concentración de cartera es inferior al 90 %."
            )

        # Alerta de razón corriente
        if ultimo["razon_corriente"] < 1:
            st.error(
                "ALERTA DE LIQUIDEZ: la razón corriente es inferior "
                "a 1. Los activos corrientes no cubren el pasivo "
                "utilizado en este indicador."
            )
        else:
            st.info(
                "La razón corriente es superior a 1. "
                "Los activos corrientes superan el pasivo utilizado "
                "en el cálculo."
            )

    # 7. Aclaración metodológica
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

        # Interpretación económica del modelo
        st.subheader("Interpretación económica del modelo")

        st.write(
            f"El coeficiente de ingresos (β₁) es "
            f"{modelo.params.iloc[1]:.4f}. Esto indica que, "
            "por cada millón de pesos adicional en ingresos, "
            "el modelo estima un incremento promedio de "
            f"{modelo.params.iloc[1]:.4f} millones de pesos "
            "en los costos."
        )

        st.write(
            f"El coeficiente de determinación R² es "
            f"{modelo.rsquared:.4f}, lo que indica que "
            f"aproximadamente el {modelo.rsquared * 100:.2f} % "
            "de la variación observada en los costos se explica "
            "por la relación lineal con los ingresos dentro de "
            "esta muestra."
        )

        st.info(
            "El modelo identifica una asociación entre ingresos "
            "y costos, pero no demuestra una relación de causalidad. "
            "Sus resultados deben considerarse exploratorios debido "
            "al reducido número de observaciones."
        )

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

