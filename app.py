import streamlit as st
import itertools
import pandas as pd
import re

# ---------------------------
# Función para extraer variables
# ---------------------------
def extraer_variables(expr):
    variables = sorted(set(re.findall(r'[A-Za-z]+', expr)))
    return variables

# ---------------------------
# Reemplazar operadores
# ---------------------------
def traducir_expresion(expr):
    expr = expr.upper()
    expr = expr.replace("AND", "and")
    expr = expr.replace("OR", "or")
    expr = expr.replace("NOT", "not")
    expr = expr.replace("XOR", "^")
    return expr

# ---------------------------
# Evaluación segura
# ---------------------------
def evaluar(expr, valores):
    try:
        return int(eval(expr, {"__builtins__": None}, valores))
    except Exception:
        raise ValueError("Error al evaluar la expresión")

# ---------------------------
# Generar tabla de verdad
# ---------------------------
def generar_tabla(expr):
    if not expr.strip():
        raise ValueError("La expresión está vacía")

    variables = extraer_variables(expr)
    expr_traducida = traducir_expresion(expr)

    combinaciones = list(itertools.product([0, 1], repeat=len(variables)))

    filas = []
    for comb in combinaciones:
        valores = dict(zip(variables, comb))

        # convertir a booleanos para evaluación
        valores_bool = {k: bool(v) for k, v in valores.items()}

        resultado = evaluar(expr_traducida, valores_bool)

        fila = list(comb) + [resultado]
        filas.append(fila)

    columnas = variables + ["Resultado"]
    df = pd.DataFrame(filas, columns=columnas)

    return df

# ---------------------------
# UI
# ---------------------------
st.title("Calculadora de Tablas de Verdad")

expr = st.text_input("Ingresa la expresión lógica (ej: A AND B OR NOT C)")

if st.button("Generar tabla"):
    try:
        df = generar_tabla(expr)
        st.dataframe(df)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar CSV",
            data=csv,
            file_name="tabla_verdad.csv",
            mime="text/csv"
        )

    except ValueError as e:
        st.error(f"⚠️ {e}")