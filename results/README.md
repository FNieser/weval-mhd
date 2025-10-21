# Mittelhochdeutsch LLM Evaluation - Ergebnisse

Vollständige Ergebnisse der Evaluation von 5 Large Language Models auf ihre Fähigkeit, mittelhochdeutsche Texte korrekt zu übersetzen und mit historischem Wissen umzugehen.

## 📊 Übersicht

- **Getestete Modelle**: 5 (mit je 3 System-Prompt-Varianten = 15 Konfigurationen)
- **Test-Prompts**: 34
- **Kategorien**: 
  - Übersetzungen (12 Prompts)
  - Schimpfwörter/Flüche (6 Prompts)
  - Falsche Übersetzungen erkennen (5 Prompts)
  - Erfundener Kontext (6 Prompts)
  - Erfundene Geschichte (5 Prompts)

## 🏆 Ergebnisse (Hauptranking)

### Top 5 Modelle

1. **🥇 Claude 3.5 Sonnet** (Anthropic) - **90.6%**
   - Min: 41.0% | Max: 100.0%
   - 34/34 Tests erfolgreich
   - Beste Konfiguration: Mit System-Prompt (MHD-Experte, präzise)

2. **🥈 GPT-4o** (OpenAI) - **82.8%**
   - Min: 37.0% | Max: 100.0%
   - 34/34 Tests erfolgreich
   - Beste Konfiguration: Mit System-Prompt (MHD-Experte, präzise)

3. **🥉 Llama 3.1 70B Instruct** (Meta) - **73.0%**
   - Min: 0.0% | Max: 100.0%
   - 34/34 Tests erfolgreich
   - Beste Konfiguration: Mit System-Prompt (MHD-Experte, keine derben Wörter)

4. **GPT-4o-mini** (OpenAI) - **67.5%**
   - Min: 0.0% | Max: 100.0%
   - 34/34 Tests erfolgreich

5. **Gemini Pro 1.5** (Google) - **0.0%**
   - ⚠️ 34/34 Tests fehlgeschlagen (Circuit Breaker Fehler)

## 📁 Dateien

### Visualisierungen
- **[mittelhochdeutsch-complete.html](mittelhochdeutsch-complete.html)** - Interaktive Visualisierung mit:
  - 🏆 Leaderboard (konsolidiert)
  - 📋 Detaillierte Rankings (alle 15 Konfigurationen)
  - 📊 Kategorien-Analyse
  - 🔥 Heatmap (klickbar für Details)

### Rohdaten
- **[evaluation-results.zip](evaluation-results.zip)** - Komprimierte JSON-Ergebnisse (478 KB)
- **[mittelhochdeutsch-evaluation.yml](mittelhochdeutsch-evaluation.yml)** - Blueprint mit allen Test-Prompts

### Vollständige JSON
Die vollständige `evaluation-results.json` (5.4 MB) ist zu groß für Git und ist im ZIP enthalten.

## 🎯 Wichtigste Erkenntnisse

### Stärken nach Kategorie

- **Übersetzungen**: Claude 3.5 Sonnet (96.2%)
- **Schimpfwörter**: Claude 3.5 Sonnet (92.1%)
- **Falsche Übersetzungen erkennen**: Claude 3.5 Sonnet (91.3%)
- **Erfundener Kontext vermeiden**: Claude 3.5 Sonnet (87.4%)
- **Erfundene Geschichte vermeiden**: GPT-4o (85.6%)

### System-Prompt-Effektivität

Der System-Prompt **"Du bist ein Experte für mittelhochdeutsche Sprache und Literatur. Übersetze präzise und gestehe Unwissenheit ein"** zeigte durchweg die besten Ergebnisse über alle Modelle hinweg.

### Besondere Beobachtungen

1. **Claude 3.5 Sonnet** ist deutlicher Marktführer mit 90.6% Gesamtscore
2. **GPT-4o** liegt solide auf Platz 2 mit 82.8%
3. **Llama 3.1 70B** zeigt als Open-Source-Modell respektable 73.0%
4. **Gemini Pro 1.5** hatte technische Probleme (API-Fehler: "No endpoints found")
5. Die **Miniatur-Version GPT-4o-mini** erreicht 67.5% - beachtlich für ihre Größe

## 📖 Verwendung

### Visualisierung öffnen

Die HTML-Datei kann direkt im Browser geöffnet werden:

```bash
# Windows
start mittelhochdeutsch-complete.html

# Mac/Linux
open mittelhochdeutsch-complete.html
```

### Interaktive Features

- **Tabs wechseln**: Zwischen Leaderboard, Details, Kategorien und Heatmap navigieren
- **Heatmap klicken**: Auf einzelne Scores klicken für detaillierte Analyse
- **Modal schließen**: ESC-Taste oder X-Button

## 🔧 Evaluation-Setup

Die Evaluation wurde durchgeführt mit:
- **Platform**: [Weval](https://weval.ai)
- **Datum**: 21. Oktober 2025
- **Judge-Modelle**: Qwen 3 30B, GLM-4.5, GPT-OSS-120B
- **Evaluation-Methode**: Coverage-basierte Kriterien-Bewertung

## 📚 Test-Blueprint

Die vollständige Test-Suite ist in `mittelhochdeutsch-evaluation.yml` definiert und umfasst:

- Klassische mittelhochdeutsche Texte (Nibelungenlied, Parzival)
- Falsche Freunde (z.B. "ellende" ≠ "elend")
- Historische Namen und Begriffe
- Schimpfwörter und derbe Sprache
- Halluzinations-Tests (erfundene Werke, Autoren, Ereignisse)

## 🤝 Zitation

Wenn du diese Evaluation in deiner Forschung verwendest, referenziere bitte:

```
Nieser, F. (2025). Mittelhochdeutsch LLM Evaluation.
GitHub Repository: https://github.com/FNieser/weval-mhd
```

## 📄 Lizenz

Die Test-Suite und Ergebnisse stehen unter MIT License.

## 🔗 Links

- **GitHub Repository**: https://github.com/FNieser/weval-mhd
- **Weval Platform**: https://weval.ai
- **Kontakt**: [@FNieser](https://github.com/FNieser)

---

*Generiert am: 21. Oktober 2025*  
*Evaluation ID: bac13a55e27a871d*
