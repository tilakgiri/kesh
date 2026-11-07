
import streamlit as st
import psutil

# Page configuration
st.set_page_config(
    page_title="Personal PC & Network Monitor",
    page_icon="🥭",
    layout="wide"
)

# Dashboard title
st.title("Personal PC & Network Monitor")
st.caption("Real-time system and internet monitoring")

# System information
@st.fragment(run_every="5s")
def system_dashboard():

    st.subheader("System Overview")

    cpu_usage = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory()

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label="CPU Usage",
            value=f"{cpu_usage}%"
        )

    with col2:
        st.metric(
            label="RAM Usage",
            value=f"{ram.percent}%"
        )

    st.subheader("Internet Monitoring")

    col3, col4, col5 = st.columns(3)

    with col3:
        st.metric("Internet Status", "Coming Soon")

    with col4:
        st.metric("Ping", "Coming Soon")

    with col5:
        st.metric("Network Speed", "Coming Soon")


system_dashboard()

st.divider()

st.caption("Personal PC & Network Monitor | Version 1.0")
st.caption("Developed with Python and Streamlit")
