import streamlit as st
import pandas as pd

st.set_page_config(page_title="Arca Reportes", page_icon="📊", layout="wide")
st.title("📊 Arca Reportes")

USER, PASS = "admin", "1234"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    with st.form("login_form"):
        user = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Ingresar")
        if submit:
            if user == USER and password == PASS:
                st.session_state.logged_in = True
                st.success("Inicio de sesión exitoso ✅")
            else:
                st.error("Usuario o contraseña incorrectos ❌")
    st.stop()

st.sidebar.header("Carga de archivos CSV")
emitidos = st.sidebar.file_uploader("Comprobantes emitidos", type=["csv"])
recibidos = st.sidebar.file_uploader("Comprobantes recibidos", type=["csv"])

if emitidos and recibidos:
    df_emitidos = pd.read_csv(emitidos)
    df_recibidos = pd.read_csv(recibidos)

    st.header("📅 Resumen general")
    total_emitidos = df_emitidos["Importe Total"].sum()
    total_recibidos = df_recibidos["Importe Total"].sum()
    diferencia = total_emitidos - total_recibidos

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Emitidos", f"${total_emitidos:,.2f}")
    c2.metric("Total Recibidos", f"${total_recibidos:,.2f}")
    c3.metric("Diferencia", f"${diferencia:,.2f}")

    st.header("📆 Comprobantes por día")
    if "Fecha Emisión" in df_emitidos.columns:
        diarios = df_emitidos.groupby("Fecha Emisión")["Importe Total"].sum().reset_index()
        st.dataframe(diarios)

    st.header("👥 Proveedores / Clientes")
    if "Denominación Vendedor" in df_recibidos.columns:
        st.write(df_recibidos.groupby("Denominación Vendedor")["Importe Total"].sum())

else:
    st.info("📂 Cargá los dos archivos CSV para comenzar el análisis.")
