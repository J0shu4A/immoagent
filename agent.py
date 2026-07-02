# Haupt-Orchestrator - koordiniert alle Agenten des Systems
#
# Pipeline pro Anfrage:
# 1. TriageAgent       -> Klassifikation + Ticket-ID
# 2. RAG Retrieval     -> semantische Suche in ChromaDB
# 3. Antwortgenerierung -> LLM mit FAQ-Kontext
# 4. EscalationAgent   -> automatisch oder manuell?
# 5. DocumentationAgent -> Interaktion dokumentieren
# 6. Logging           -> alles in queries.csv speichern

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from agents.triage_agent import TriageAgent
from agents.escalation_agent import EscalationAgent
from agents.documentation_agent import DocumentationAgent
from dotenv import load_dotenv
import csv
import os
from datetime import datetime

load_dotenv()

# .replace() statt .format() verwenden um Konflikte mit den
# geschweiften Klammern im JSON-Kontext zu vermeiden
ANSWER_PROMPT = """Du bist ein freundlicher Service-Mitarbeiter einer Immobilienverwaltung.
Beantworte die Mieteranfrage basierend auf den FAQ-Informationen.

Regeln:
- Antworte praezise, freundlich und auf Deutsch.
- Gib keine rechtsverbindliche Beratung.
- Wenn Informationen fehlen, sage das ehrlich.
- Bei Notfaellen (Wasserschaden, Heizungsausfall, Stromausfall, Gasgeruch):
  weise auf sofortige Kontaktaufnahme mit dem Notdienst hin.

FAQ-Kontext:
{context}

Anfrage: {query}
Intent: {intent}
Kategorie: {category}

Antwort:"""

LOG_PATH = "logs/queries.csv"


class SupportAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        # ChromaDB muss vorher mit ingest.py aufgebaut worden sein
        self.vectordb = Chroma(
            persist_directory="./chroma_db",
            embedding_function=self.embeddings
        )
        self.triage_agent = TriageAgent()
        self.escalation_agent = EscalationAgent()
        self.documentation_agent = DocumentationAgent()

    def retrieve(self, query: str, k: int = 3):
        # Gibt Liste von (Document, Score) Tupeln zurück
        # Score = L2-Distanz: 0 = perfekt, höher = unähnlicher
        return self.vectordb.similarity_search_with_score(query, k=k)

    def generate_answer(self, query, triage_result, docs_with_scores):
        context = "\n\n".join([
            f"Frage: {d.metadata.get('question', '-')}\n"
            f"Kategorie: {d.metadata.get('category', '-')}\n"
            f"Antwort: {d.page_content}"
            for d, _ in docs_with_scores
        ])

        # Confidence aus L2-Distanz berechnen
        # ChromaDB gibt keine Cosine-Similarity zurück, daher Normalisierung:
        # score=0 -> confidence=1.0, score=2 -> confidence=0.0
        if docs_with_scores:
            raw_score = float(docs_with_scores[0][1])
            confidence = max(0.0, min(1.0, 1 - (raw_score / 2.0)))
        else:
            confidence = 0.0

        prompt = ANSWER_PROMPT\
            .replace("{context}", context)\
            .replace("{query}", query)\
            .replace("{intent}", triage_result.get("intent", "Unbekannt"))\
            .replace("{category}", triage_result.get("category", "Unbekannt"))

        answer = self.llm.invoke(prompt).content
        return answer, confidence

    def run(self, query: str) -> dict:
        # Schritt 1: Triage
        triage = self.triage_agent.run(query)

        # Schritt 2 + 3: Retrieval und Antwort
        docs = self.retrieve(query)
        answer, confidence = self.generate_answer(query, triage, docs)

        # Schritt 4: Eskalation prüfen
        escalation = self.escalation_agent.evaluate(query, triage, confidence)

        # Schritt 5: Dokumentation
        doc = self.documentation_agent.run(
            query, triage, answer, confidence, escalation["eskalieren"]
        )

        result = {
            "query": query,
            "triage": triage,
            "answer": answer,
            "confidence": round(confidence, 2),
            "escalate": escalation["eskalieren"],
            "escalation_detail": escalation,
            "documentation": doc,
            "sources": [d.metadata.get("question", "-") for d, _ in docs]
        }

        # Schritt 6: Logging
        self._log(result)
        return result

    def _log(self, result: dict):
        os.makedirs("logs", exist_ok=True)
        write_header = not os.path.exists(LOG_PATH)
        with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if write_header:
                w.writerow([
                    "timestamp", "ticket_id", "query", "intent", "category",
                    "sentiment", "dringlichkeit", "prioritaet", "confidence",
                    "escalate", "sla_risiko", "answer_preview"
                ])
            w.writerow([
                datetime.now().isoformat(),
                result["triage"].get("ticket_id", "-"),
                result["query"],
                result["triage"].get("intent", ""),
                result["triage"].get("category", ""),
                result["triage"].get("sentiment", ""),
                result["triage"].get("dringlichkeit", ""),
                result["triage"].get("prioritaet", "P3"),
                result["confidence"],
                result["escalate"],
                result["escalation_detail"].get("sla_risiko", False),
                result["answer"][:200]
            ])