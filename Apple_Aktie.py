import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime  # Importieren für aktuelles Datum

end_date = datetime.today().strftime('%Y-%m-%d')  # heute im Format JJJJ-MM-TT

st.title("Plascred Aktienkurs")

ticker_symbol = "XV2.F"
daten = yf.download(ticker_symbol, start="2025-01-01", end=end_date)

st.write("Daten (Ausschnitt):")
st.dataframe(daten.tail())

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(daten['Close'])
ax.set_title(f'{ticker_symbol} Aktienkurs')
ax.set_xlabel('Datum')
ax.set_ylabel('Schlusskurs')

st.pyplot(fig)
