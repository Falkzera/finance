import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gastos WhatsApp", layout="wide")

st.title("📊 Controle de Gastos via WhatsApp")

try:
    df = pd.read_csv("gastos.csv")
    df["data"] = pd.to_datetime(df["data"])

    st.subheader("Tabela de gastos")
    st.dataframe(df.sort_values("data", ascending=False), use_container_width=True)

    total = df["valor"].sum()
    st.metric("💰 Total gasto", f"R$ {total:.2f}")

    st.subheader("Gastos por item")
    st.bar_chart(df.groupby("item")["valor"].sum())

    st.subheader("Gastos ao longo do tempo")
    df_diario = df.groupby(df["data"].dt.date)["valor"].sum()
    st.line_chart(df_diario)

except FileNotFoundError:
    st.warning("Ainda não há dados. Envie um gasto pelo WhatsApp!")
