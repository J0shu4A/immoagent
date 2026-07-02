from agent import SupportAgent
import pandas as pd

TEST_SET = [
    {
        "query": "Wann ist meine Miete fällig?",
        "expected_intent": "Frage",
        "expected_category": "Miete"
    },
    {
        "query": "Wie kann ich meine Miete bezahlen?",
        "expected_intent": "Frage",
        "expected_category": "Miete"
    },
    {
        "query": "Wann bekomme ich die Nebenkostenabrechnung?",
        "expected_intent": "Frage",
        "expected_category": "Nebenkosten"
    },
    {
        "query": "Kann ich die Belege zur Nebenkostenabrechnung einsehen?",
        "expected_intent": "Frage",
        "expected_category": "Nebenkosten"
    },
    {
        "query": "Ich habe einen Wasserschaden in meiner Wohnung.",
        "expected_intent": "Schadensmeldung",
        "expected_category": "Reparaturen"
    },
    {
        "query": "Meine Heizung funktioniert nicht mehr.",
        "expected_intent": "Schadensmeldung",
        "expected_category": "Reparaturen"
    },
    {
        "query": "Kann ich selbst einen Handwerker beauftragen?",
        "expected_intent": "Frage",
        "expected_category": "Reparaturen"
    },
    {
        "query": "Wie kann ich meinen Mietvertrag kündigen?",
        "expected_intent": "Kündigung",
        "expected_category": "Mietvertrag"
    },
    {
        "query": "Welche Kündigungsfrist gilt für meine Wohnung?",
        "expected_intent": "Frage",
        "expected_category": "Mietvertrag"
    },
    {
        "query": "Wann bekomme ich meine Schlüssel?",
        "expected_intent": "Frage",
        "expected_category": "Einzug"
    },
    {
        "query": "Wie läuft die Wohnungsabnahme beim Auszug ab?",
        "expected_intent": "Frage",
        "expected_category": "Auszug"
    },
    {
        "query": "Wann erhalte ich meine Kaution zurück?",
        "expected_intent": "Frage",
        "expected_category": "Auszug"
    },
    {
        "query": "Ich habe mein Passwort für das Mieterportal vergessen.",
        "expected_intent": "Support",
        "expected_category": "Konto"
    },
    {
        "query": "Warum kann ich mich nicht im Portal anmelden?",
        "expected_intent": "Support",
        "expected_category": "Technisch"
    },
    {
        "query": "Ich bin sehr unzufrieden mit der Bearbeitung meines Schadens.",
        "expected_intent": "Beschwerde",
        "expected_category": "Allgemein"
    }
]


def run_evaluation():
    agent = SupportAgent()
    results = []

    for i, test in enumerate(TEST_SET, 1):
        print(f"  Teste {i}/{len(TEST_SET)}: {test['query'][:50]}...")
        result = agent.run(test["query"])

        intent_correct = result["triage"]["intent"] == test["expected_intent"]
        category_correct = result["triage"]["category"] == test["expected_category"]

        results.append({
            "query": test["query"],
            "expected_intent": test["expected_intent"],
            "got_intent": result["triage"]["intent"],
            "intent_correct": intent_correct,
            "expected_category": test["expected_category"],
            "got_category": result["triage"]["category"],
            "category_correct": category_correct,
            "confidence": result["confidence"],
            "escalated": result["escalate"],
            "answer_len": len(result["answer"])
        })

    df = pd.DataFrame(results)

    print("\n=== Evaluationsergebnisse ===")
    print(f"Intent Accuracy:      {df['intent_correct'].mean():.1%}")
    print(f"Category Accuracy:    {df['category_correct'].mean():.1%}")
    print(f"Ø Confidence Score:   {df['confidence'].mean():.2f}")
    print(f"Eskalationsrate:      {df['escalated'].mean():.1%}")
    print(f"Ø Antwortlänge:       {df['answer_len'].mean():.0f} Zeichen")

    # Fehleranalyse
    wrong_intents = df[~df['intent_correct']][['query', 'expected_intent', 'got_intent']]
    if not wrong_intents.empty:
        print("\n--- Falsch klassifizierte Intents ---")
        print(wrong_intents.to_string(index=False))

    wrong_cats = df[~df['category_correct']][['query', 'expected_category', 'got_category']]
    if not wrong_cats.empty:
        print("\n--- Falsch klassifizierte Kategorien ---")
        print(wrong_cats.to_string(index=False))

    # Zielwert-Check
    print("\n=== Zielwert-Check ===")
    print(f"Intent Accuracy ≥ 85%:   {'✓' if df["intent_correct"].mean() >= 0.85 else '✗'} ({df["intent_correct"].mean():.1%})")
    print(f"Ø Confidence ≥ 0.65:     {'✓' if df["confidence"].mean() >= 0.65 else '✗'} ({df["confidence"].mean():.2f})")
    print(f"Eskalationsrate 10–25%:  {'✓' if 0.10 <= df["escalated"].mean() <= 0.25 else '✗'} ({df["escalated"].mean():.1%})")

    import os
    os.makedirs("logs", exist_ok=True)
    df.to_csv("logs/evaluation_results.csv", index=False)
    print("\n✓ Ergebnisse gespeichert: logs/evaluation_results.csv")

    return df


if __name__ == "__main__":
    run_evaluation()