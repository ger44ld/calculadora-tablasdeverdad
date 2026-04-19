import streamlit as st
import itertools
import pandas as pd
import re

# ---------------------------
# Estado inicial
# ---------------------------
if "expr" not in st.session_state:
    st.session_state.expr = ""

# ---------------------------
# Funciones de UI
# ---------------------------
def agregar(token):
    st.session_state.expr += token + " "

def limpiar():
    st.session_state.expr = ""

# ---------------------------
# Extraer variables
# ---------------------------
def extraer_variables(expr):
    return sorted(set(re.findall(r'[A-Za-z]+', expr)))

# ---------------------------
# Traducir operadores
# ---------------------------
def traducir_expresion(expr):
    expr = expr.upper()

    # Bicondicional
    expr = re.sub(r'(\w+)\s*<->\s*(\w+)', r'(\1 == \2)', expr)

    # Condicional
    expr = re.sub(r'(\w+)\s*->\s*(\w+)', r'((not \1) or \2)', expr)

    # Operadores básicos
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
        raise ValueError("Error en la expresión lógica")

# ---------------------------
# Generar tabla
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
        valores_bool = {k: bool(v) for k, v in valores.items()}
        resultado = evaluar(expr_traducida, valores_bool)
        filas.append(list(comb) + [resultado])

    columnas = variables + ["Resultado"]
    return pd.DataFrame(filas, columns=columnas)

# ---------------------------
# UI
# ---------------------------
st.title("Calculadora de Tablas de Verdad")

st.subheader("Construye la expresión lógica")

# Columnas de botones
col1, col2, col3 = st.columns(3)

# Variables
with col1:
    if st.button("A"): agregar("A")
    if st.button("B"): agregar("B")
    if st.button("C"): agregar("C")
    if st.button("D"): agregar("D")

# Operadores lógicos
with col2:
    if st.button("AND"): agregar("AND")
    if st.button("OR"): agregar("OR")
    if st.button("NOT"): agregar("NOT")
    if st.button("XOR"): agregar("XOR")

# Operadores avanzados y control
with col3:
    if st.button("→"): agregar("->")
    if st.button("↔"): agregar("<->")
    if st.button("("): agregar("(")
    if st.button(")"): agregar(")")
    if st.button("Limpiar"): limpiar()

# Mostrar expresión
st.text_input("Expresión lógica:", st.session_state.expr)

# Generar tabla
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
