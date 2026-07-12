# Evaluation des KI-Agenten mit 100 Testfaellen
# Abdeckung aller 9 Kategorien aus der FAQ-Wissensdatenbank
# Ausfuehren: python3 evaluate.py

from agent import SupportAgent
import pandas as pd
import time
import os

TEST_SET = [
    # Miete (12 Faelle)
    {"query": "Wann ist meine Miete faellig?", "expected_intent": "Frage", "expected_category": "Miete"},
    {"query": "Wie kann ich meine Miete bezahlen?", "expected_intent": "Frage", "expected_category": "Miete"},
    {"query": "Ich habe meine Miete noch nicht bezahlt, was passiert jetzt?", "expected_intent": "Frage", "expected_category": "Miete"},
    {"query": "Kann ich eine Ratenzahlung fuer meine Mietschulden vereinbaren?", "expected_intent": "Frage", "expected_category": "Miete"},
    {"query": "Wie bekomme ich eine Mietbescheinigung?", "expected_intent": "Frage", "expected_category": "Miete"},
    {"query": "Ich moechte per SEPA-Lastschrift zahlen, wie geht das?", "expected_intent": "Frage", "expected_category": "Miete"},
    {"query": "Bis wann muss die Miete ueberwiesen sein?", "expected_intent": "Frage", "expected_category": "Miete"},
    {"query": "Was sind Mahngebuehren und muss ich die zahlen?", "expected_intent": "Frage", "expected_category": "Miete"},
    {"query": "Ich bin sehr unzufrieden, meine Miete wurde erhoehen ohne Ankuendigung!", "expected_intent": "Beschwerde", "expected_category": "Miete"},
    {"query": "Was ist eine Staffelmiete?", "expected_intent": "Frage", "expected_category": "Miete"},
    {"query": "Was ist eine Indexmiete?", "expected_intent": "Frage", "expected_category": "Miete"},
    {"query": "Kann ich eine Quittung fuer meine Mietzahlung bekommen?", "expected_intent": "Frage", "expected_category": "Miete"},

    # Nebenkosten (10 Faelle)
    {"query": "Wann bekomme ich die Nebenkostenabrechnung?", "expected_intent": "Frage", "expected_category": "Nebenkosten"},
    {"query": "Wie werden die Nebenkosten berechnet?", "expected_intent": "Frage", "expected_category": "Nebenkosten"},
    {"query": "Kann ich die Belege zur Nebenkostenabrechnung einsehen?", "expected_intent": "Frage", "expected_category": "Nebenkosten"},
    {"query": "Ich habe eine Nachzahlung bekommen, wann muss ich zahlen?", "expected_intent": "Frage", "expected_category": "Nebenkosten"},
    {"query": "Was ist in den Nebenkosten enthalten?", "expected_intent": "Frage", "expected_category": "Nebenkosten"},
    {"query": "Meine Nebenkostenabrechnung scheint falsch, was kann ich tun?", "expected_intent": "Beschwerde", "expected_category": "Nebenkosten"},
    {"query": "Wie hoch sind meine monatlichen Nebenkosten?", "expected_intent": "Frage", "expected_category": "Nebenkosten"},
    {"query": "Werden Heizkosten in den Nebenkosten berechnet?", "expected_intent": "Frage", "expected_category": "Nebenkosten"},
    {"query": "Was ist ein Umlageschluessel?", "expected_intent": "Frage", "expected_category": "Nebenkosten"},
    {"query": "Ich moechte Widerspruch gegen die Nebenkostenabrechnung einlegen.", "expected_intent": "Beschwerde", "expected_category": "Nebenkosten"},

    # Reparaturen (15 Faelle)
    {"query": "Wie melde ich einen Schaden?", "expected_intent": "Frage", "expected_category": "Reparaturen"},
    {"query": "Ich habe einen Wasserschaden in meiner Wohnung.", "expected_intent": "Schadensmeldung", "expected_category": "Reparaturen"},
    {"query": "Meine Heizung funktioniert nicht mehr.", "expected_intent": "Schadensmeldung", "expected_category": "Reparaturen"},
    {"query": "Was gilt als Notfall bei der Hausverwaltung?", "expected_intent": "Frage", "expected_category": "Reparaturen"},
    {"query": "Wer bezahlt die Reparatur in meiner Wohnung?", "expected_intent": "Frage", "expected_category": "Reparaturen"},
    {"query": "Kann ich selbst einen Handwerker beauftragen?", "expected_intent": "Frage", "expected_category": "Reparaturen"},
    {"query": "Wie lange dauert es bis mein Schaden behoben wird?", "expected_intent": "Frage", "expected_category": "Reparaturen"},
    {"query": "Ich rieche Gas in meiner Wohnung, was soll ich tun?", "expected_intent": "Schadensmeldung", "expected_category": "Reparaturen"},
    {"query": "Der Aufzug in unserem Haus funktioniert nicht.", "expected_intent": "Schadensmeldung", "expected_category": "Reparaturen"},
    {"query": "Was sind Kleinreparaturen und muss ich sie selbst zahlen?", "expected_intent": "Frage", "expected_category": "Reparaturen"},
    {"query": "Mein Rohr ist gebrochen, Wasser laeuft aus!", "expected_intent": "Schadensmeldung", "expected_category": "Reparaturen"},
    {"query": "Die Heizung faellt im Winter aus, was ist zu tun?", "expected_intent": "Schadensmeldung", "expected_category": "Reparaturen"},
    {"query": "Ich bin sehr unzufrieden, mein Schaden wird seit Wochen nicht behoben.", "expected_intent": "Beschwerde", "expected_category": "Reparaturen"},
    {"query": "Mein Schloss ist defekt und ich komme nicht in die Wohnung.", "expected_intent": "Schadensmeldung", "expected_category": "Reparaturen"},
    {"query": "Der Strom in meiner Wohnung ist komplett ausgefallen.", "expected_intent": "Schadensmeldung", "expected_category": "Reparaturen"},

    # Mietvertrag (12 Faelle)
    {"query": "Wie kann ich meinen Mietvertrag kuendigen?", "expected_intent": "Kuendigung", "expected_category": "Mietvertrag"},
    {"query": "Welche Kuendigungsfrist gilt fuer meine Wohnung?", "expected_intent": "Frage", "expected_category": "Mietvertrag"},
    {"query": "Kann ich einen Nachmieter vorschlagen?", "expected_intent": "Frage", "expected_category": "Mietvertrag"},
    {"query": "Darf ich meinen Mietvertrag auf eine andere Person uebertragen?", "expected_intent": "Frage", "expected_category": "Mietvertrag"},
    {"query": "Kann ich in meiner Wohnung ein Gewerbe betreiben?", "expected_intent": "Frage", "expected_category": "Mietvertrag"},
    {"query": "Ich moechte einen Untermieter aufnehmen, ist das erlaubt?", "expected_intent": "Frage", "expected_category": "Mietvertrag"},
    {"query": "Was ist eine Staffelmiete im Mietvertrag?", "expected_intent": "Frage", "expected_category": "Mietvertrag"},
    {"query": "Ich moechte meinen Mietvertrag zum naechsten Monat kuendigen.", "expected_intent": "Kuendigung", "expected_category": "Mietvertrag"},
    {"query": "Darf ich Haustiere in meiner Wohnung halten?", "expected_intent": "Frage", "expected_category": "Mietvertrag"},
    {"query": "Was steht zur Renovierungspflicht in meinem Mietvertrag?", "expected_intent": "Frage", "expected_category": "Mietvertrag"},
    {"query": "Kann ich meinen Mietvertrag vorzeitig aufloesen?", "expected_intent": "Kuendigung", "expected_category": "Mietvertrag"},
    {"query": "Wann darf der Vermieter die Miete erhoehen?", "expected_intent": "Frage", "expected_category": "Mietvertrag"},

    # Einzug (8 Faelle)
    {"query": "Wann erhalte ich meine Schluessel?", "expected_intent": "Frage", "expected_category": "Einzug"},
    {"query": "Wie vereinbare ich einen Uebergabetermin?", "expected_intent": "Frage", "expected_category": "Einzug"},
    {"query": "Erhalte ich ein Uebergabeprotokoll?", "expected_intent": "Frage", "expected_category": "Einzug"},
    {"query": "Was muss ich beim Einzug beachten?", "expected_intent": "Frage", "expected_category": "Einzug"},
    {"query": "Wie hoch ist die Kaution und wann muss ich sie zahlen?", "expected_intent": "Frage", "expected_category": "Einzug"},
    {"query": "Kann ich vor dem offiziellen Einzugstermin in die Wohnung?", "expected_intent": "Frage", "expected_category": "Einzug"},
    {"query": "Was passiert wenn ich Maengel beim Einzug feststelle?", "expected_intent": "Frage", "expected_category": "Einzug"},
    {"query": "Wie viele Schluessel bekomme ich beim Einzug?", "expected_intent": "Frage", "expected_category": "Einzug"},

    # Auszug (10 Faelle)
    {"query": "Wie laeuft die Wohnungsabnahme ab?", "expected_intent": "Frage", "expected_category": "Auszug"},
    {"query": "Wann bekomme ich meine Kaution zurueck?", "expected_intent": "Frage", "expected_category": "Auszug"},
    {"query": "Muss ich die Wohnung renovieren beim Auszug?", "expected_intent": "Frage", "expected_category": "Auszug"},
    {"query": "Wann muss ich alle Schluessel zurueckgeben?", "expected_intent": "Frage", "expected_category": "Auszug"},
    {"query": "Wie vereinbare ich den Abnahmetermin?", "expected_intent": "Frage", "expected_category": "Auszug"},
    {"query": "Was passiert wenn ich die Wohnung nicht rechtzeitig raeme?", "expected_intent": "Frage", "expected_category": "Auszug"},
    {"query": "Ich bin unzufrieden, meine Kaution wurde nicht zurueckgezahlt.", "expected_intent": "Beschwerde", "expected_category": "Auszug"},
    {"query": "Wie lange hat der Vermieter Zeit die Kaution zurueckzuzahlen?", "expected_intent": "Frage", "expected_category": "Auszug"},
    {"query": "Was wird bei der Wohnungsabnahme geprueft?", "expected_intent": "Frage", "expected_category": "Auszug"},
    {"query": "Kann der Vermieter Kosten von der Kaution abziehen?", "expected_intent": "Frage", "expected_category": "Auszug"},

    # Konto (8 Faelle)
    {"query": "Wie registriere ich mich im Mieterportal?", "expected_intent": "Support", "expected_category": "Konto"},
    {"query": "Ich habe mein Passwort fuer das Mieterportal vergessen.", "expected_intent": "Support", "expected_category": "Konto"},
    {"query": "Kann ich meine Kontaktdaten im Portal aendern?", "expected_intent": "Frage", "expected_category": "Konto"},
    {"query": "Wie kann ich Dokumente im Portal hochladen?", "expected_intent": "Frage", "expected_category": "Konto"},
    {"query": "Ich habe keinen Registrierungslink erhalten.", "expected_intent": "Support", "expected_category": "Konto"},
    {"query": "Wie aendere ich meine E-Mail-Adresse im Portal?", "expected_intent": "Frage", "expected_category": "Konto"},
    {"query": "Kann ich meine Zahlungshistorie im Portal einsehen?", "expected_intent": "Frage", "expected_category": "Konto"},
    {"query": "Mein Konto wurde gesperrt, was kann ich tun?", "expected_intent": "Support", "expected_category": "Konto"},

    # Technisch (8 Faelle)
    {"query": "Das Mieterportal laedt nicht, was kann ich tun?", "expected_intent": "Support", "expected_category": "Technisch"},
    {"query": "Warum kann ich mich nicht im Portal anmelden?", "expected_intent": "Support", "expected_category": "Technisch"},
    {"query": "Welche Browser werden unterstuetzt?", "expected_intent": "Frage", "expected_category": "Technisch"},
    {"query": "Ich bekomme keine E-Mails vom Portal.", "expected_intent": "Support", "expected_category": "Technisch"},
    {"query": "Die App stuerzt immer ab wenn ich mich anmelden moechte.", "expected_intent": "Support", "expected_category": "Technisch"},
    {"query": "Meine Dokumente koennen nicht hochgeladen werden.", "expected_intent": "Support", "expected_category": "Technisch"},
    {"query": "Das Portal zeigt einen Fehler an.", "expected_intent": "Support", "expected_category": "Technisch"},
    {"query": "Funktioniert das Portal auch auf dem Smartphone?", "expected_intent": "Frage", "expected_category": "Technisch"},

    # Allgemein (17 Faelle)
    {"query": "Wie erreiche ich die Hausverwaltung?", "expected_intent": "Frage", "expected_category": "Allgemein"},
    {"query": "Wann sind die Geschaeftszeiten?", "expected_intent": "Frage", "expected_category": "Allgemein"},
    {"query": "Wie reiche ich eine Beschwerde ein?", "expected_intent": "Beschwerde", "expected_category": "Allgemein"},
    {"query": "Wer ist mein Ansprechpartner?", "expected_intent": "Frage", "expected_category": "Allgemein"},
    {"query": "Darf ich in meiner Wohnung rauchen?", "expected_intent": "Frage", "expected_category": "Allgemein"},
    {"query": "Was sind die Ruhezeiten im Haus?", "expected_intent": "Frage", "expected_category": "Allgemein"},
    {"query": "Wie beantrage ich einen Parkplatz?", "expected_intent": "Frage", "expected_category": "Allgemein"},
    {"query": "Was ist die Hausordnung und wo finde ich sie?", "expected_intent": "Frage", "expected_category": "Allgemein"},
    {"query": "Mein Nachbar macht sehr viel Laerm, was kann ich tun?", "expected_intent": "Beschwerde", "expected_category": "Allgemein"},
    {"query": "Ich moechte einen Hund anschaffen, ist das erlaubt?", "expected_intent": "Frage", "expected_category": "Allgemein"},
    {"query": "Ich bin sehr unzufrieden mit dem Service der Hausverwaltung.", "expected_intent": "Beschwerde", "expected_category": "Allgemein"},
    {"query": "Gibt es einen Keller fuer meine Wohnung?", "expected_intent": "Frage", "expected_category": "Allgemein"},
    {"query": "Wie melde ich einen Nachbarschaftsstreit?", "expected_intent": "Beschwerde", "expected_category": "Allgemein"},
    {"query": "Kann ich eine Katze in meiner Wohnung halten?", "expected_intent": "Frage", "expected_category": "Allgemein"},
    {"query": "Wann findet die naechste Hausversammlung statt?", "expected_intent": "Frage", "expected_category": "Allgemein"},
    {"query": "Wie lautet die Telefonnummer der Hausverwaltung?", "expected_intent": "Frage", "expected_category": "Allgemein"},
    {"query": "Ich moechte eine Beschwerde ueber meinen Nachbarn einreichen.", "expected_intent": "Beschwerde", "expected_category": "Allgemein"},
]

# Anzahl Testfaelle anpassen - z.B. 30 fuer schnellen Durchlauf
MAX_TESTS = 100
def run_evaluation():
    agent = SupportAgent()
    results = []

    print(f"Starte Evaluation mit {len(TEST_SET)} Testfaellen...\n")

    for i, test in enumerate(TEST_SET[:MAX_TESTS], 1):
        print(f"  [{i:03d}/{len(TEST_SET)}] {test['query'][:60]}...")

        start = time.time()
        result = agent.run(test["query"])
        elapsed = round(time.time() - start, 2)

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
            "antwortzeit": elapsed,
            "answer_len": len(result["answer"])
        })

    df = pd.DataFrame(results)

    print("\n=== Evaluationsergebnisse ===")
    print(f"Testfaelle gesamt:    {len(df)}")
    print(f"Intent Accuracy:      {df['intent_correct'].mean():.1%}")
    print(f"Category Accuracy:    {df['category_correct'].mean():.1%}")
    print(f"Ø Confidence Score:   {df['confidence'].mean():.2f}")
    print(f"Eskalationsrate:      {df['escalated'].mean():.1%}")
    print(f"Ø Antwortzeit:        {df['antwortzeit'].mean():.2f} Sek.")
    print(f"Ø Antwortlaenge:      {df['answer_len'].mean():.0f} Zeichen")

    # Zielwert-Check
    print("\n=== Zielwert-Check ===")
    print(f"Intent Accuracy >= 85%:   {'OK' if df['intent_correct'].mean() >= 0.85 else 'NICHT ERREICHT'} ({df['intent_correct'].mean():.1%})")
    print(f"Ø Confidence > 0.65:      {'OK' if df['confidence'].mean() > 0.65 else 'NICHT ERREICHT'} ({df['confidence'].mean():.2f})")
    print(f"Eskalationsrate 10-25%:   {'OK' if 0.10 <= df['escalated'].mean() <= 0.25 else 'NICHT ERREICHT'} ({df['escalated'].mean():.1%})")
    print(f"Ø Antwortzeit < 3 Sek.:   {'OK' if df['antwortzeit'].mean() < 3.0 else 'NICHT ERREICHT'} ({df['antwortzeit'].mean():.2f} Sek.)")

    # Fehleranalyse
    wrong_intents = df[~df['intent_correct']][['query', 'expected_intent', 'got_intent']]
    if not wrong_intents.empty:
        print("\n=== Falsch klassifizierte Intents ===")
        print(wrong_intents.to_string(index=False))

    wrong_cats = df[~df['category_correct']][['query', 'expected_category', 'got_category']]
    if not wrong_cats.empty:
        print("\n=== Falsch klassifizierte Kategorien ===")
        print(wrong_cats.to_string(index=False))

    # Auswertung nach Kategorie
    print("\n=== Auswertung nach Kategorie ===")
    cat_stats = df.groupby('expected_category').agg(
        Anzahl=('query', 'count'),
        Intent_Accuracy=('intent_correct', 'mean'),
        Category_Accuracy=('category_correct', 'mean'),
        Avg_Confidence=('confidence', 'mean'),
        Eskalationsrate=('escalated', 'mean')
    ).round(2)
    print(cat_stats.to_string())

    os.makedirs("logs", exist_ok=True)
    df.to_csv("logs/evaluation_results.csv", index=False)
    print("\nErgebnisse gespeichert: logs/evaluation_results.csv")

    return df


if __name__ == "__main__":
    run_evaluation()