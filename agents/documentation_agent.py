# Dokumentations-Agent - erstellt nach jeder Interaktion automatisch
# eine strukturierte Zusammenfassung und erkennt Wissenslücken in der FAQ

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import json
import csv
import os
from datetime import datetime

load_dotenv()

DOC_PROMPT = """Du bist ein Dokumentations-Agent einer Immobilienverwaltung.
Erstelle nach dieser abgeschlossenen Mieterinteraktion eine strukturierte Dokumentation.

Antworte NUR mit gueltigem JSON:
{{
  "kurzzusammenfassung": "1-2 Saetze was der Mieter wollte und wie es geloest wurde",
  "loesung": "Beschreibung der Loesung oder des naechsten Schritts",
  "wissensluecke": true/false,
  "neuer_faq_vorschlag": {{
    "frage": "Moegliche neue FAQ-Frage falls Wissensluecke erkannt",
    "antwort": "Moegliche Antwort"
  }},
  "tags": ["tag1", "tag2"],
  "qualitaet": "gut|mittel|schlecht",
  "verbesserungsvorschlag": "Optionaler Verbesserungsvorschlag"
}}

Anfrage: {query}
Intent: {intent}
Kategorie: {category}
Generierte Antwort: {answer}
Confidence: {confidence}
Eskaliert: {escalated}"""

DOC_LOG = "logs/dokumentation.csv"
FAQ_SUGGESTIONS = "logs/faq_vorschlaege.csv"


class DocumentationAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

    def run(self, query: str, triage_result: dict, answer: str,
            confidence: float, escalated: bool) -> dict:

        prompt = DOC_PROMPT\
            .replace("{query}", query)\
            .replace("{intent}", triage_result.get("intent", "-"))\
            .replace("{category}", triage_result.get("category", "-"))\
            .replace("{answer}", answer[:500])\
            .replace("{confidence}", str(round(confidence, 2)))\
            .replace("{escalated}", str(escalated))

        response = self.llm.invoke(prompt).content

        try:
            # Manchmal gibt das LLM Markdown-Codeblöcke zurück, die wir entfernen müssen
            clean = response.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            doc = json.loads(clean)
        except Exception:
            doc = {
                "kurzzusammenfassung": query[:100],
                "loesung": answer[:100],
                "wissensluecke": False,
                "neuer_faq_vorschlag": {"frage": "", "antwort": ""},
                "tags": [],
                "qualitaet": "mittel",
                "verbesserungsvorschlag": ""
            }

        self._log_dokumentation(query, triage_result, doc, confidence, escalated)

        # Falls eine Wissenslücke erkannt wurde, Vorschlag separat speichern
        if doc.get("wissensluecke") and doc.get("neuer_faq_vorschlag", {}).get("frage"):
            self._log_faq_vorschlag(doc["neuer_faq_vorschlag"], triage_result)

        return doc

    def _log_dokumentation(self, query, triage, doc, confidence, escalated):
        os.makedirs("logs", exist_ok=True)
        write_header = not os.path.exists(DOC_LOG)
        with open(DOC_LOG, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if write_header:
                w.writerow(["timestamp", "ticket_id", "query", "intent", "category",
                            "zusammenfassung", "loesung", "qualitaet", "wissensluecke",
                            "confidence", "escalated", "tags"])
            w.writerow([
                datetime.now().isoformat(),
                triage.get("ticket_id", "-"),
                query,
                triage.get("intent", "-"),
                triage.get("category", "-"),
                doc.get("kurzzusammenfassung", ""),
                doc.get("loesung", ""),
                doc.get("qualitaet", ""),
                doc.get("wissensluecke", False),
                round(confidence, 2),
                escalated,
                ", ".join(doc.get("tags", []))
            ])

    def _log_faq_vorschlag(self, vorschlag, triage):
        write_header = not os.path.exists(FAQ_SUGGESTIONS)
        with open(FAQ_SUGGESTIONS, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if write_header:
                w.writerow(["timestamp", "category", "frage", "antwort"])
            w.writerow([
                datetime.now().isoformat(),
                triage.get("category", "-"),
                vorschlag.get("frage", ""),
                vorschlag.get("antwort", "")
            ])