import streamlit as st
import csv
import io

import pandas as pd
import streamlit as st

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

def _candidate_delimiters(text: str) -> list[str]:
    base = [",", ";", "\t", "|"]
    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=base)
    except csv.Error:
        return base

    return [dialect.delimiter] + [d for d in base if d != dialect.delimiter]


def load_csv(uploaded_file, label):
    """Read a CSV handling common encoding and delimiter issues."""
    if uploaded_file is None:
        return None

    raw_bytes = uploaded_file.getvalue()
    encodings = ("utf-8", "utf-8-sig", "latin-1", "cp1252")
    attempts = []

    for encoding in encodings:
        try:
            decoded = raw_bytes.decode(encoding)
        except UnicodeDecodeError:
            attempts.append(f"- No se pudo decodificar con codificación {encoding}.")
            continue

        for sep in _candidate_delimiters(decoded):
            # Primera lectura estricta
            try:
                buffer = io.StringIO(decoded)
                return pd.read_csv(buffer, sep=sep, engine="python")
            except (pd.errors.ParserError, UnicodeDecodeError, ValueError) as exc:
                attempts.append(
                    f"- Error leyendo con codificación {encoding} y separador '{sep}': {exc.__class__.__name__}."
                )

            # Segunda lectura omitiendo filas dañadas
            bad_lines: list[list[str]] = []

            def _collect_bad(line: list[str]):
                bad_lines.append(line)
                return None

            try:
                buffer = io.StringIO(decoded)
                df = pd.read_csv(
                    buffer,
                    sep=sep,
                    engine="python",
                    on_bad_lines=_collect_bad,
                )
            except (pd.errors.ParserError, UnicodeDecodeError, ValueError):
                continue

            if bad_lines:
                st.warning(
                    f"⚠️ Se omitieron {len(bad_lines)} fila(s) con formato inválido en '{label}'."
                )
            return df

    detail = "\n".join(dict.fromkeys(attempts))  # dict.fromkeys preserves order and removes duplicates
    st.error(
        "❌ No se pudo leer el archivo "
        f"'{label}'. Asegúrate de que el archivo sea un CSV válido con un separador estándar.\n" + detail
    )
    st.stop()


if emitidos and recibidos:
    df_emitidos = pd.read_csv(emitidos)
    df_recibidos = pd.read_csv(recibidos)
    df_emitidos = load_csv(emitidos, "Comprobantes emitidos")
    df_recibidos = load_csv(recibidos, "Comprobantes recibidos")

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
