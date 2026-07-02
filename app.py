# ImmoPilot - Streamlit UI für den KI-gestützten Mieterservice
#
# Seiten:
# - Mieterportal: öffentliche Seite für Anfragen
# - Admin-Login: Passwortschutz für Mitarbeitende
# - Dashboard: KPIs, Charts, Human-in-the-Loop
# - Copilot: Echtzeit-Unterstützung für Mitarbeitende
# - Wissensbasis: Dokumentations-Log und FAQ-Vorschläge

import streamlit as st
import pandas as pd
import os
from datetime import datetime
from agent import SupportAgent
from agents.copilot_agent import CopilotAgent
from ingest import load_and_index

if not os.path.exists("./chroma_db"):
    load_and_index()

# Muss als erster Streamlit-Befehl stehen
st.set_page_config(
    page_title="ImmoPilot",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.hero {
    background: linear-gradient(135deg, #1B2A4A 0%, #2D4270 100%);
    border-radius: 16px; padding: 2.5rem 2rem; margin-bottom: 2rem;
}
.hero h1 { font-size: 2rem; font-weight: 600; margin: 0 0 0.5rem; color: white; }
.hero p { font-size: 1rem; opacity: 0.75; margin: 0; color: white; }
.card { background: white; border-radius: 12px; padding: 1.5rem; border: 1px solid #E8EAF0; margin-bottom: 1rem; }
.metric-card { background: white; border-radius: 12px; padding: 1.25rem; border: 1px solid #E8EAF0; text-align: center; }
.metric-label { font-size: 12px; color: #8A92A6; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
.metric-value { font-size: 2rem; font-weight: 600; color: #1B2A4A; }
.metric-sub { font-size: 12px; margin-top: 4px; }
.answer-box { background: #F0F4FF; border-left: 4px solid #2D4270; border-radius: 0 8px 8px 0; padding: 1.25rem 1.5rem; font-size: 0.95rem; line-height: 1.7; color: #2D3748; }
.escalate-box { background: #FFF8E1; border-left: 4px solid #F59E0B; border-radius: 0 8px 8px 0; padding: 1rem 1.25rem; font-size: 0.9rem; color: #92400E; margin-bottom: 1rem; }
/* Prioritäts-Badges: P1=rot, P2=gelb, P3=blau */
.p1-badge { background: #FDECEA; color: #C0392B; padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.p2-badge { background: #FEF8E7; color: #B7791F; padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.p3-badge { background: #E8F0FE; color: #1B4DA8; padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.section-title { font-size: 1.1rem; font-weight: 600; color: #1B2A4A; margin-bottom: 1rem; }
.source-pill { display: inline-block; background: #F0F2F5; color: #4A5568; border-radius: 20px; padding: 4px 12px; font-size: 12px; margin: 3px; }
.faq-card { background: #F8FAFF; border: 1px solid #D0DCFF; border-radius: 10px; padding: 1rem; margin-bottom: 0.75rem; }
.faq-relevanz { font-size: 11px; color: #4A5568; float: right; }
.hint-box { background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 8px; padding: 0.75rem 1rem; font-size: 13px; color: #92400E; margin-bottom: 0.5rem; }
div[data-testid="stButton"] > button { background: #2D4270; color: white; border: none; border-radius: 8px; padding: 0.6rem 1.5rem; font-weight: 500; }
div[data-testid="stButton"] > button:hover { background: #1B2A4A; color: white; }
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# Session State initialisieren - wird nur beim ersten Laden gesetzt
for key, val in [("admin_logged_in", False), ("page", "mieter"),
                 ("last_result", None), ("ticket_status", {})]:
    if key not in st.session_state:
        st.session_state[key] = val

ADMIN_PASSWORD = "admin123"
LOG_PATH = "logs/queries.csv"
DOC_LOG = "logs/dokumentation.csv"
FAQ_LOG = "logs/faq_vorschlaege.csv"


# Agenten einmalig laden und cachen
@st.cache_resource
def load_agent():
    return SupportAgent()

@st.cache_resource
def load_copilot():
    return CopilotAgent()


agent = load_agent()
copilot = load_copilot()


def load_logs(path):
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path)


def priority_badge(p):
    cls = {"P1": "p1-badge", "P2": "p2-badge", "P3": "p3-badge"}.get(p, "p3-badge")
    return f'<span class="{cls}">{p}</span>'


def nav():
    # Admin-Tabs nur nach Login anzeigen
    cols = st.columns([2.5, 1, 1, 1, 1, 1])
    with cols[0]:
        st.markdown("### 🏢 ImmoPilot")
    with cols[1]:
        if st.button("Mieterportal", use_container_width=True):
            st.session_state.page = "mieter"; st.rerun()
    with cols[2]:
        if st.session_state.admin_logged_in:
            if st.button("Dashboard", use_container_width=True):
                st.session_state.page = "dashboard"; st.rerun()
        else:
            if st.button("Admin-Login", use_container_width=True):
                st.session_state.page = "login"; st.rerun()
    with cols[3]:
        if st.session_state.admin_logged_in:
            if st.button("Copilot", use_container_width=True):
                st.session_state.page = "copilot"; st.rerun()
    with cols[4]:
        if st.session_state.admin_logged_in:
            if st.button("Wissensbasis", use_container_width=True):
                st.session_state.page = "wissen"; st.rerun()
    with cols[5]:
        if st.session_state.admin_logged_in:
            if st.button("Abmelden", use_container_width=True):
                st.session_state.admin_logged_in = False
                st.session_state.page = "mieter"; st.rerun()
    st.divider()


def page_mieter():
    st.markdown('<div class="hero"><h1>Mieterservice</h1><p>Stellen Sie Ihre Frage - unser KI-Assistent antwortet sofort.</p></div>', unsafe_allow_html=True)
    col_main, col_side = st.columns([2, 1])

    with col_main:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Ihre Anfrage</div>', unsafe_allow_html=True)
        query = st.text_area("", placeholder="z.B. Ich habe einen Wasserschaden in meiner Wohnung...",
                             height=130, label_visibility="collapsed")
        send = st.button("Anfrage senden")
        st.markdown('</div>', unsafe_allow_html=True)

        if send:
            if not query.strip():
                st.error("Bitte geben Sie eine Anfrage ein.")
            else:
                with st.spinner("Analysiere Ihre Anfrage..."):
                    result = agent.run(query)
                st.session_state.last_result = result
                triage = result["triage"]

                # Ticket-Info und Priorität anzeigen
                st.markdown(f"""
                <div style="display:flex;gap:12px;align-items:center;margin-bottom:1rem;">
                    <span style="font-size:13px;color:#8A92A6;">Ticket</span>
                    <span style="font-weight:600;color:#1B2A4A;">{triage.get('ticket_id','-')}</span>
                    {priority_badge(triage.get('prioritaet','P3'))}
                </div>
                """, unsafe_allow_html=True)

                if result.get("escalate"):
                    st.markdown('<div class="escalate-box">Ihre Anfrage wurde zur persoenlichen Bearbeitung weitergeleitet. Ein Mitarbeiter meldet sich bei Ihnen.</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="section-title">Antwort</div>', unsafe_allow_html=True)

                st.markdown(f'<div class="answer-box">{result["answer"]}</div>', unsafe_allow_html=True)

                if result.get("sources"):
                    st.markdown('<div style="margin-top:1rem;font-size:13px;color:#8A92A6;">Quellen</div>', unsafe_allow_html=True)
                    pills = "".join([f'<span class="source-pill">{s}</span>' for s in result["sources"]])
                    st.markdown(pills, unsafe_allow_html=True)

                st.markdown("")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Intent", triage.get("intent", "-"))
                c2.metric("Kategorie", triage.get("category", "-"))
                c3.metric("Stimmung", triage.get("sentiment", "-"))
                c4.metric("Confidence", f"{result['confidence']:.0%}")

    with col_side:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Typische Anfragen</div>', unsafe_allow_html=True)
        for ex in ["Wann ist meine Miete faellig?", "Wasserschaden melden",
                   "Nebenkostenabrechnung", "Mietvertrag kuendigen",
                   "Passwort vergessen", "Kaution zurueck?", "Handwerker beauftragen?"]:
            st.markdown(f'<div style="padding:8px 0;border-bottom:1px solid #F0F2F5;font-size:14px;color:#4A5568;">- {ex}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Notfall?</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:14px;color:#4A5568;line-height:1.8;">Bei dringenden Schaeden:<br><strong style="color:#1B2A4A;">Notdienst: 0800 000 0000</strong><br><br>Geschaeftszeiten:<br>Mo-Fr 8:00-17:00 Uhr</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


def page_login():
    col = st.columns([1, 1.2, 1])[1]
    with col:
        st.markdown("### Admin-Zugang")
        st.markdown("Nur fuer autorisierte Mitarbeitende.")
        pw = st.text_input("Passwort", type="password")
        if st.button("Anmelden", use_container_width=True):
            if pw == ADMIN_PASSWORD:
                st.session_state.admin_logged_in = True
                st.session_state.page = "dashboard"
                st.rerun()
            else:
                st.error("Falsches Passwort.")


def page_dashboard():
    st.markdown('<div class="hero"><h1>Admin-Dashboard</h1><p>Auswertungen und eskalierte Faelle</p></div>', unsafe_allow_html=True)

    df = load_logs(LOG_PATH)
    if df.empty:
        st.info("Noch keine Anfragen vorhanden.")
        return

    # Spalten zuweisen - 12 Spalten = neues Format mit ticket_id und prioritaet
    if len(df.columns) == 12:
        df.columns = ["timestamp", "ticket_id", "query", "intent", "category",
                      "sentiment", "dringlichkeit", "prioritaet", "confidence",
                      "escalate", "sla_risiko", "answer_preview"]
    else:
        # Rückwärtskompatibilität mit altem Log-Format
        df.columns = ["timestamp", "query", "intent", "category", "sentiment",
                      "dringlichkeit", "confidence", "escalate", "answer_preview"]
        df["ticket_id"] = "-"
        df["prioritaet"] = "P3"
        df["sla_risiko"] = False

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["confidence"] = pd.to_numeric(df["confidence"], errors="coerce")
    df["escalate"] = df["escalate"].astype(str).str.lower().isin(["true", "1"])

    total = len(df)
    eskaliert = int(df["escalate"].sum())
    auto = total - eskaliert
    avg_conf = df["confidence"].mean()

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Anfragen gesamt</div><div class="metric-value">{total}</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Automatisch beantwortet</div><div class="metric-value" style="color:#1A7F4B;">{auto}</div><div class="metric-sub" style="color:#1A7F4B;">{(auto/total):.0%} Automatisierungsgrad</div></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Eskaliert</div><div class="metric-value" style="color:#C0392B;">{eskaliert}</div><div class="metric-sub" style="color:#C0392B;">{eskaliert/total:.0%} Eskalationsrate</div></div>', unsafe_allow_html=True)
    with k4:
        cc = "#1A7F4B" if avg_conf >= 0.65 else "#C0392B"
        st.markdown(f'<div class="metric-card"><div class="metric-label">Ø Confidence</div><div class="metric-value" style="color:{cc};">{avg_conf:.2f}</div><div class="metric-sub" style="color:{cc};">Ziel: >= 0.65</div></div>', unsafe_allow_html=True)

    st.markdown("")
    ch1, ch2 = st.columns(2)
    with ch1:
        st.markdown('<div class="section-title">Anfragen nach Kategorie</div>', unsafe_allow_html=True)
        st.bar_chart(df["category"].value_counts(), color="#2D4270")
    with ch2:
        st.markdown('<div class="section-title">Intent-Verteilung</div>', unsafe_allow_html=True)
        st.bar_chart(df["intent"].value_counts(), color="#2D4270")

    ch3, ch4 = st.columns(2)
    with ch3:
        st.markdown('<div class="section-title">Sentiment-Verteilung</div>', unsafe_allow_html=True)
        st.bar_chart(df["sentiment"].value_counts(), color="#2D4270")
    with ch4:
        st.markdown('<div class="section-title">Confidence-Verlauf</div>', unsafe_allow_html=True)
        st.line_chart(df[["timestamp", "confidence"]].set_index("timestamp").sort_index(), color="#2D4270")

    # Eskalierte Fälle mit Status-Verwaltung (Human-in-the-Loop)
    st.markdown('<div class="section-title">Eskalierte Faelle - Human-in-the-Loop</div>', unsafe_allow_html=True)
    esc_df = df[df["escalate"] == True].sort_values("timestamp", ascending=False).reset_index(drop=True)

    if esc_df.empty:
        st.success("Keine offenen eskalierten Faelle.")
    else:
        for idx, row in esc_df.iterrows():
            tid = row.get("ticket_id", "-")
            # unique_key verhindert doppelte Widget-Keys bei mehreren Tickets
            unique_key = f"{idx}_{tid}"
            status = st.session_state.ticket_status.get(unique_key, "Offen")
            status_color = {"Offen": "#C0392B", "In Bearbeitung": "#B7791F", "Erledigt": "#1A7F4B"}.get(status, "#C0392B")

            with st.expander(f"{row['timestamp'].strftime('%d.%m.%Y %H:%M')}  |  {tid}  |  {row.get('prioritaet','P3')}  |  {str(row['query'])[:60]}..."):
                c1, c2, c3, c4 = st.columns(4)
                c1.markdown(f"**Intent:** {row['intent']}")
                c2.markdown(f"**Kategorie:** {row['category']}")
                c3.markdown(f"**Dringlichkeit:** {row['dringlichkeit']}")
                c4.markdown(f"**Sentiment:** {row['sentiment']}")
                st.markdown(f"**Anfrage:** {row['query']}")
                st.markdown(f"**Antwort-Vorschau:** {row['answer_preview']}")
                st.markdown(f"**Confidence:** {float(row['confidence']):.0%}")
                st.markdown(f'<span style="color:{status_color};font-weight:500;">Status: {status}</span>', unsafe_allow_html=True)

                col_s1, col_s2, col_s3 = st.columns(3)
                if col_s1.button("In Bearbeitung", key=f"wip_{unique_key}"):
                    st.session_state.ticket_status[unique_key] = "In Bearbeitung"; st.rerun()
                if col_s2.button("Erledigt", key=f"done_{unique_key}"):
                    st.session_state.ticket_status[unique_key] = "Erledigt"; st.rerun()
                if col_s3.button("Zuruecksetzen", key=f"reset_{unique_key}"):
                    st.session_state.ticket_status[unique_key] = "Offen"; st.rerun()

    st.markdown('<div class="section-title">Alle Anfragen</div>', unsafe_allow_html=True)
    disp = df[["timestamp", "ticket_id", "query", "intent", "category",
               "sentiment", "confidence", "escalate"]].copy()
    disp["timestamp"] = disp["timestamp"].dt.strftime("%d.%m.%Y %H:%M")
    disp["confidence"] = disp["confidence"].apply(lambda x: f"{x:.0%}")
    disp["escalate"] = disp["escalate"].apply(lambda x: "Ja" if x else "Nein")
    disp.columns = ["Zeitstempel", "Ticket-ID", "Anfrage", "Intent",
                    "Kategorie", "Sentiment", "Confidence", "Eskaliert"]
    st.dataframe(disp, use_container_width=True, hide_index=True)

    # CSV-Export für externe Auswertung
    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button("CSV exportieren", csv_data,
                       f"anfragen_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")


def page_copilot():
    st.markdown('<div class="hero"><h1>Copilot-Agent</h1><p>Echtzeit-Unterstuetzung fuer Mitarbeitende</p></div>', unsafe_allow_html=True)
    col_main, col_side = st.columns([2, 1])

    with col_main:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Mieteranfrage eingeben</div>', unsafe_allow_html=True)
        query = st.text_area("", placeholder="Anfrage des Mieters hier eingeben...",
                             height=100, label_visibility="collapsed")
        analyse = st.button("Analysieren und Vorschlaege generieren")
        st.markdown('</div>', unsafe_allow_html=True)

        if analyse and query.strip():
            with st.spinner("Copilot analysiert..."):
                from agents.triage_agent import TriageAgent
                triage_temp = TriageAgent()
                triage = triage_temp.run(query)
                result = copilot.run(query, triage)

            if result["success"]:
                data = result["data"]
                st.markdown('<div class="section-title">FAQ-Vorschlaege</div>', unsafe_allow_html=True)
                for faq in data.get("faq_vorschlaege", []):
                    relevanz = int(faq.get("relevanz", 0) * 100)
                    st.markdown(
                        f'<div class="faq-card">'
                        f'<span class="faq-relevanz">Relevanz: {relevanz}%</span>'
                        f'<strong style="color:#1B2A4A;font-size:14px;">{faq.get("frage","")}</strong>'
                        f'<p style="margin:8px 0 0;font-size:13px;color:#4A5568;">{faq.get("antwort","")}</p>'
                        f'</div>', unsafe_allow_html=True)

                st.markdown('<div class="section-title">Antwort-Entwurf</div>', unsafe_allow_html=True)
                entwurf = data.get("antwort_entwurf", "")
                st.text_area("Entwurf bearbeiten:", value=entwurf, height=150)

                if data.get("hinweise"):
                    st.markdown('<div class="section-title">Hinweise</div>', unsafe_allow_html=True)
                    for h in data["hinweise"]:
                        st.markdown(f'<div class="hint-box">! {h}</div>', unsafe_allow_html=True)
            else:
                st.warning("Copilot konnte keine Vorschlaege generieren.")

    with col_side:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Zuletzt bearbeitet</div>', unsafe_allow_html=True)
        df = load_logs(LOG_PATH)
        if not df.empty:
            recent = df.tail(5).values.tolist()
            for row in reversed(recent):
                q = str(row[2]) if len(row) > 2 else "-"
                i = str(row[3]) if len(row) > 3 else "-"
                st.markdown(
                    f'<div style="padding:8px 0;border-bottom:1px solid #F0F2F5;font-size:13px;">'
                    f'<span style="color:#8A92A6;">{i}</span><br>{q[:60]}...</div>',
                    unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


def page_wissen():
    st.markdown('<div class="hero"><h1>Wissensbasis</h1><p>Auto-Dokumentation und FAQ-Vorschlaege</p></div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Dokumentations-Log", "FAQ-Vorschlaege"])

    with tab1:
        df_doc = load_logs(DOC_LOG)
        if df_doc.empty:
            st.info("Noch keine Dokumentationen vorhanden.")
        else:
            total = len(df_doc)
            luecken = int(df_doc["wissensluecke"].astype(str).str.lower().isin(["true", "1"]).sum()) \
                if "wissensluecke" in df_doc.columns else 0
            k1, k2 = st.columns(2)
            with k1:
                st.markdown(f'<div class="metric-card"><div class="metric-label">Dokumentierte Interaktionen</div><div class="metric-value">{total}</div></div>', unsafe_allow_html=True)
            with k2:
                st.markdown(f'<div class="metric-card"><div class="metric-label">Erkannte Wissensluecken</div><div class="metric-value" style="color:#C0392B;">{luecken}</div></div>', unsafe_allow_html=True)
            st.markdown("")
            st.dataframe(df_doc, use_container_width=True, hide_index=True)

    with tab2:
        df_faq = load_logs(FAQ_LOG)
        if df_faq.empty:
            st.info("Noch keine FAQ-Vorschlaege vorhanden. Der Dokumentations-Agent generiert Vorschlaege automatisch wenn Wissensluecken erkannt werden.")
        else:
            st.markdown(f"**{len(df_faq)} neue FAQ-Vorschlaege** vom Dokumentations-Agenten")
            st.markdown("")
            for idx, row in df_faq.iterrows():
                with st.expander(str(row.get("frage", "-"))[:80]):
                    st.markdown(f"**Kategorie:** {row.get('category', '-')}")
                    st.markdown(f"**Vorgeschlagene Frage:** {row.get('frage', '-')}")
                    st.markdown(f"**Vorgeschlagene Antwort:** {row.get('antwort', '-')}")
                    st.markdown(f"**Erstellt:** {row.get('timestamp', '-')}")
                    # TODO: "In FAQ aufnehmen" soll faq.json aktualisieren und ingest.py neu ausführen
                    c1, c2 = st.columns(2)
                    c1.button("In FAQ aufnehmen", key=f"accept_{idx}")
                    c2.button("Ablehnen", key=f"reject_{idx}")


# Seitensteuerung
nav()

page = st.session_state.page
if page == "mieter":
    page_mieter()
elif page == "login":
    page_login()
elif page == "dashboard":
    if st.session_state.admin_logged_in:
        page_dashboard()
    else:
        st.session_state.page = "login"; st.rerun()
elif page == "copilot":
    if st.session_state.admin_logged_in:
        page_copilot()
    else:
        st.session_state.page = "login"; st.rerun()
elif page == "wissen":
    if st.session_state.admin_logged_in:
        page_wissen()
    else:
        st.session_state.page = "login"; st.rerun()