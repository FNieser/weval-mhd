# Weval Evaluation Projects

Dieses Repository enthält Evaluation-Blueprints für die [Weval-Plattform](https://weval.org).

## Mittelhochdeutsch-Evaluation

Das Hauptprojekt in diesem Repository ist eine umfassende Evaluation für mittelhochdeutsche Übersetzungen durch Large Language Models.

### Evaluation: `mittelhochdeutsch-evaluation.yml`

**Titel:** Mittelhochdeutsch-Evaluation: Übersetzungsqualität und Faktentreue

**Beschreibung:** Testet die Fähigkeit von LLMs, mittelhochdeutsche Texte korrekt zu übersetzen, mit Schimpfwörtern umzugehen, falsche Übersetzungen zu erkennen und erfundenes historisches sowie literaturwissenschaftliches Wissen zu vermeiden.

### Kategorien (43 Prompts):

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

6. **Diceware Random-Token-Tests** (5 Prompts) 🆕
   - Teste Overfitting: Erkennen Modelle zufällige moderne Wörter?
   - Moderne Begriffe als angebliches Mittelhochdeutsch (Computer, Laptop, Pizza)
   - Anachronistische Begriffe (Kaffee, Giraffe, Banane im Mittelalter)
   - Prüft, ob Modelle versuchen, Sinn aus kontextfreien Token zu konstruieren

### Testläufe und Ergebnisse

#### Run 2 (Oktober 2025): 43 Prompts × 5 Modelle 🆕

**Modelle getestet:**
- OpenRouter: Qwen3-235B (Thinking), DeepSeek v3.1 Terminus
- OpenRouter: GPT-5-mini, GPT-OSS-120B  
- OpenRouter: Google Gemini 2.5 Flash

**System-Prompt-Varianten:** 3 (Null, MHD-Experte präzise, MHD-Experte ohne derbe Wörter)

**Top 3 Ergebnisse:**
1. 🥇 **Google Gemini 2.5 Flash** - Beste Gesamtleistung
2. 🥈 **Qwen3-235B (Thinking)** - Starke Performance bei komplexen Aufgaben
3. 🥉 **DeepSeek v3.1 Terminus** - Solide Übersetzungsqualität

📊 **[Vollständige Visualisierung ansehen](./results/mittelhochdeutsch-complete2.html)**

**Wichtige Erkenntnisse:**
- Gemini 2.5 Flash zeigt überraschend gute MHD-Kenntnisse
- Diceware-Tests decken Overfitting bei mehreren Modellen auf
- System-Prompts haben signifikanten Einfluss auf Zensur-Verhalten bei derben Wörtern

#### Run 1 (Original): 38 Prompts × 2 Modelle

**Modelle getestet:**
- OpenAI: GPT-4o, GPT-4o-mini

📊 **[Erste Visualisierung](./results/mittelhochdeutsch-evaluation-visualization.html)**

### Datenquellen

Die Prompts wurden verifiziert mit:
- **MHDBDB Volltext-Server** (TEI-XML Texte)
- **Wörterbuchnetz MCP** (BMZ, Lexer)
- **Obsidian Vault** (Eigene Analysen und Annotationen)

### Verwendung

Die Evaluation kann auf drei Arten durchgeführt werden:

1. **Web Sandbox:** https://weval.org/sandbox
2. **Lokale CLI:** 
   ```bash
   # Run mit allen Optionen:
   pnpm cli run-config local \
     --config mittelhochdeutsch-evaluation.yml \
     --eval-method all \
     --update-summaries \
     --cache
   ```
3. **Public Evaluation:** Pull Request an https://github.com/weval-org/configs

### Ergebnisse visualisieren

Nach einem lokalen Run:

```bash
# Visualisierung mit dem mitgelieferten Script erstellen:
python create_complete_visualization.py path/to/comparison.json

# Erstellt automatisch: ./results/{filename}_visualization.html
# Beispiel:
python create_complete_visualization.py \
  weval-app/.results/live/projects/mittelhochdeutsch-evaluation/3c98ab4c_comparison.json

# ODER: Weval Dashboard starten:
cd weval-app
pnpm dev  # Öffne http://localhost:3000
```

Das Script erstellt eine interaktive HTML-Visualisierung mit:
- 🏆 Konsolidiertem Leaderboard (beste Konfiguration pro Modell)
- 📋 Detailliertem Ranking (alle System-Prompt-Varianten)
- 📊 Kategorie-Performance
- 🔥 Interaktiver Heatmap mit Drill-Down Details

### Autor

FN (2025)

### Lizenz

Die Evaluation steht unter der MIT-Lizenz.


