# Ingest-Skript - lädt FAQ-Daten und indexiert sie in ChromaDB
# Muss einmalig ausgeführt werden, danach bei jeder Änderung an der faq.json
# Ausführung: python3 ingest.py

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from dotenv import load_dotenv
import json
import os
import shutil

load_dotenv()


def load_and_index():
    with open("data/faq.json", "r", encoding="utf-8") as f:
        faqs = json.load(f)

    docs = []
    for faq in faqs:
        tags = ", ".join(faq.get("tags", []))

        # Frage + Antwort + Tags kombinieren verbessert die Retrieval-Qualität
        # gegenüber reiner Antwort-Indexierung
        content = f"""Frage: {faq['question']}

Antwort:
{faq['answer']}

Tags:
{tags}"""

        doc = Document(
            page_content=content,
            metadata={
                "id": faq["id"],
                "question": faq["question"],
                "category": faq["category"],
                "tags": tags
            }
        )
        docs.append(doc)

    # Alte DB löschen damit keine veralteten Einträge übrig bleiben
    if os.path.exists("./chroma_db"):
        shutil.rmtree("./chroma_db")
        print("Alte ChromaDB geloescht.")

    # text-embedding-3-small: günstig und für deutschen Text gut geeignet
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    vectordb = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )

    print(f"Indexiert: {len(docs)} FAQ-Eintraege")
    print("ChromaDB erfolgreich erstellt.")
    return vectordb


if __name__ == "__main__":
    load_and_index()