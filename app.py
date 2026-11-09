
import streamlit as st
import psutil
import plotly.graph_objects as go

from collections import deque
from datetime import datetime
from pathlib import Path

from monitor.network_monitor import check_internet

# -----------------------------
# PAGE CONFIGURATION
# -----------------------------

st.set_page_config(
    page_title="Nexus | Network Monitor",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# LOAD CUSTOM CSS
# -----------------------------

css_path = Path(__file__).parent / "assets" / "style.css"

with open(css_path, "r", encoding="utf-8") as file:
    st.markdown(
        f"<style>{file.read()}</style>",
        unsafe_allow_html=True
    )

# -----------------------------
# SESSION STATE
# -----------------------------

if "timestamps" not in st.session_state:
    st.session_state.timestamps = deque(maxlen=30)
    st.session_state.cpu_history = deque(maxlen=30)
    st.session_state.ram_history = deque(maxlen=30)
    st.session_state.ping_history = deque(maxlen=30)

# -----------------------------
# SIDEBAR
# -----------------------------

with st.sidebar:

    st.title("🌐 NEXUS")
    st.caption("PERSONAL NETWORK MONITOR")

    st.divider()

    st.subheader("Navigation")

    page = st.radio(
        "Navigate",
        ["Overview", "System Performance", "Network Monitoring"],
        label_visibility="collapsed"
    )

    st.divider()

    st.subheader("Settings")

    st.write("Refresh interval")
    st.caption("Current interval: 5 seconds")

    st.divider()

    st.caption("Version 2.0")
    st.caption("Developed with Python")

# -----------------------------
# DASHBOARD HEADER
# -----------------------------

st.title("Network Command Center")

st.caption(
    "Monitor your PC performance and internet connection."
)

@st.fragment(run_every="5s")
def dashboard():

    # Collect monitoring data
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory()
    network = check_internet()

    now = datetime.now().strftime("%H:%M:%S")

    # Store history
    st.session_state.timestamps.append(now)
    st.session_state.cpu_history.append(cpu)
    st.session_state.ram_history.append(ram.percent)
    st.session_state.ping_history.append(network["latency"])

    # -----------------------------
    # STATUS BAR
    # -----------------------------

    status_col1, status_col2 = st.columns(2)

    with status_col1:
        if network["connected"]:
            st.success("● INTERNET CONNECTED")
        else:
            st.error("● INTERNET DISCONNECTED")

    with status_col2:
        st.caption(f"Last updated: {now}")

    st.divider()

    # -----------------------------
    # OVERVIEW CARDS
    # -----------------------------

    st.subheader("System Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("CPU Usage", f"{cpu:.1f}%")
    c2.metric("RAM Usage", f"{ram.percent:.1f}%")
    c3.metric(
        "Available RAM",
        f"{ram.available / (1024 ** 3):.2f} GB"
    )

    c4.metric(
        "Ping Latency",
        f'{network["latency"]} ms'
        if network["latency"] is not None
        else "N/A"
    )

    st.divider()

    # -----------------------------
    # PERFORMANCE CHARTS
    # -----------------------------

    if page == "Overview" or page == "System Performance":

        st.subheader("System Performance")

        chart1, chart2 = st.columns(2)

        with chart1:

            cpu_fig = go.Figure()

            cpu_fig.add_trace(go.Scatter(
                x=list(st.session_state.timestamps),
                y=list(st.session_state.cpu_history),
                mode="lines",
                name="CPU",
                line=dict(color="#38bdf8", width=3),
                fill="tozeroy"
            ))

            cpu_fig.update_layout(
                title="CPU Utilization",
                yaxis_range=[0, 100],
                yaxis_title="Usage (%)",
                height=320,
                template="plotly_dark",
                paper_bgcolor="#152238",
                plot_bgcolor="#152238",
                margin=dict(l=20, r=20, t=50, b=20)
            )

            st.plotly_chart(
                cpu_fig,
                use_container_width=True
            )

        with chart2:

            ram_fig = go.Figure()

            ram_fig.add_trace(go.Scatter(
                x=list(st.session_state.timestamps),
                y=list(st.session_state.ram_history),
                mode="lines",
                name="RAM",
                line=dict(color="#a78bfa", width=3),
                fill="tozeroy"
            ))

            ram_fig.update_layout(
                title="Memory Utilization",
                yaxis_range=[0, 100],
                yaxis_title="Usage (%)",
                height=320,
                template="plotly_dark",
                paper_bgcolor="#152238",
                plot_bgcolor="#152238",
                margin=dict(l=20, r=20, t=50, b=20)
            )

            st.plotly_chart(
                ram_fig,
                use_container_width=True
            )

    # -----------------------------
    # NETWORK MONITORING
    # -----------------------------

    if page == "Overview" or page == "Network Monitoring":

        st.divider()
        st.subheader("Network Performance")

        if network["connected"]:

            if network["latency"] < 50:
                st.success("Connection quality: Excellent")
            elif network["latency"] < 100:
                st.info("Connection quality: Good")
            else:
                st.warning("Connection quality: High latency")

        else:
            st.error("Unable to reach monitoring server.")

        ping_fig = go.Figure()

        ping_fig.add_trace(go.Scatter(
            x=list(st.session_state.timestamps),
            y=list(st.session_state.ping_history),
            mode="lines+markers",
            name="Ping",
            connectgaps=False,
            line=dict(color="#34d399", width=3)
        ))

        ping_fig.update_layout(
            title="Network Latency History",
            yaxis_title="Latency (ms)",
            height=320,
            template="plotly_dark",
            paper_bgcolor="#152238",
            plot_bgcolor="#152238",
            margin=dict(l=20, r=20, t=50, b=20)
        )

        st.plotly_chart(
            ping_fig,
            use_container_width=True
        )

        st.caption("Monitoring destination: Google DNS (8.8.8.8)")

    st.divider()

    st.caption(
        "NEXUS Network Monitor | Built with Python and Streamlit"
    )


dashboard()
