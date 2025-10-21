# Weval Evaluation Projects

Dieses Repository enthält Evaluation-Blueprints für die [Weval-Plattform](https://weval.org).

## Mittelhochdeutsch-Evaluation

Das Hauptprojekt in diesem Repository ist eine umfassende Evaluation für mittelhochdeutsche Übersetzungen durch Large Language Models.

### Evaluation: `mittelhochdeutsch-evaluation.yml`

**Titel:** Mittelhochdeutsch-Evaluation: Übersetzungsqualität und Faktentreue

**Beschreibung:** Testet die Fähigkeit von LLMs, mittelhochdeutsche Texte korrekt zu übersetzen, mit Schimpfwörtern umzugehen, falsche Übersetzungen zu erkennen und erfundenes historisches sowie literaturwissenschaftliches Wissen zu vermeiden.

### Kategorien (33 Prompts):

1. **Korrekte Übersetzungen** (11 Prompts)
   - Authentische mhd. Verse aus Nibelungenlied und Parzival
   - Höfische Konzepte (minne, tugent, êre, âventiure)
   - Falsche Freunde (ellende, ê)

2. **Schimpfwörter und derbe Ausdrücke** (7 Prompts)
   - Historische Schimpfwörter (schalc, gouch, tôr, zage)
   - Derbe Begriffe aus der Schwankliteratur
   - Anachronismus-Tests

3. **Falsche Übersetzungen erkennen** (5 Prompts)
   - Verwechslungen (schœne vs. schon)
   - Kasus-Fehler
   - Moderne Anachronismen

4. **Erfundenes Kontextwissen** (5 Prompts)
   - Nicht existierende Textstellen
   - Erfundene Sekundärliteratur
   - Falsche Etymologien

5. **Erfundenes historisches Wissen** (5 Prompts)
   - Erfundene Autoren
   - Nicht existierende historische Ereignisse
   - Falsche biografische Daten

### Datenquellen

Die Prompts wurden verifiziert mit:
- **MHDBDB Volltext-Server** (TEI-XML Texte)
- **Wörterbuchnetz MCP** (BMZ, Lexer)
- **Obsidian Vault** (Eigene Analysen und Annotationen)

### Verwendung

Die Evaluation kann auf drei Arten durchgeführt werden:

1. **Web Sandbox:** https://weval.org/sandbox
2. **Lokale CLI:** `pnpm cli run-config projects/mittelhochdeutsch-evaluation.yml`
3. **Public Evaluation:** Pull Request an https://github.com/weval-org/configs

### Autor

FN (2025)

### Lizenz

Die Evaluation steht unter der MIT-Lizenz.


