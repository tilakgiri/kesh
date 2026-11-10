
import streamlit as st
import psutil
import plotly.graph_objects as go
import time

from collections import deque
from datetime import datetime
from pathlib import Path

from monitor.network_monitor import check_internet


# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="KESH | PC & Network Monitor",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =====================================================
# 2. LOAD CUSTOM CSS
# =====================================================

css_path = Path(__file__).parent / "assets" / "style.css"

with open(css_path, "r", encoding="utf-8") as file:
    st.markdown(
        f"<style>{file.read()}</style>",
        unsafe_allow_html=True
    )


# =====================================================
# 3. SESSION STATE INITIALIZATION
# =====================================================

# Store the last 30 monitoring readings.

if "timestamps" not in st.session_state:
    st.session_state.timestamps = deque(maxlen=30)

if "cpu_history" not in st.session_state:
    st.session_state.cpu_history = deque(maxlen=30)

if "ram_history" not in st.session_state:
    st.session_state.ram_history = deque(maxlen=30)

if "ping_history" not in st.session_state:
    st.session_state.ping_history = deque(maxlen=30)

if "download_history" not in st.session_state:
    st.session_state.download_history = deque(maxlen=30)

if "upload_history" not in st.session_state:
    st.session_state.upload_history = deque(maxlen=30)


# Previous network readings for speed calculations.

if "previous_received" not in st.session_state:
    st.session_state.previous_received = None

if "previous_sent" not in st.session_state:
    st.session_state.previous_sent = None

if "previous_time" not in st.session_state:
    st.session_state.previous_time = None


# =====================================================
# 4. SIDEBAR
# =====================================================

with st.sidebar:

    st.title("🌐 KESH")

    st.caption("PERSONAL PC & NETWORK MONITOR")

    st.divider()

    st.subheader("Navigation")

    page = st.radio(
        "Navigate",
        [
            "Overview",
            "System Performance",
            "Network Monitoring"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.subheader("Settings")

    st.write("Automatic Refresh")

    st.info("Refresh interval: 5 seconds")

    st.divider()

    st.caption("KESH | Version 2.1")
    st.caption("Built with Python and Streamlit")


# =====================================================
# 5. DASHBOARD HEADER
# =====================================================

st.title("KESH - Network Command Center")

st.caption(
    "Monitor your computer's performance and internet connection."
)


# =====================================================
# 6. MAIN MONITORING FUNCTION
# =====================================================

@st.fragment(run_every="5s")
def dashboard():

    # -------------------------------------------------
    # A. COLLECT SYSTEM INFORMATION
    # -------------------------------------------------

    cpu = psutil.cpu_percent(interval=0.2)

    ram = psutil.virtual_memory()

    # -------------------------------------------------
    # B. CHECK INTERNET CONNECTIVITY
    # -------------------------------------------------

    network = check_internet()

    # -------------------------------------------------
    # C. COLLECT NETWORK TRAFFIC
    # -------------------------------------------------

    net_stats = psutil.net_io_counters()

    current_received = net_stats.bytes_recv

    current_sent = net_stats.bytes_sent

    current_time = time.monotonic()

    download_speed = 0.0

    upload_speed = 0.0

    # Calculate network speed using previous readings.

    if st.session_state.previous_time is not None:

        elapsed = (
            current_time -
            st.session_state.previous_time
        )

        if elapsed > 0:

            received_difference = (
                current_received -
                st.session_state.previous_received
            )

            sent_difference = (
                current_sent -
                st.session_state.previous_sent
            )

            # Convert bytes per second into Mbps.

            if received_difference >= 0:

                download_speed = (
                    received_difference * 8
                    / elapsed
                    / 1_000_000
                )

            if sent_difference >= 0:

                upload_speed = (
                    sent_difference * 8
                    / elapsed
                    / 1_000_000
                )

    # Save current readings for the next calculation.

    st.session_state.previous_received = current_received

    st.session_state.previous_sent = current_sent

    st.session_state.previous_time = current_time

    # -------------------------------------------------
    # D. SAVE MONITORING HISTORY
    # -------------------------------------------------

    timestamp = datetime.now().strftime("%H:%M:%S")

    st.session_state.timestamps.append(timestamp)

    st.session_state.cpu_history.append(cpu)

    st.session_state.ram_history.append(ram.percent)

    st.session_state.ping_history.append(
        network["latency"]
    )

    st.session_state.download_history.append(
        download_speed
    )

    st.session_state.upload_history.append(
        upload_speed
    )

    # -------------------------------------------------
    # E. CONNECTION STATUS
    # -------------------------------------------------

    st.subheader("Connection Status")

    status_col1, status_col2 = st.columns(2)

    with status_col1:

        if network["connected"]:

            st.success("● INTERNET CONNECTED")

        else:

            st.error("● INTERNET DISCONNECTED")

    with status_col2:

        st.caption(f"Last updated: {timestamp}")

    st.divider()

    # =================================================
    # 7. OVERVIEW PAGE
    # =================================================

    if page == "Overview":

        st.subheader("System Overview")

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric(
            "CPU Usage",
            f"{cpu:.1f}%"
        )

        col2.metric(
            "RAM Usage",
            f"{ram.percent:.1f}%"
        )

        col3.metric(
            "Ping Latency",
            f'{network["latency"]:.1f} ms'
            if network["latency"] is not None
            else "N/A"
        )

        col4.metric(
            "Download",
            f"{download_speed:.2f} Mbps"
        )

        col5.metric(
            "Upload",
            f"{upload_speed:.2f} Mbps"
        )

        st.divider()

        # System charts

        st.subheader("System Performance")

        chart1, chart2 = st.columns(2)

        with chart1:

            cpu_fig = go.Figure()

            cpu_fig.add_trace(go.Scatter(
                x=list(st.session_state.timestamps),
                y=list(st.session_state.cpu_history),
                mode="lines",
                name="CPU",
                line=dict(
                    color="#38bdf8",
                    width=3
                ),
                fill="tozeroy"
            ))

            cpu_fig.update_layout(
                title="CPU Utilization",
                yaxis_title="Usage (%)",
                yaxis_range=[0, 100],
                height=320,
                template="plotly_dark",
                paper_bgcolor="#152238",
                plot_bgcolor="#152238"
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
                line=dict(
                    color="#a78bfa",
                    width=3
                ),
                fill="tozeroy"
            ))

            ram_fig.update_layout(
                title="RAM Utilization",
                yaxis_title="Usage (%)",
                yaxis_range=[0, 100],
                height=320,
                template="plotly_dark",
                paper_bgcolor="#152238",
                plot_bgcolor="#152238"
            )

            st.plotly_chart(
                ram_fig,
                use_container_width=True
            )

        # Network summary

        st.divider()

        st.subheader("Network Performance")

        ping_col, download_col, upload_col = st.columns(3)

        ping_col.metric(
            "Latency",
            f'{network["latency"]} ms'
            if network["latency"] is not None
            else "N/A"
        )

        download_col.metric(
            "Download",
            f"{download_speed:.2f} Mbps"
        )

        upload_col.metric(
            "Upload",
            f"{upload_speed:.2f} Mbps"
        )


    # =================================================
    # 8. SYSTEM PERFORMANCE PAGE
    # =================================================

    elif page == "System Performance":

        st.subheader("System Performance")

        col1, col2, col3 = st.columns(3)

        col1.metric("CPU Usage", f"{cpu:.1f}%")

        col2.metric("RAM Usage", f"{ram.percent:.1f}%")

        col3.metric(
            "Available RAM",
            f"{ram.available / (1024 ** 3):.2f} GB"
        )

        st.divider()

        # CPU graph

        cpu_fig = go.Figure()

        cpu_fig.add_trace(go.Scatter(
            x=list(st.session_state.timestamps),
            y=list(st.session_state.cpu_history),
            mode="lines+markers",
            name="CPU",
            line=dict(color="#38bdf8", width=3),
            fill="tozeroy"
        ))

        cpu_fig.update_layout(
            title="CPU Usage History",
            xaxis_title="Time",
            yaxis_title="Usage (%)",
            yaxis_range=[0, 100],
            height=350,
            template="plotly_dark",
            paper_bgcolor="#152238",
            plot_bgcolor="#152238"
        )

        st.plotly_chart(
            cpu_fig,
            use_container_width=True
        )

        # RAM graph

        ram_fig = go.Figure()

        ram_fig.add_trace(go.Scatter(
            x=list(st.session_state.timestamps),
            y=list(st.session_state.ram_history),
            mode="lines+markers",
            name="RAM",
            line=dict(color="#a78bfa", width=3),
            fill="tozeroy"
        ))

        ram_fig.update_layout(
            title="RAM Usage History",
            xaxis_title="Time",
            yaxis_title="Usage (%)",
            yaxis_range=[0, 100],
            height=350,
            template="plotly_dark",
            paper_bgcolor="#152238",
            plot_bgcolor="#152238"
        )

        st.plotly_chart(
            ram_fig,
            use_container_width=True
        )


    # =================================================
    # 9. NETWORK MONITORING PAGE
    # =================================================

    elif page == "Network Monitoring":

        st.subheader("Network Overview")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Ping Latency",
            f'{network["latency"]} ms'
            if network["latency"] is not None
            else "N/A"
        )

        col2.metric(
            "Download Speed",
            f"{download_speed:.2f} Mbps"
        )

        col3.metric(
            "Upload Speed",
            f"{upload_speed:.2f} Mbps"
        )

        # Connection quality

        st.divider()

        st.subheader("Connection Quality")

        if not network["connected"]:

            st.error("Unable to reach Google DNS (8.8.8.8).")

        elif network["latency"] < 50:

            st.success("Excellent connection quality")

        elif network["latency"] < 100:

            st.info("Good connection quality")

        else:

            st.warning("High network latency")

        # Ping graph

        st.divider()

        st.subheader("Ping Latency History")

        ping_fig = go.Figure()

        ping_fig.add_trace(go.Scatter(
            x=list(st.session_state.timestamps),
            y=list(st.session_state.ping_history),
            mode="lines+markers",
            name="Ping",
            connectgaps=False,
            line=dict(
                color="#34d399",
                width=3
            )
        ))

        ping_fig.update_layout(
            title="Network Latency",
            xaxis_title="Time",
            yaxis_title="Latency (ms)",
            height=320,
            template="plotly_dark",
            paper_bgcolor="#152238",
            plot_bgcolor="#152238"
        )

        st.plotly_chart(
            ping_fig,
            use_container_width=True
        )

        # Download graph

        st.divider()

        st.subheader("Download Traffic")

        download_fig = go.Figure()

        download_fig.add_trace(go.Scatter(
            x=list(st.session_state.timestamps),
            y=list(st.session_state.download_history),
            mode="lines+markers",
            name="Download",
            line=dict(
                color="#38bdf8",
                width=3
            ),
            fill="tozeroy"
        ))

        download_fig.update_layout(
            title="Download Speed History",
            xaxis_title="Time",
            yaxis_title="Speed (Mbps)",
            height=320,
            template="plotly_dark",
            paper_bgcolor="#152238",
            plot_bgcolor="#152238"
        )

        st.plotly_chart(
            download_fig,
            use_container_width=True
        )

        # Upload graph

        st.divider()

        st.subheader("Upload Traffic")

        upload_fig = go.Figure()

        upload_fig.add_trace(go.Scatter(
            x=list(st.session_state.timestamps),
            y=list(st.session_state.upload_history),
            mode="lines+markers",
            name="Upload",
            line=dict(
                color="#a78bfa",
                width=3
            ),
            fill="tozeroy"
        ))

        upload_fig.update_layout(
            title="Upload Speed History",
            xaxis_title="Time",
            yaxis_title="Speed (Mbps)",
            height=320,
            template="plotly_dark",
            paper_bgcolor="#152238",
            plot_bgcolor="#152238"
        )

        st.plotly_chart(
            upload_fig,
            use_container_width=True
        )

        st.caption(
            "Traffic is measured across all network interfaces."
        )


# =====================================================
# 10. RUN DASHBOARD
# =====================================================

dashboard()


# =====================================================
# 11. FOOTER
# =====================================================

st.divider()

st.caption(
    "KESH | Personal PC & Network Monitor | Version 2.1"
)
