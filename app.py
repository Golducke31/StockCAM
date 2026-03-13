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
    /* Botón Guardar Verde */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
        color: white;
    }
    label { color: #58a6ff !important; font-weight: bold !important; }
    </style>
    
    <div class="header-container">
        <h1 style='margin:0; color: white; font-size: 26px;'>BERARDI S.A.</h1>
        <p style='margin:0; color: #58a6ff; font-weight: 500;'>Control de Cámaras v2.1</p>
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

# 3. LÓGICA DE ESTADO (Para Edición)
if "edit_id" not in st.session_state: st.session_state.edit_id = None

df_actual = cargar_datos()

# 4. FORMULARIO DINÁMICO
st.markdown(f"### {'📝 EDITANDO ID: ' + str(st.session_state.edit_id) if st.session_state.edit_id else '📥 NUEVO REGISTRO'}")

# Precarga de datos si estamos editando
if st.session_state.edit_id:
    val_viejo = df_actual[df_actual["ID"] == st.session_state.edit_id].iloc[0]
    idx_tipo = ["📥 Ingreso", "🔄 Transf.", "🔙 Devol.", "📤 Salida"].index(val_viejo["Tipo"])
else:
    val_viejo = None
    idx_tipo = 0

tipo_op = st.radio("OPERACIÓN:", ["📥 Ingreso", "🔄 Transf.", "🔙 Devol.", "📤 Salida"], index=idx_tipo, horizontal=True)

st.markdown("---")

with st.container():
    c1, c2 = st.columns(2)
    with c1: cat = st.selectbox("Familia:", list(PRODUCTOS_BERARDI.keys()))
    with c2: prod = st.selectbox("Producto:", PRODUCTOS_BERARDI[cat])
    
    ck, cb = st.columns(2)
    with ck: kgs = st.number_input("Kilos Netos:", min_value=0.0, step=0.5, value=float(val_viejo["Kgs"]) if val_viejo is not None else 0.0)
    with cb: bultos = st.number_input("Bultos:", min_value=0, step=1, value=int(val_viejo["Bultos"]) if val_viejo is not None else 0)
    
    # --- LOGÍSTICA DE CÁMARAS MEJORADA ---
    st.markdown("<p style='color: #58a6ff; font-weight: bold; margin-top:15px;'>UBICACIÓN Y MOVIMIENTO</p>", unsafe_allow_html=True)
    
    if "Transf" in tipo_op:
        col_orig, col_dest = st.columns(2)
        with col_orig: 
            orig = st.selectbox("Desde (Origen):", ["Cámara 2", "Cámara 3", "Cámara 4"], 
                               index=(["Cámara 2", "Cámara 3", "Cámara 4"].index(val_viejo["Origen"]) if val_viejo is not None and val_viejo["Origen"] in ["Cámara 2", "Cámara 3", "Cámara 4"] else 0))
        with col_dest: 
            dest = st.selectbox("Hacia (Destino):", ["Cámara 2", "Cámara 3", "Cámara 4"], 
                               index=(["Cámara 2", "Cámara 3", "Cámara 4"].index(val_viejo["Destino"]) if val_viejo is not None and val_viejo["Destino"] in ["Cámara 2", "Cámara 3", "Cámara 4"] else 1))
    elif "Salida" in tipo_op:
        orig = st.selectbox("Extraer de:", ["Cámara 2", "Cámara 3", "Cámara 4"])
        dest = "EXPEDICIÓN / VENTA"
    else: # Ingresos y Devoluciones
        orig = "EXTERNO / CLIENTE"
        dest = st.selectbox("Ingresa a:", ["Cámara 2", "Cámara 3", "Cámara 4"])

    pos = st.text_input("Posición específica:", value=val_viejo["Pos"] if val_viejo is not None else "", placeholder="Ej: Fila A, Estante 3")

# BOTONES DE ACCIÓN
col_btn1, col_btn2 = st.columns([3, 1])
with col_btn1:
    txt_boton = "💾 ACTUALIZAR REGISTRO" if st.session_state.edit_id else "💾 GUARDAR MOVIMIENTO"
    if st.button(txt_boton):
        if kgs > 0 or bultos > 0:
            if st.session_state.edit_id: # Lógica Modificar
                df_actual.loc[df_actual["ID"] == st.session_state.edit_id, ["Tipo", "Producto", "Kgs", "Bultos", "Origen", "Destino", "Pos"]] = [tipo_op, prod, kgs, bultos, orig, dest, pos]
                st.session_state.edit_id = None
                st.success("Registro actualizado correctamente")
            else: # Lógica Nuevo
                nuevo_id = int(df_actual["ID"].max() + 1) if not df_actual.empty else 101
                nuevo_reg = {"ID": nuevo_id, "Fecha": datetime.now().strftime("%H:%M - %d/%m"), "Tipo": tipo_op, "Producto": prod, "Kgs": kgs, "Bultos": bultos, "Origen": orig, "Destino": dest, "Pos": pos}
                df_actual = pd.concat([df_actual, pd.DataFrame([nuevo_reg])], ignore_index=True)
                st.success(f"ID {nuevo_id} guardado con éxito")
            
            guardar_datos(df_actual)
            st.rerun()
        else:
            st.error("Debe ingresar Kilos o Bultos")

with col_btn2:
    if st.session_state.edit_id:
        if st.button("❌"):
            st.session_state.edit_id = None
            st.rerun()

# 5. GESTIÓN DE REGISTROS (EDITAR / ELIMINAR)
st.markdown("---")
if not df_actual.empty:
    with st.expander("🗑️ MODIFICAR O ELIMINAR REGISTROS"):
        ids = df_actual["ID"].astype(int).tolist()[::-1]
        id_sel = st.selectbox("Seleccione ID:", ids)
        
        c_ed, c_del = st.columns(2)
        with c_ed:
            if st.button("✏️ EDITAR", key="btn_edit_footer"):
                st.session_state.edit_id = id_sel
                st.rerun()
        with c_del:
            if st.button("🗑️ BORRAR", type="secondary"):
                df_actual = df_actual[df_actual["ID"] != id_sel]
                guardar_datos(df_actual)
                st.warning(f"ID {id_sel} eliminado")
                st.rerun()

    # 6. HISTORIAL VISUAL
    st.markdown("### 🕒 Últimos Movimientos")
    for _, row in df_actual.tail(3).iloc[::-1].iterrows():
        c_lat = "#238636" if "Ingreso" in row['Tipo'] else "#da3633" if "Salida" in row['Tipo'] else "#1f6feb"
        st.markdown(f"""
            <div class="history-card" style="border-left-color: {c_lat};">
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: #58a6ff; font-weight: bold;">ID: {int(row['ID'])}</span>
                    <span style="color: #8b949e; font-size: 0.8rem;">{row['Fecha']}</span>
                </div>
                <strong style="font-size: 1.1rem;">{row['Producto']}</strong><br>
                <span>{row['Kgs']} Kg | {row['Bultos']} Bultos</span><br>
                <small style="color: #8b949e;">De: {row['Origen']} ➡️ A: {row['Destino']}</small><br>
                <small style="color: #8b949e;">📍 {row['Pos']}</small>
            </div>
        """, unsafe_allow_html=True)
