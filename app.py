import streamlit as st
import itertools
import pandas as pd
import re

# ---------------------------
# Estado
# ---------------------------
if "expr" not in st.session_state:
    st.session_state.expr = ""

def agregar(token):
    st.session_state.expr += token + " "

def limpiar():
    st.session_state.expr = ""

# ---------------------------
# EXTRAER SOLO A, B, C, D (FIX DEFINITIVO)
# ---------------------------
def extraer_variables(expr):
    expr = expr.upper()
    variables_validas = {"A", "B", "C", "D"}
    tokens = set(re.findall(r'\b[A-Z]\b', expr))
    return sorted(tokens.intersection(variables_validas))

# ---------------------------
# TRADUCCIÓN SEGURA A PYTHON
# ---------------------------
def traducir_expresion(expr):
    expr = expr.upper()

    # operadores avanzados
    expr = re.sub(r'(\b[A-D]\b)\s*<->\s*(\b[A-D]\b)', r'(\1 == \2)', expr)
    expr = re.sub(r'(\b[A-D]\b)\s*->\s*(\b[A-D]\b)', r'(not \1 or \2)', expr)

    # operadores básicos
    expr = expr.replace("AND", " and ")
    expr = expr.replace("OR", " or ")
    expr = expr.replace("NOT", " not ")
    expr = expr.replace("XOR", " != ")

    return expr

# ---------------------------
# EVALUACIÓN SEGURA
# ---------------------------
def evaluar(expr, valores):
    try:
        return int(eval(expr, {"__builtins__": None}, valores))
    except Exception as e:
        raise ValueError(f"Error en la expresión lógica: {e}")

# ---------------------------
# TABLA DE VERDAD
# ---------------------------
def generar_tabla(expr):
    if not expr.strip():
        raise ValueError("La expresión está vacía")

    variables = extraer_variables(expr)

    if len(variables) == 0:
        raise ValueError("Usa solo A, B, C o D")

    expr_py = traducir_expresion(expr)

    combinaciones = list(itertools.product([0, 1], repeat=len(variables)))

    filas = []
    for comb in combinaciones:
        valores = dict(zip(variables, comb))
        resultado = evaluar(expr_py, valores)
        filas.append(list(comb) + [resultado])

    columnas = variables + ["Resultado"]
    return pd.DataFrame(filas, columns=columnas)

# ---------------------------
# UI
# ---------------------------
st.title("🧠 Calculadora de Tablas de Verdad")

col1, col2, col3 = st.columns(3)

# Variables
with col1:
    if st.button("A"): agregar("A")
    if st.button("B"): agregar("B")
    if st.button("C"): agregar("C")
    if st.button("D"): agregar("D")

# Operadores
with col2:
    if st.button("AND"): agregar("AND")
    if st.button("OR"): agregar("OR")
    if st.button("NOT"): agregar("NOT")
    if st.button("XOR"): agregar("XOR")

# Avanzados
with col3:
    if st.button("→"): agregar("->")
    if st.button("↔"): agregar("<->")
    if st.button("("): agregar("(")
    if st.button(")"): agregar(")")
    if st.button("Limpiar"): limpiar()

st.text_input("Expresión lógica:", st.session_state.expr)

if st.button("Generar tabla"):
    try:
        df = generar_tabla(st.session_state.expr)
        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Descargar CSV",
            csv,
            "tabla_verdad.csv",
            "text/csv"
        )

    except ValueError as e:
        st.error(f"⚠️ {e}")
