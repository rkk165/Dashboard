
# Sleep Apnea Monitoring Dashboard (Web App)
# Requirements: streamlit, pandas, matplotlib, plotly, openpyxl

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from io import StringIO

st.set_page_config(page_title="Sleep Apnea Dashboard", layout="centered")
st.title("📊 Sleep Apnea Monitoring Dashboard")

st.markdown("Upload your O2Ring CSV file and enter your AHI and ODI values.")

uploaded_file = st.file_uploader("Upload O2Ring CSV", type="csv")
ahi_input = st.number_input("Enter AHI (Apnea-Hypopnea Index)", min_value=0.0, step=0.1)
odi_input = st.number_input("Enter ODI (Oxygen Desaturation Index)", min_value=0.0, step=0.1)

@st.cache_data
def process_o2ring(file):
    df = pd.read_csv(file)
    df["Oxygen Level"] = pd.to_numeric(df["Oxygen Level"].str.strip(), errors='coerce')
    df["Pulse Rate"] = pd.to_numeric(df["Pulse Rate"].str.strip(), errors='coerce')
    df["Time"] = pd.to_datetime(df["Time"], errors='coerce', dayfirst=True)
    desats = (df["Oxygen Level"].diff() <= -3).sum()
    summary = {
        "Date": df["Time"].dt.date.min(),
        "Mean SpO2": round(df["Oxygen Level"].mean(), 1),
        "Min SpO2": df["Oxygen Level"].min(),
        "Desaturation Events (≥3%)": desats,
        "AHI": ahi_input,
        "ODI": odi_input,
    }
    return summary, df

if uploaded_file is not None:
    summary, df = process_o2ring(uploaded_file)
    st.success("File processed successfully!")
    st.subheader("📈 Summary Metrics")
    st.write(summary)

    st.subheader("📉 Oxygen Level Trend")
    fig = px.line(df, x="Time", y="Oxygen Level", title="SpO₂ Over Time")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("❤️ Pulse Rate Trend")
    fig2 = px.line(df, x="Time", y="Pulse Rate", title="Pulse Rate Over Time")
    st.plotly_chart(fig2, use_container_width=True)

    st.download_button(
        label="Download Summary as CSV",
        data=pd.DataFrame([summary]).to_csv(index=False),
        file_name="sleep_apnea_summary.csv",
        mime="text/csv"
    )
