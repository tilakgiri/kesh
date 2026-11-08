
import streamlit as st
import psutil
import plotly.graph_objects as go
from collections import deque
from datetime import datetime
from monitor.network_monitor import check_internet

# Page configuration
st.set_page_config(
    page_title="PC & Network Monitor",
    page_icon="🌐",
    layout="wide"
)

st.title("🌐 Personal PC & Network Monitor")
st.caption("Real-time system and internet monitoring")

# Store recent monitoring data
if "timestamps" not in st.session_state:
    st.session_state.timestamps = deque(maxlen=30)
    st.session_state.cpu_history = deque(maxlen=30)
    st.session_state.ram_history = deque(maxlen=30)

if "ping_history" not in st.session_state:
    st.session_state.ping_history = deque(maxlen=30)

@st.fragment(run_every="5s")
def dashboard():

    # Collect system data
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory()
    network = check_internet()

    st.session_state.ping_history.append(
    network["latency"]
    )

    timestamp = datetime.now().strftime("%H:%M:%S")

    st.session_state.timestamps.append(timestamp)
    st.session_state.cpu_history.append(cpu)
    st.session_state.ram_history.append(ram.percent)

    # Metric cards
    st.subheader("System Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("CPU Usage", f"{cpu}%")
    col2.metric("RAM Usage", f"{ram.percent}%")
    col3.metric(
        "Available RAM",
        f"{ram.available / (1024 ** 3):.2f} GB"
    )

    # CPU graph
    st.subheader("CPU Usage History")

    cpu_fig = go.Figure()

    cpu_fig.add_trace(go.Scatter(
        x=list(st.session_state.timestamps),
        y=list(st.session_state.cpu_history),
        mode="lines+markers",
        name="CPU Usage",
        fill="tozeroy"
    ))

    cpu_fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Usage (%)",
        yaxis_range=[0, 100],
        height=300
    )

    st.plotly_chart(cpu_fig, use_container_width=True)

    # RAM graph
    st.subheader("RAM Usage History")

    ram_fig = go.Figure()

    ram_fig.add_trace(go.Scatter(
        x=list(st.session_state.timestamps),
        y=list(st.session_state.ram_history),
        mode="lines+markers",
        name="RAM Usage",
        fill="tozeroy"
    ))

    ram_fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Usage (%)",
        yaxis_range=[0, 100],
        height=300
    )

    st.plotly_chart(ram_fig, use_container_width=True)

dashboard()

st.divider()

st.subheader("Internet Monitoring")


st.subheader("Internet Monitoring")

network = check_internet()

col1, col2, col3 = st.columns(3)

with col1:
    if network["connected"]:
        st.metric("Internet Status", "Connected")
    else:
        st.metric("Internet Status", "Disconnected")

with col2:
    if network["latency"] is not None:
        st.metric(
            "Ping Latency",
            f'{network["latency"]} ms'
        )
    else:
        st.metric("Ping Latency", "N/A")

with col3:
    if network["connected"]:
        if network["latency"] < 50:
            quality = "Excellent"
        elif network["latency"] < 100:
            quality = "Good"
        else:
            quality = "Slow"
    else:
        quality = "Offline"

    st.metric("Connection Quality", quality)



st.subheader("Ping Latency History")

ping_fig = go.Figure()

ping_fig.add_trace(go.Scatter(
    x=list(st.session_state.timestamps),
    y=list(st.session_state.ping_history),
    mode="lines+markers",
    name="Ping",
    connectgaps=False
))

ping_fig.update_layout(
    xaxis_title="Time",
    yaxis_title="Latency (ms)",
    height=300
)

st.plotly_chart(
    ping_fig,
    use_container_width=True
)
