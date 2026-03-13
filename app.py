import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. CONFIGURACIÓN VISUAL (MODO OSCURO BERARDI)
st.set_page_config(page_title="Berardi Stock Pro", page_icon="❄️", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    .header-container {
        background: linear-gradient(135deg, #003366 0%, #001a33 100%);
        padding: 20px; border-radius: 15px; text-align: center;
        margin-bottom: 25px; border: 1px solid #30363d;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    div.row-widget.stRadio > div { flex-direction: row; justify-content: space-between; gap: 10px; }
    .history-card {
        background-color: #161b22; padding: 15px; border-radius: 12px;
        margin-bottom: 12px; border-left: 6px solid #58a6ff; border: 1px solid #30363d;
    }
    .stButton > button { border-radius: 12px; font-weight: bold; width: 100%; height: 3.5em; border: none; }
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
        color: white;
    }
    label { color: #58a6ff !important; font-weight: bold !important; }
    </style>
    
    <div class="header-container">
        <h1 style='margin:0; color: white; font-size: 26px;'>BERARDI S.A.</h1>
        <p style='margin:0; color: #58a6ff; font-weight: 500;'>Control de Cámaras v2.2</p>
    </div>
    """, unsafe_allow_html=True)

# 2. DATOS Y PRODUCTOS
DB_FILE = "stock_berardi_data.csv"
PRODUCTOS_BERARDI = {
    "PESCADOS": ["Merluza (Filete)", "Merluza (HGT)", "Abadejo", "Gatuzo", "Besugo"],
    "MARISCOS": ["Langostino Entero", "Langostino Cola", "Calamar Entero", "Vainas"],
    "REBOZADOS": ["Medallones", "Bastoncitos", "Formitas"],
    "INSUMOS": ["Hielo", "Cajas Master", "Bolsas"]
}

def cargar_datos():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["ID", "Fecha", "Tipo", "Producto", "Kgs", "Bultos", "Origen", "Destino", "Pos"])

def guardar_datos(df): df.to_csv(DB_FILE, index=False)

if "edit_id" not in st.session_state: st.session_state.edit_id = None
df_actual = cargar_datos()

# 3. FORMULARIO
st.markdown(f"### {'📝 EDITANDO ID: ' + str(st.session_state.edit_id) if st.session_state.edit_id else '📥 NUEVO REGISTRO'}")

if st.session_state.edit_id:
    val_viejo = df_actual[df_actual["ID"] == st.session_state.edit_id].iloc[0]
    idx_tipo = ["📥 Ingreso", "🔄 Transf.", "🔙 Devol.", "📤 Salida"].index(val_viejo["Tipo"])
else:
    val_viejo, idx_tipo = None, 0

tipo_op = st.radio("OPERACIÓN:", ["📥 Ingreso", "🔄 Transf.", "🔙 Devol.", "📤 Salida"], index=idx_tipo, horizontal=True)

with st.container():
    c1, c2 = st.columns(2)
    with c1: cat = st.selectbox("Familia:", list(PRODUCTOS_BERARDI.keys()))
    with c2: prod = st.selectbox("Producto:", PRODUCTOS_BERARDI[cat])
    
    ck, cb = st.columns(2)
    with ck: kgs = st.number_input("Kilos Netos:", min_value=0.0, step=0.5, value=float(val_viejo["Kgs"]) if val_viejo is not None else 0.0)
    with cb: bultos = st.number_input("Bultos:", min_value=0, step=1, value=int(val_viejo["Bultos"]) if val_viejo is not None else 0)
    
    st.markdown("<p style='color: #58a6ff; font-weight: bold; margin-top:15px;'>LOGÍSTICA</p>", unsafe_allow_html=True)
    
    col_o, col_d = st.columns(2)
    
    if "Ingreso" in tipo_op:
        with col_o: 
            orig = st.selectbox("Origen:", ["Producción", "Proveedor", "Rouco"])
        with col_d: 
            dest = st.selectbox("Destino:", ["Cámara 2", "Cámara 3", "Cámara 4"])
            
    elif "Transf" in tipo_op:
        with col_o: 
            orig = st.selectbox("Desde:", ["Cámara 2", "Cámara 3", "Cámara 4"])
        with col_d: 
            dest = st.selectbox("Hacia:", ["Cámara 2", "Cámara 3", "Cámara 4"], index=1)
            
    elif "Salida" in tipo_op:
        with col_o: 
            orig = st.selectbox("Extraer de:", ["Cámara 2", "Cámara 3", "Cámara 4"])
        with col_d: 
            dest = st.text_input("Destino:", value="Expedición", disabled=True)
            
    else: # Devolución
        with col_o: 
            orig = st.text_input("Origen:", value="Cliente / Externo")
        with col_d: 
            dest = st.selectbox("Ingresa a:", ["Cámara 2", "Cámara 3", "Cámara 4"])

    pos = st.text_input("Posición:", value=val_viejo["Pos"] if val_viejo is not None else "", placeholder="Ej: Fila A-3")

# BOTONES
c_b1, c_b2 = st.columns([3, 1])
with c_b1:
    if st.button("💾 ACTUALIZAR" if st.session_state.edit_id else "💾 GUARDAR"):
        if kgs > 0 or bultos > 0:
            if st.session_state.edit_id:
                df_actual.loc[df_actual["ID"] == st.session_state.edit_id, ["Tipo", "Producto", "Kgs", "Bultos", "Origen", "Destino", "Pos"]] = [tipo_op, prod, kgs, bultos, orig, dest, pos]
                st.session_state.edit_id = None
            else:
                nuevo_id = int(df_actual["ID"].max() + 1) if not df_actual.empty else 101
                nuevo_reg = {"ID": nuevo_id, "Fecha": datetime.now().strftime("%H:%M - %d/%m"), "Tipo": tipo_op, "Producto": prod, "Kgs": kgs, "Bultos": bultos, "Origen": orig, "Destino": dest, "Pos": pos}
                df_actual = pd.concat([df_actual, pd.DataFrame([nuevo_reg])], ignore_index=True)
            guardar_datos(df_actual)
            st.rerun()

with c_b2:
    if st.session_state.edit_id and st.button("❌"):
        st.session_state.edit_id = None
        st.rerun()

# GESTIÓN Y LISTADO
st.markdown("---")
if not df_actual.empty:
    with st.expander("🛠️ EDITAR / ELIMINAR"):
        id_sel = st.selectbox("Seleccionar ID:", df_actual["ID"].astype(int).tolist()[::-1])
        c_e, c_d = st.columns(2)
        if c_e.button("✏️ EDITAR"):
            st.session_state.edit_id = id_sel
            st.rerun()
        if c_d.button("🗑️ BORRAR", type="secondary"):
            df_actual = df_actual[df_actual["ID"] != id_sel]
            guardar_datos(df_actual)
            st.rerun()

    st.markdown("### 🕒 Últimos Movimientos")
    for _, row in df_actual.tail(3).iloc[::-1].iterrows():
        color = "#238636" if "Ingreso" in row['Tipo'] else "#da3633" if "Salida" in row['Tipo'] else "#1f6feb"
        st.markdown(f"""
            <div class="history-card" style="border-left-color: {color};">
                <strong>ID: {int(row['ID'])} | {row['Tipo']}</strong><br>
                <span style="font-size: 1.1rem;">{row['Producto']}</span><br>
                <span>{row['Kgs']} Kg | {row['Bultos']} Bultos</span><br>
                <small style="color: #8b949e;">{row['Origen']} ➡️ {row['Destino']} ({row['Pos']})</small>
            </div>
        """, unsafe_allow_html=True)
