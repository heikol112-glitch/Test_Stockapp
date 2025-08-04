import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt

st.title("Apple Aktienkurs")

ticker_symbol = "AAPL"
daten = yf.download(ticker_symbol, start="2025-01-01", end="2025-08-02")

st.write("Daten (Ausschnitt):")
st.dataframe(daten.tail())

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(daten['Close'])
ax.set_title(f'{ticker_symbol} Aktienkurs')
ax.set_xlabel('Datum')
ax.set_ylabel('Schlusskurs')

st.pyplot(fig)
