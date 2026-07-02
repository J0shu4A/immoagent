# Triage Agent - klassifiziert eingehende Mieteranfragen
# Gibt strukturiertes JSON zurück mit Intent, Kategorie, Priorität etc.

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import json
import uuid
from datetime import datetime

load_dotenv()

# Prompt muss doppelte {{ }} verwenden damit Python sie nicht als Platzhalter interpretiert
# Nur {query} wird ersetzt
TRIAGE_PROMPT = """Analysiere diese Mieteranfrage und antworte NUR mit gueltigem JSON:
{{
  "intent": "Frage|Beschwerde|Schadensmeldung|Kuendigung|Support|Sonstiges",
  "category": "Miete|Nebenkosten|Reparaturen|Mietvertrag|Einzug|Auszug|Konto|Technisch|Allgemein",
  "sentiment": "positiv|neutral|negativ",
  "dringlichkeit": "niedrig|mittel|hoch",
  "prioritaet": "P1|P2|P3",
  "schluesselwoerter": ["wort1", "wort2"],
  "zusammenfassung": "Kurze 1-Satz Zusammenfassung der Anfrage"
}}

Prioritaet-Regeln:
- P1 = Notfall (Wasserschaden, Heizungsausfall, Stromausfall, Gasgeruch)
- P2 = Wichtig (Beschwerde, Kuendigung, negatives Sentiment)
- P3 = Standard (allgemeine Fragen, technischer Support)

Anfrage: {query}"""


class TriageAgent:
    def __init__(self):
        # Niedrige Temperatur für konsistente Klassifikation
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

    def run(self, query: str) -> dict:
        prompt = TRIAGE_PROMPT.replace("{query}", query)
        response = self.llm.invoke(prompt).content

        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            # Fallback falls LLM kein valides JSON zurückgibt
            result = {
                "intent": "Sonstiges",
                "category": "Allgemein",
                "sentiment": "neutral",
                "dringlichkeit": "niedrig",
                "prioritaet": "P3",
                "schluesselwoerter": [],
                "zusammenfassung": query[:100]
            }

        # Ticket-ID für Nachverfolgung generieren
        result["ticket_id"] = f"TKT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"
        result["timestamp"] = datetime.now().isoformat()
        return result