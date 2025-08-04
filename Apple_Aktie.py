import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import feedparser
import asyncio
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
# 📈 SEITE 1: Aktienkurse
# ----------------------------------------
if seite == "📈 Aktienkurse":
    st.title("📈 Aktienkurs-Vergleich")

    # Zeitraum-Auswahl
    tage_optionen = {
        "Letzte 7 Tage": 7,
        "Letzte 14 Tage": 14,
        "Letzte 30 Tage": 30,
        "Letzte 90 Tage": 90
    }
    ausgewählter_zeitraum = st.selectbox("Zeitraum auswählen:", list(tage_optionen.keys()))
    tage = tage_optionen[ausgewählter_zeitraum]

    # Normierungsschalter
    normieren = st.checkbox("📊 Kurse normieren (Start = 100)", value=True)

    # Liste vordefinierter Aktien
    vordefinierte_aktien = {
        "Apple (AAPL)": "AAPL",
        "Microsoft (MSFT)": "MSFT",
        "Tesla (TSLA)": "TSLA",
        "Amazon (AMZN)": "AMZN",
        "Google (GOOGL)": "GOOGL",
        "Meta (META)": "META",
        "Nvidia (NVDA)": "NVDA",
        "PlasCred Circular Innovations Inc": "XV2.F"
    }

    auswahl = st.multiselect(
        "Wähle ein oder mehrere Unternehmen aus:",
        options=list(vordefinierte_aktien.keys())
    )

    manuelle_ticker = st.text_input(
        "Weitere Ticker manuell eingeben (durch Komma getrennt, z. B. NFLX,INTC):"
    ).upper()

    # Tickerliste zusammenbauen
    ticker_liste = [vordefinierte_aktien[aktie] for aktie in auswahl]
    if manuelle_ticker:
        zusätzliche = [t.strip() for t in manuelle_ticker.split(",") if t.strip()]
        ticker_liste.extend(zusätzliche)

    # Speichern für Nachrichtenansicht
    st.session_state['ticker_liste'] = ticker_liste

    if ticker_liste:
        st.write(f"🔎 Zeige Kursverläufe für: {', '.join(ticker_liste)}")

        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=tage)

        alle_kurse = pd.DataFrame()

        for ticker in ticker_liste:
            try:
                df = yf.download(ticker, start=start_date, end=end_date)[['Close']]
                df.rename(columns={"Close": ticker}, inplace=True)
                if normieren:
                    df[ticker] = (df[ticker] / df[ticker].iloc[0]) * 100
                if alle_kurse.empty:
                    alle_kurse = df
                else:
                    alle_kurse = pd.concat([alle_kurse, df], axis=1)  # concat statt join
            except Exception as e:
                st.warning(f"Konnte Daten für {ticker} nicht laden: {e}")

        if not alle_kurse.empty:
            alle_kurse.reset_index(inplace=True)
            alle_kurse.set_index("Date", inplace=True)

            # Falls MultiIndex in den Spalten vorhanden ist, flach machen
            if isinstance(alle_kurse.columns, pd.MultiIndex):
                alle_kurse.columns = ['_'.join(col).strip() for col in alle_kurse.columns.values]

            st.line_chart(alle_kurse)
        else:
            st.warning("Keine gültigen Kursdaten gefunden.")
    else:
        st.info("Bitte wähle mindestens eine Aktie aus oder gib Ticker ein.")

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

        async def get_translated_text(text, src='en', dest='de'):
            translator = Translator()
            # Asynchron übersetzen
            translated = await asyncio.to_thread(translator.translate, text, src=src, dest=dest)
            return translated.text

        async def display_news():
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
                                # Asynchrone Übersetzung der Titel und Zusammenfassungen
                                translated_title = await get_translated_text(eintrag.title)
                                translated_summary = await get_translated_text(eintrag.summary)

                                st.subheader(translated_title)
                                st.write(published_time.strftime("%Y-%m-%d %H:%M"))
                                st.write(translated_summary)
                                st.markdown(f"[🔗 Zur Quelle]({eintrag.link})", unsafe_allow_html=True)
                                st.markdown("---")
                                count += 1
                        except Exception as e:
                            st.warning(f"Fehler bei der Verarbeitung einer Nachricht: {e}")
                            continue

                    if count == 0:
                        st.info(f"Keine aktuellen News in den letzten {news_tage} Tagen gefunden.")
                else:
                    st.warning(f"Keine News gefunden für {ticker}.")

        # Eventloop starten und Nachrichten anzeigen
        asyncio.run(display_news())
