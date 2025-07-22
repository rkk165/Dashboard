
# Sleep Apnea Monitoring Dashboard (Web App)
# Requirements: streamlit, pandas, matplotlib, plotly, openpyxl

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import os
from io import StringIO
from datetime import timedelta, date

HISTORY_FILE = "history.csv"

st.set_page_config(page_title="Sleep Apnea Dashboard", layout="centered")
st.title("📊 Sleep Apnea Monitoring Dashboard")

st.markdown("Upload your O2Ring CSV file. The app will estimate AHI, ODI, total desaturation events, and track history.")

uploaded_file = st.file_uploader("Upload O2Ring CSV", type="csv")

@st.cache_data
def process_o2ring(file):
    df = pd.read_csv(file)
    df["Oxygen Level"] = pd.to_numeric(df["Oxygen Level"].str.strip(), errors='coerce')
    df["Pulse Rate"] = pd.to_numeric(df["Pulse Rate"].str.strip(), errors='coerce')
    df["Time"] = pd.to_datetime(df["Time"], errors='coerce', dayfirst=True)

    df = df.dropna(subset=["Oxygen Level", "Time"])
    df = df.sort_values("Time").reset_index(drop=True)

    # Calculate desaturation events (drops ≥3% from previous reading)
    desat_events = (df["Oxygen Level"].diff() <= -3).sum()

    # Calculate monitoring duration in hours
    duration_hours = (df["Time"].iloc[-1] - df["Time"].iloc[0]).total_seconds() / 3600
    duration_hours = max(duration_hours, 0.1)

    # Estimate ODI
    odi = round(desat_events / duration_hours, 2)

    # Estimate AHI
    ahi = round(odi * 0.75, 2)

    summary = {
        "Date": df["Time"].dt.date.min(),
        "Monitoring Time (hrs)": round(duration_hours, 2),
        "Mean SpO2": round(df["Oxygen Level"].mean(), 1),
        "Min SpO2": df["Oxygen Level"].min(),
        "Total Desaturations": desat_events,
        "ODI (events/hr)": odi,
        "Estimated AHI (events/hr)": ahi,
    }
    return summary, df

def update_history(new_entry):
    if os.path.exists(HISTORY_FILE):
        history = pd.read_csv(HISTORY_FILE)
    else:
        history = pd.DataFrame()

    history = pd.concat([history, pd.DataFrame([new_entry])], ignore_index=True)
    history.drop_duplicates(subset=["Date"], keep="last", inplace=True)
    history = history.sort_values("Date")
    history.to_csv(HISTORY_FILE, index=False)
    return history

if uploaded_file is not None:
    summary, df = process_o2ring(uploaded_file)
    st.success("File processed successfully!")

    st.subheader("📈 Estimated Sleep Apnea Metrics")
    st.write(summary)

    history_df = update_history(summary)

    st.subheader("📅 Historical Trend Table")
    st.dataframe(history_df)

    st.subheader("📊 Trend Graphs")
    fig = px.line(history_df, x="Date", y=["Estimated AHI (events/hr)", "ODI (events/hr)", "Total Desaturations"],
                  title="Sleep Apnea Metrics Over Time")
    st.plotly_chart(fig, use_container_width=True)

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
