import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import feedparser
import io
from ta.momentum import RSIIndicator
import requests

st.set_page_config(page_title="Aktien & News Dashboard", layout="wide")

# Session state
if 'ticker_liste' not in st.session_state:
    st.session_state['ticker_liste'] = []
if 'kursdaten' not in st.session_state:
    st.session_state['kursdaten'] = pd.DataFrame()

# Sidebar-Navigation
seite = st.sidebar.selectbox("Navigation", ["📈 Aktienkurse", "📰 Finanznachrichten"])

# Seite 1: Aktienkurse
if seite == "📈 Aktienkurse":
    st.title("📈 Aktienkurs & Indikatoren")

    # Zeitraum
    tage_opt = {"Letzte 7 Tage":7,"Letzte 14 Tage":14,"Letzte 30 Tage":30,"Letzte 90 Tage":90}
    selected = st.selectbox("Zeitraum auswählen:", list(tage_opt.keys()))
    tage = tage_opt[selected]

    normieren = st.checkbox("📊 Kurse normieren (Start = 100)", value=True)
    indikator_sma = st.checkbox("SMA anzeigen (z. B. 20‑Tage Durchschnitt)", value=True)
    indikator_rsi = st.checkbox("RSI anzeigen (Perioden = 14)", value=True)

    # Aktienliste
    vordef = {"Apple (AAPL)": "AAPL","Microsoft (MSFT)": "MSFT","Tesla (TSLA)": "TSLA",
             "Amazon (AMZN)": "AMZN","Google (GOOGL)": "GOOGL","Meta (META)": "META","Nvidia (NVDA)": "NVDA"}

    auswahl = st.multiselect("Wähle Aktien:", list(vordef.keys()))
    manuell = st.text_input("Weitere Ticker (Komma‑getrennt, z. B. NFLX,INTC):").upper()

    ticker_liste = [vordef[a] for a in auswahl]
    if manuell:
        ticker_liste += [t.strip() for t in manuell.split(",") if t.strip()]
    st.session_state['ticker_liste'] = ticker_liste

    if ticker_liste:
        st.write(f"🔎 Zeige Daten für: {', '.join(ticker_liste)}")

        start = datetime.date.today() - datetime.timedelta(days=tage)
        df_all = pd.DataFrame()

        alerts = []
        for ticker in ticker_liste:
            df = yf.download(ticker, start=start, end=datetime.date.today())[["Close"]]
            df.rename(columns={"Close":ticker}, inplace=True)
            if normieren:
                df[ticker] = df[ticker] / df[ticker].iloc[0] * 100
            if indikator_sma:
                df[f"SMA_{ticker}"] = df[ticker].rolling(window=20).mean()
            if indikator_rsi:
                rsi = RSIIndicator(close=df[ticker], window=14).rsi()
                df[f"RSI_{ticker}"] = rsi
                latest_rsi = rsi.iloc[-1]
                if latest_rsi > 70:
                    alerts.append(f"{ticker}: RSI {latest_rsi:.1f} → überkauft")
                elif latest_rsi < 30:
                    alerts.append(f"{ticker}: RSI {latest_rsi:.1f} → überverkauft")
            df_all = df_all.join(df, how="outer") if not df_all.empty else df

        if not df_all.empty:
            st.line_chart(df_all[[col for col in df_all if not col.startswith("RSI_")]])

            st.session_state['kursdaten'] = df_all.copy()

            csv = df_all.reset_index().to_csv(index=False).encode('utf-8')
            st.download_button("📥 Kursdaten als CSV", data=csv, file_name="kurse.csv", mime="text/csv")
            
            if alerts:
                for msg in alerts:
                    st.warning(msg)
        else:
            st.warning("Keine Kursdaten gefunden.")
    else:
        st.info("Bitte Aktien auswählen oder Ticker eingeben.")

# Seite 2: Nachrichten
elif seite == "📰 Finanznachrichten":
    st.title("📰 Aktien‑News & API")

    tickers = st.session_state.get('ticker_liste', [])
    api_key = st.sidebar.text_input("NewsAPI‑Key", type="password")
    days = st.selectbox("Nur News der letzten ... Tage", [1,3,7,14,30], index=2)
    cutoff = datetime.datetime.now() - datetime.timedelta(days=days)

    if not tickers:
        st.info("Bitte zuerst bei 'Aktienkurse' Aktien wählen.")
    elif not api_key:
        st.warning("Bitte deinen NewsAPI‑Key eingeben (z. B. newsapi.org)")
    else:
        tabs = st.tabs(tickers)
        for idx, ticker in enumerate(tickers):
            with tabs[idx]:
                st.subheader(f"News zu {ticker}")
                url = f"https://newsapi.org/v2/everything?q={ticker}&language=en&apiKey={api_key}"
                resp = requests.get(url).json()
                if resp.get("articles"):
                    count = 0
                    for art in resp["articles"]:
                        published = datetime.datetime.fromisoformat(art["publishedAt"][:-1])
                        if published >= cutoff:
                            st.markdown(f"### {art['title']}")
                            st.write(published.strftime("%Y-%m-%d %H:%M"))
                            st.write(art.get("description", ""))
                            st.markdown(f"[🔗 Quelle]({art['url']})", unsafe_allow_html=True)
                            st.markdown("---")
                            count += 1
                    if count == 0:
                        st.info(f"Keine News in den letzten {days} Tagen.")
                else:
                    st.error("Fehler beim Laden der News oder keine Artikel.")


Von meinem iPhone gesendet

Am 04.08.2025 um 19:43 schrieb Gmx <heiko-le@gmx.de>:

﻿
import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import feedparser

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
        "Nvidia (NVDA)": "NVDA"
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
                    alle_kurse = alle_kurse.join(df, how="outer")
            except Exception as e:
                st.warning(f"Konnte Daten für {ticker} nicht laden: {e}")

        if not alle_kurse.empty:
            alle_kurse.reset_index(inplace=True)
            alle_kurse.set_index("Date", inplace=True)
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
                            st.subheader(eintrag.title)
                            st.write(published_time.strftime("%Y-%m-%d %H:%M"))
                            st.write(eintrag.summary)
                            st.markdown(f"[🔗 Zur Quelle]({eintrag.link})", unsafe_allow_html=True)
                            st.markdown("---")
                            count += 1
                    except:
                        continue

                if count == 0:
                    st.info(f"Keine aktuellen News in den letzten {news_tage} Tagen gefunden.")
            else:
                st.warning(f"Keine News gefunden für {ticker}.")



Von meinem iPhone gesendet

Am 04.08.2025 um 19:41 schrieb Gmx <heiko-le@gmx.de>:

﻿
import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import feedparser
import io
from ta.momentum import RSIIndicator
import requests

st.set_page_config(page_title="Aktien & News Dashboard", layout="wide")

# Session state
if 'ticker_liste' not in st.session_state:
    st.session_state['ticker_liste'] = []
if 'kursdaten' not in st.session_state:
    st.session_state['kursdaten'] = pd.DataFrame()

# Sidebar-Navigation
seite = st.sidebar.selectbox("Navigation", ["📈 Aktienkurse", "📰 Finanznachrichten"])

# Seite 1: Aktienkurse
if seite == "📈 Aktienkurse":
    st.title("📈 Aktienkurs & Indikatoren")

    # Zeitraum
    tage_opt = {"Letzte 7 Tage":7,"Letzte 14 Tage":14,"Letzte 30 Tage":30,"Letzte 90 Tage":90}
    selected = st.selectbox("Zeitraum auswählen:", list(tage_opt.keys()))
    tage = tage_opt[selected]

    normieren = st.checkbox("📊 Kurse normieren (Start = 100)", value=True)
    indikator_sma = st.checkbox("SMA anzeigen (z. B. 20‑Tage Durchschnitt)", value=True)
    indikator_rsi = st.checkbox("RSI anzeigen (Perioden = 14)", value=True)

    # Aktienliste
    vordef = {"Apple (AAPL)": "AAPL","Microsoft (MSFT)": "MSFT","Tesla (TSLA)": "TSLA",
             "Amazon (AMZN)": "AMZN","Google (GOOGL)": "GOOGL","Meta (META)": "META","Nvidia (NVDA)": "NVDA"}

    auswahl = st.multiselect("Wähle Aktien:", list(vordef.keys()))
    manuell = st.text_input("Weitere Ticker (Komma‑getrennt, z. B. NFLX,INTC):").upper()

    ticker_liste = [vordef[a] for a in auswahl]
    if manuell:
        ticker_liste += [t.strip() for t in manuell.split(",") if t.strip()]
    st.session_state['ticker_liste'] = ticker_liste

    if ticker_liste:
        st.write(f"🔎 Zeige Daten für: {', '.join(ticker_liste)}")

        start = datetime.date.today() - datetime.timedelta(days=tage)
        df_all = pd.DataFrame()

        alerts = []
        for ticker in ticker_liste:
            df = yf.download(ticker, start=start, end=datetime.date.today())[["Close"]]
            df.rename(columns={"Close":ticker}, inplace=True)
            if normieren:
                df[ticker] = df[ticker] / df[ticker].iloc[0] * 100
            if indikator_sma:
                df[f"SMA_{ticker}"] = df[ticker].rolling(window=20).mean()
            if indikator_rsi:
                rsi = RSIIndicator(close=df[ticker], window=14).rsi()
                df[f"RSI_{ticker}"] = rsi
                latest_rsi = rsi.iloc[-1]
                if latest_rsi > 70:
                    alerts.append(f"{ticker}: RSI {latest_rsi:.1f} → überkauft")
                elif latest_rsi < 30:
                    alerts.append(f"{ticker}: RSI {latest_rsi:.1f} → überverkauft")
            df_all = df_all.join(df, how="outer") if not df_all.empty else df

        if not df_all.empty:
            st.line_chart(df_all[[col for col in df_all if not col.startswith("RSI_")]])

            st.session_state['kursdaten'] = df_all.copy()

            csv = df_all.reset_index().to_csv(index=False).encode('utf-8')
            st.download_button("📥 Kursdaten als CSV", data=csv, file_name="kurse.csv", mime="text/csv")
            
            if alerts:
                for msg in alerts:
                    st.warning(msg)
        else:
            st.warning("Keine Kursdaten gefunden.")
    else:
        st.info("Bitte Aktien auswählen oder Ticker eingeben.")

# Seite 2: Nachrichten
elif seite == "📰 Finanznachrichten":
    st.title("📰 Aktien‑News & API")

    tickers = st.session_state.get('ticker_liste', [])
    api_key = st.sidebar.text_input("NewsAPI‑Key", type="password")
    days = st.selectbox("Nur News der letzten ... Tage", [1,3,7,14,30], index=2)
    cutoff = datetime.datetime.now() - datetime.timedelta(days=days)

    if not tickers:
        st.info("Bitte zuerst bei 'Aktienkurse' Aktien wählen.")
    elif not api_key:
        st.warning("Bitte deinen NewsAPI‑Key eingeben (z. B. newsapi.org)")
    else:
        tabs = st.tabs(tickers)
        for idx, ticker in enumerate(tickers):
            with tabs[idx]:
                st.subheader(f"News zu {ticker}")
                url = f"https://newsapi.org/v2/everything?q={ticker}&language=en&apiKey={api_key}"
                resp = requests.get(url).json()
                if resp.get("articles"):
                    count = 0
                    for art in resp["articles"]:
                        published = datetime.datetime.fromisoformat(art["publishedAt"][:-1])
                        if published >= cutoff:
                            st.markdown(f"### {art['title']}")
                            st.write(published.strftime("%Y-%m-%d %H:%M"))
                            st.write(art.get("description", ""))
                            st.markdown(f"[🔗 Quelle]({art['url']})", unsafe_allow_html=True)
                            st.markdown("---")
                            count += 1
                    if count == 0:
                        st.info(f"Keine News in den letzten {days} Tagen.")
                else:
                    st.error("Fehler beim Laden der News oder keine Artikel.")
