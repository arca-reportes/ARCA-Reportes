 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/app_streamlit_auth.py b/app_streamlit_auth.py
index 7e40415f9b66f8266ab5f2a2ec878937ae57d214..f37f076482411414e37dc834b897fae921506dcc 100644
--- a/app_streamlit_auth.py
+++ b/app_streamlit_auth.py
@@ -4,50 +4,72 @@ import pandas as pd
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
 
+def load_csv(uploaded_file, label):
+    """Read a CSV handling common formatting issues."""
+    if uploaded_file is None:
+        return None
+
+    read_options = [
+        {},
+        {"sep": None, "engine": "python"},
+        {"sep": ";", "engine": "python"},
+    ]
+
+    for options in read_options:
+        try:
+            uploaded_file.seek(0)
+            return pd.read_csv(uploaded_file, **options)
+        except (pd.errors.ParserError, UnicodeDecodeError):
+            continue
+
+    st.error(f"❌ No se pudo leer el archivo '{label}'. Verifica que sea un CSV válido.")
+    st.stop()
+
+
 if emitidos and recibidos:
-    df_emitidos = pd.read_csv(emitidos)
-    df_recibidos = pd.read_csv(recibidos)
+    df_emitidos = load_csv(emitidos, "Comprobantes emitidos")
+    df_recibidos = load_csv(recibidos, "Comprobantes recibidos")
 
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
EOF
)
