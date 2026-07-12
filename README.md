ImmoPilot — KI-Agent für Mieteranfragen

Prototyp im Rahmen der Bachelorarbeit:
„Potenziale und Herausforderungen von KI-Agenten zur Automatisierung betrieblicher Geschäftsprozesse"


Live-Demo

Die Anwendung ist öffentlich zugänglich unter:
https://immoagent.streamlit.app

Admin-Zugang (für Dashboard, Copilot und Wissensbasis):
Passwort: admin123


Was ist ImmoPilot?

ImmoPilot ist ein KI-gestützter Support-Agent für eine fiktive Immobilienverwaltung. Er bearbeitet eingehende Mieteranfragen automatisch — von der Klassifikation über die Wissensdatenbankabfrage bis zur Antwortgenerierung.

Das System besteht aus fünf spezialisierten Agenten:

AgentFunktionTriage-AgentKlassifikation, Priorisierung (P1/P2/P3), Ticket-IDAntwort-AgentRAG-basierte Antwortgenerierung mit FAQ-KontextEskalations-AgentRegelbasierte Eskalationsentscheidung, SLA-MonitoringDokumentations-AgentAutomatische Erfassung, WissenslückenerkennungCopilot-AgentEchtzeit-FAQ-Vorschläge für Mitarbeitende


Technologie-Stack

KomponenteTechnologieFrameworkLangChainSprachmodellGPT-4o-mini (OpenAI)VektordatenbankChromaDB (lokal)Embeddingstext-embedding-3-small (OpenAI)BenutzeroberflächeStreamlitDeploymentStreamlit Cloud


Projektstruktur

KI-Agent/
├── agent.py                    # Haupt-Orchestrator — koordiniert alle Agenten
├── ingest.py                   # FAQ-Daten laden und in ChromaDB indexieren
├── app.py                      # Streamlit UI — alle 5 Seiten
├── evaluate.py                 # Evaluation mit 100 Testfällen
├── agents/
│   ├── __init__.py
│   ├── triage_agent.py         # Klassifikation und Ticket-Erstellung
│   ├── escalation_agent.py     # Eskalationslogik und SLA-Monitor
│   ├── documentation_agent.py  # Auto-Dokumentation und FAQ-Vorschläge
│   └── copilot_agent.py        # Mitarbeiter-Assistenz
├── data/
│   └── faq.json                # 60 FAQ-Einträge, 9 Kategorien
├── logs/
│   ├── queries.csv             # Alle Anfragen (auto-generiert)
│   ├── dokumentation.csv       # Auto-Dokumentation (auto-generiert)
│   ├── faq_vorschlaege.csv     # Erkannte Wissenslücken (auto-generiert)
│   └── evaluation_results.csv  # Evaluationsergebnisse (auto-generiert)
├── chroma_db/                  # Vektordatenbank (auto-generiert)
├── requirements.txt            # Python-Abhängigkeiten
└── .env                        # API-Key (nicht in Git!)


Lokale Installation

Voraussetzungen


Python 3.10+
OpenAI API-Key (https://platform.openai.com/api-keys)


Schritt 1 — Repository klonen

bashgit clone https://github.com/J0shu4A/immoagent.git
cd immoagent

Schritt 2 — Virtuelle Umgebung erstellen

bashpython3 -m venv venv
source venv/bin/activate

Schritt 3 — Abhängigkeiten installieren

bashpip install -r requirements.txt

Schritt 4 — API-Key hinterlegen

.env Datei erstellen:

OPENAI_API_KEY=sk-proj-dein-key-hier

Schritt 5 — Wissensdatenbank aufbauen

bashpython3 ingest.py

Ausgabe: Indexiert: 60 FAQ-Eintraege

Schritt 6 — App starten

bashstreamlit run app.py

Browser öffnet sich automatisch unter http://localhost:8501
App-Seiten im Überblick

Mieterportal (öffentlich)

Mieter stellen Freitextanfragen und erhalten automatisch eine Antwort mit Ticket-ID und Priorität.

Admin-Login

Passwort: admin123

Dashboard (Admin)


KPI-Karten: Anfragen gesamt, Automatisierungsgrad, Eskalationsrate, Confidence
Charts: Kategorie-, Intent-, Sentiment-Verteilung, Confidence-Verlauf
Evaluationssektion mit Zielwert-Check
Human-in-the-Loop: Eskalierte Fälle mit Status-Verwaltung
CSV-Export aller Anfragen


Copilot (Admin)

Mitarbeitende geben eine Mieteranfrage ein und erhalten:


3 priorisierte FAQ-Vorschläge mit Relevanzwerten
Bearbeitbaren Antwort-Entwurf
Hinweise auf mögliche Fallstricke


Wissensbasis (Admin)


Dokumentations-Log aller Interaktionen
Automatisch erkannte Wissenslücken als FAQ-Vorschläge



Wissensdatenbank

60 FAQ-Einträge in 9 Kategorien:

Kategorie: 
Miete  7
Nebenkosten  5
Reparaturen  8
Mietvertrag  7
Einzug  5
Auszug  5
Konto  4
Technisch  4
Allgemein  15


GitHub

Quellcode: https://github.com/J0shu4A/immoagent
