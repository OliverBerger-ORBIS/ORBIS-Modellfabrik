import pandas as pd
import streamlit as st

from message_monitor_service import MessageMonitorService

st.set_page_config(page_title="APS – Nachrichten-Zentrale", layout="wide")

# ---- Configuration (adjust to your broker) ----
BROKER_HOST = st.secrets.get("mqtt_host", "localhost")
BROKER_PORT = int(st.secrets.get("mqtt_port", 1883))
MQTT_USER = st.secrets.get("mqtt_user", None)
MQTT_PASS = st.secrets.get("mqtt_pass", None)
SUB_FILTER = st.secrets.get("mqtt_sub_filter", "#")
SUB_QOS = int(st.secrets.get("mqtt_sub_qos", 0))
DB_PATH = st.secrets.get("mqtt_db_path", "messages.sqlite")


# ---- Keep service alive across reruns ----
@st.cache_resource
def get_service():
    svc = MessageMonitorService(
        broker_host=BROKER_HOST,
        broker_port=BROKER_PORT,
        username=MQTT_USER,
        password=MQTT_PASS,
        subscribe_filter=(SUB_FILTER, SUB_QOS),
        db_path=DB_PATH,
        keepalive=45,
        tls=False,
    )
    return svc.start()


svc = get_service()

st.sidebar.subheader("Verbindung")
st.sidebar.write(f"Broker: **{BROKER_HOST}:{BROKER_PORT}**")
st.sidebar.write("Status: " + ("🟢 verbunden" if svc.is_connected() else "🔴 getrennt"))
if st.sidebar.button("Neu verbinden"):
    svc.stop()
    svc = get_service()
    st.experimental_rerun()

tab_center, tab_control = st.tabs(["📬 Nachrichten‑Zentrale", "🛠️ Steuerung"])

with tab_center:
    st.subheader("Letzte Nachrichten")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        limit = st.number_input("Anzahl", min_value=50, max_value=5000, value=300, step=50)
    with col2:
        if st.button("Aktualisieren"):
            st.experimental_rerun()
    with col3:
        st.caption("Tipp: Auto-Refresh kann über Streamlit Components ergänzt werden.")
    msgs = svc.fetch_recent(limit=limit)
    if msgs:
        df = pd.DataFrame(
            [
                {
                    "Zeit": pd.to_datetime(m.ts, unit="s"),
                    "Richtung": m.direction,
                    "Topic": m.topic,
                    "QoS": m.qos,
                    "Retain": bool(m.retain),
                    "Payload": m.payload,
                }
                for m in msgs
            ]
        )
        st.dataframe(df, use_container_width=True, height=600)
    else:
        st.info("Noch keine Nachrichten empfangen/gespeichert.")

with tab_control:
    st.subheader("Nachricht senden")
    with st.form("publish_form", clear_on_submit=False):
        topic = st.text_input("Topic", value="aps/control/example")
        payload = st.text_area("Payload (Text oder JSON)", value='{"cmd": "ping"}', height=120)
        qos = st.selectbox("QoS", options=[0, 1, 2], index=0)
        retain = st.checkbox("Retain", value=False)
        submitted = st.form_submit_button("Senden")
        if submitted:
            # try to parse JSON, else send as string
            data = payload
            try:
                import json

                data = json.loads(payload)
            except Exception:
                pass
            mid = svc.publish(topic, data, qos=int(qos), retain=retain)
            if mid is not None:
                st.success(f"Gesendet (mid={mid})")
            else:
                st.error("Senden fehlgeschlagen (vermutlich getrennt).")
