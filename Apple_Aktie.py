import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import feedparser
from googletrans import Translator

st.set_page_config(page_title="Aktien & News", layout="wide")

# SESSION STATE: Ticker-Auswahl merken
if 'ticker_liste' not in st.session_state:
    st.session_state['ticker_liste'] = []

# Sidebar-Navigation
seite = st.sidebar.selectbox(
    "Navigation",
    ["📈 Aktienkurse", "📰 Finanznachrichten"]
)

# ----------------------------------------
# 📰 SEITE 2: Finanznachrichten
# ----------------------------------------
elif seite == "📰 Finanznachrichten":
    st.title("📰 Nachrichten zu gewählten Aktien")

    ticker_liste = st.session_state.get('ticker_liste', [])

    if not ticker_liste:
        st.info("⚠️ Bitte zuerst im Reiter '📈 Aktienkurse' ein oder mehrere Ticker auswählen.")
    else:
        # Zeitraumfilter für Nachrichten
        news_tage = st.selectbox("Nur Nachrichten aus den letzten ...", [1, 3, 7, 14, 30], index=2)
        grenze_datum = datetime.datetime.now() - datetime.timedelta(days=news_tage)

        # Initialisieren des Translators
        translator = Translator()

        for ticker in ticker_liste:
            st.header(f"📰 News zu {ticker}")

            rss_url = f"https://finance.yahoo.com/rss/headline?s={ticker}"
            feed = feedparser.parse(rss_url)

            if feed.entries:
                count = 0
                for eintrag in feed.entries:
                    try:
                        published_time = datetime.datetime(*eintrag.published_parsed[:6])
                        if published_time >= grenze_datum:
                            # Übersetze den Titel und die Zusammenfassung ins Deutsche
                            title_translated = translator.translate(eintrag.title, src='en', dest='de').text
                            summary_translated = translator.translate(eintrag.summary, src='en', dest='de').text

                            st.subheader(title_translated)
                            st.write(published_time.strftime("%Y-%m-%d %H:%M"))
                            st.write(summary_translated)
                            st.markdown(f"[🔗 Zur Quelle]({eintrag.link})", unsafe_allow_html=True)
                            st.markdown("---")
                            count += 1
                    except:
                        continue

                if count == 0:
                    st.info(f"Keine aktuellen News in den letzten {news_tage} Tagen gefunden.")
            else:
                st.warning(f"Keine News gefunden für {ticker}.")
