# Eskalations-Agent - entscheidet ob eine Anfrage automatisch beantwortet
# werden kann oder manuell bearbeitet werden muss
# Berücksichtigt Confidence-Score, Sentiment, Dringlichkeit und SLA-Status

from datetime import datetime, timedelta

# SLA-Frist - im Demo auf 1 Stunde gesetzt, produktiv wären es 24h
SLA_STUNDEN = 1


class EscalationAgent:
    def __init__(self):
        self.sla_limit = timedelta(hours=SLA_STUNDEN)

    def evaluate(self, query: str, triage_result: dict, confidence: float) -> dict:
        gruende = []
        eskalieren = False

        # Confidence zu niedrig -> Antwort nicht zuverlässig genug
        if confidence < 0.5:
            eskalieren = True
            gruende.append(f"Niedrige Confidence ({confidence:.0%})")

        # Notfälle immer eskalieren
        if triage_result.get("dringlichkeit") == "hoch":
            eskalieren = True
            gruende.append("Hohe Dringlichkeit")

        if triage_result.get("prioritaet") == "P1":
            eskalieren = True
            gruende.append("Notfall P1")

        # Unzufriedener Mieter mit unsicherer Antwort -> lieber Mensch draufschauen lassen
        if triage_result.get("sentiment") == "negativ" and confidence < 0.65:
            eskalieren = True
            gruende.append("Negatives Sentiment mit niedriger Confidence")

        # Kündigung und Beschwerden immer manuell bearbeiten
        if triage_result.get("intent") in ["Beschwerde", "Kuendigung"]:
            eskalieren = True
            gruende.append(f"Sensibler Intent: {triage_result.get('intent')}")

        # SLA-Check: wie viel Zeit ist seit Ticketerstellung vergangen?
        timestamp = triage_result.get("timestamp", datetime.now().isoformat())
        try:
            created = datetime.fromisoformat(timestamp)
            verbleibend = self.sla_limit - (datetime.now() - created)
            sla_risiko = verbleibend.total_seconds() < 0
            sla_minuten = max(0, int(verbleibend.total_seconds() / 60))
        except Exception:
            sla_risiko = False
            sla_minuten = SLA_STUNDEN * 60

        if sla_risiko:
            eskalieren = True
            gruende.append("SLA-Frist überschritten")

        return {
            "eskalieren": eskalieren,
            "gruende": gruende,
            "sla_risiko": sla_risiko,
            "sla_verbleibend_min": sla_minuten,
            "prioritaet": triage_result.get("prioritaet", "P3"),
            # Vollständiger Kontext für den Mitarbeiter der den Fall übernimmt
            "kontext": {
                "query": query,
                "intent": triage_result.get("intent"),
                "category": triage_result.get("category"),
                "sentiment": triage_result.get("sentiment"),
                "dringlichkeit": triage_result.get("dringlichkeit"),
                "confidence": round(confidence, 2),
                "ticket_id": triage_result.get("ticket_id", "-"),
                "zusammenfassung": triage_result.get("zusammenfassung", "")
            }
        }