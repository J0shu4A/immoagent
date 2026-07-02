# Copilot Agent - unterstützt Mitarbeitende in Echtzeit
# Durchsucht die Wissensdatenbank und generiert FAQ-Vorschläge + Antwort-Entwurf
# Anders als der Haupt-Agent trifft hier der Mensch die finale Entscheidung

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

load_dotenv()

COPILOT_PROMPT = """Du bist ein Assistent fuer einen Mitarbeiter der Immobilienverwaltung.
Basierend auf der Mieteranfrage und den gefundenen FAQ-Eintraegen, erstelle:
1. Die 3 relevantesten FAQ-Vorschlaege fuer den Mitarbeiter
2. Einen Antwort-Entwurf den der Mitarbeiter anpassen kann
3. Hinweise auf moegliche Fallstricke

Antworte NUR mit gueltigem JSON:
{{
  "faq_vorschlaege": [
    {{"frage": "...", "antwort": "...", "relevanz": 0.95}},
    {{"frage": "...", "antwort": "...", "relevanz": 0.80}},
    {{"frage": "...", "antwort": "...", "relevanz": 0.70}}
  ],
  "antwort_entwurf": "Vorformulierte Antwort fuer den Mitarbeiter...",
  "hinweise": ["Hinweis 1", "Hinweis 2"]
}}

FAQ-Kontext:
{context}

Mieteranfrage: {query}
Kategorie: {category}
Intent: {intent}"""


class CopilotAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        # Verbindung zur bestehenden ChromaDB
        self.vectordb = Chroma(
            persist_directory="./chroma_db",
            embedding_function=self.embeddings
        )

    def run(self, query: str, triage_result: dict) -> dict:
        # k=5 statt k=3 damit Mitarbeiter mehr Auswahl hat
        docs = self.vectordb.similarity_search_with_score(query, k=5)

        context = "\n\n".join([
            f"Frage: {d.metadata.get('question', '-')}\nAntwort: {d.page_content}"
            for d, _ in docs
        ])

        prompt = COPILOT_PROMPT\
            .replace("{context}", context)\
            .replace("{query}", query)\
            .replace("{category}", triage_result.get("category", "Allgemein"))\
            .replace("{intent}", triage_result.get("intent", "Sonstiges"))

        response = self.llm.invoke(prompt).content

        try:
            clean = response.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            return {"success": True, "data": __import__("json").loads(clean)}
        except Exception:
            return {
                "success": False,
                "data": {
                    "faq_vorschlaege": [],
                    "antwort_entwurf": "Kein Entwurf verfuegbar.",
                    "hinweise": []
                }
            }