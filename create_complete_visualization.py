import json
import sys
from pathlib import Path
from collections import defaultdict

def get_category(prompt_id):
    if prompt_id.startswith('mhd-trans'):
        return 'Übersetzungen'
    if prompt_id.startswith('mhd-insult'):
        return 'Schimpfwörter'
    if prompt_id.startswith('mhd-false-trans'):
        return 'Falsche Übersetzungen'
    if prompt_id.startswith('mhd-context-fake'):
        return 'Erfundener Kontext'
    if prompt_id.startswith('mhd-history-fake'):
        return 'Erfundene Geschichte'
    if prompt_id.startswith('mhd-curse'):
        return 'Flüche'
    return 'Andere'

def simplify_model_name(model_id):
    name = model_id.split('[')[0].strip()
    if ':' in name:
        parts = name.split(':')
        return parts[-1]
    return name

def get_color_class(score):
    if score is None:
        return 'error'
    if score >= 90:
        return 'excellent'
    if score >= 70:
        return 'good'
    if score >= 50:
        return 'medium'
    if score > 0:
        return 'poor'
    return 'bad'

def extract_data(data):
    """Extrahiert alle Daten für die Visualisierung"""
    
    # Extrahiere Prompt-Definitionen
    config = data.get('config', {})
    prompt_defs = config.get('prompts', [])
    
    prompts_data = {}
    for prompt_def in prompt_defs:
        prompt_id = prompt_def.get('id')
        prompt_text = ''
        messages = prompt_def.get('messages', [])
        for msg in messages:
            if msg.get('role') == 'user':
                prompt_text = msg.get('content', '')
                break
        
        should_criteria = []
        should_not_criteria = []
        
        for point in prompt_def.get('points', []):
            if isinstance(point, dict):
                should_criteria.append(point.get('text', ''))
        
        for point in prompt_def.get('should_not', []):
            if isinstance(point, dict):
                should_not_criteria.append(point.get('text', ''))
        
        prompts_data[prompt_id] = {
            'description': prompt_def.get('description', ''),
            'prompt': prompt_text,
            'ideal': prompt_def.get('idealResponse', ''),
            'should': should_criteria,
            'should_not': should_not_criteria,
            'category': get_category(prompt_id)
        }
    
    # Extrahiere Modelle
    effective_models = [m for m in data.get('effectiveModels', []) if m != 'IDEAL_BENCHMARK']
    
    # Extrahiere Antworten
    all_responses = data.get('allFinalAssistantResponses', {})
    
    # Extrahiere Scores aus evaluationResults.llmCoverageScores
    eval_results = data.get('evaluationResults', {})
    llm_scores = eval_results.get('llmCoverageScores', {})
    
    # Baue Ergebnis-Matrix auf
    results = {}
    for prompt_id in prompts_data.keys():
        results[prompt_id] = {}
        prompt_responses = all_responses.get(prompt_id, {})
        prompt_scores = llm_scores.get(prompt_id, {})
        
        for model_id in effective_models:
            response_text = prompt_responses.get(model_id, '')
            model_score_data = prompt_scores.get(model_id, {})
            
            # Extrahiere Score
            score = None
            if isinstance(model_score_data, dict):
                avg_coverage = model_score_data.get('avgCoverageExtent')
                if avg_coverage is not None:
                    score = avg_coverage * 100
            
            # Extrahiere Kriterien-Ergebnisse
            passed_criteria = []
            failed_criteria = []
            
            point_assessments = model_score_data.get('pointAssessments', [])
            for assessment in point_assessments:
                criterion_text = assessment.get('keyPointText', '')
                coverage = assessment.get('coverageExtent', 0) * 100
                is_inverted = assessment.get('isInverted', False)
                
                if is_inverted:
                    if coverage >= 50:
                        passed_criteria.append({'text': criterion_text, 'score': coverage})
                    else:
                        failed_criteria.append({'text': criterion_text, 'score': coverage})
                else:
                    if coverage >= 50:
                        passed_criteria.append({'text': criterion_text, 'score': coverage})
                    else:
                        failed_criteria.append({'text': criterion_text, 'score': coverage})
            
            # Handle errors
            is_error = isinstance(response_text, str) and '<<error>>' in response_text
            
            results[prompt_id][model_id] = {
                'score': score,
                'output': response_text if isinstance(response_text, str) else '',
                'passed': passed_criteria,
                'failed': failed_criteria,
                'is_error': is_error
            }
    
    return results, effective_models, list(prompts_data.keys()), prompts_data

def get_system_prompt_info(model_id):
    """Extrahiert System-Prompt-Info aus der Model-ID"""
    if 'sp_idx:0' in model_id:
        return 'Kein System-Prompt'
    elif 'sp_idx:1' in model_id:
        return 'System: MHD-Experte (präzise)'
    elif 'sp_idx:2' in model_id:
        return 'System: MHD-Experte (keine derben Wörter)'
    return 'Standard'

def get_base_model_name(model_id):
    """Extrahiert den Basis-Modellnamen ohne Konfiguration"""
    return model_id.split('[')[0].strip()

def calculate_statistics(results, models, prompts, prompts_data):
    """Berechnet Statistiken und Rankings"""
    
    # Model Statistics (für alle Konfigurationen)
    model_stats = {}
    for model in models:
        scores = []
        errors = 0
        category_scores = defaultdict(list)
        
        for prompt_id in prompts:
            if prompt_id in results and model in results[prompt_id]:
                result = results[prompt_id][model]
                if result['is_error']:
                    errors += 1
                elif result['score'] is not None:
                    scores.append(result['score'])
                    category = prompts_data[prompt_id]['category']
                    category_scores[category].append(result['score'])
        
        if scores:
            model_stats[model] = {
                'avg': sum(scores) / len(scores),
                'min': min(scores),
                'max': max(scores),
                'count': len(scores),
                'errors': errors,
                'category_avg': {cat: sum(s)/len(s) for cat, s in category_scores.items() if s},
                'base_name': get_base_model_name(model),
                'sp_info': get_system_prompt_info(model)
            }
        else:
            model_stats[model] = {
                'avg': 0,
                'min': 0,
                'max': 0,
                'count': 0,
                'errors': errors,
                'category_avg': {},
                'base_name': get_base_model_name(model),
                'sp_info': get_system_prompt_info(model)
            }
    
    # Detailed Ranking (alle Konfigurationen)
    detailed_ranking = sorted(model_stats.items(), key=lambda x: x[1]['avg'], reverse=True)
    
    # Consolidated Ranking (beste Konfiguration pro Basis-Modell)
    base_model_best = {}
    for model_id, stats in model_stats.items():
        base_name = stats['base_name']
        if base_name not in base_model_best or stats['avg'] > base_model_best[base_name][1]['avg']:
            base_model_best[base_name] = (model_id, stats)
    
    consolidated_ranking = sorted(base_model_best.values(), key=lambda x: x[1]['avg'], reverse=True)
    
    # Category Best Models (nur beste Konfiguration pro Basis-Modell)
    categories = set(p['category'] for p in prompts_data.values())
    category_best = {}
    for category in categories:
        cat_scores = {}
        for base_name, (model_id, stats) in base_model_best.items():
            if category in stats['category_avg']:
                cat_scores[model_id] = stats['category_avg'][category]
        if cat_scores:
            best_model = max(cat_scores.items(), key=lambda x: x[1])
            category_best[category] = best_model
    
    return model_stats, consolidated_ranking, detailed_ranking, category_best

def create_html(data, output_path):
    print("Extrahiere Daten...")
    results, models, prompts, prompts_data = extract_data(data)
    
    print("Berechne Statistiken...")
    model_stats, consolidated_ranking, detailed_ranking, category_best = calculate_statistics(results, models, prompts, prompts_data)
    
    print("Erstelle HTML...")
    
    # Simplified model names
    model_headers = [simplify_model_name(m) for m in models]
    
    # Build HTML
    html = f'''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mittelhochdeutsch Evaluation - Vollständige Ergebnisse</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1800px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ font-size: 1.1em; opacity: 0.9; }}
        
        .tabs {{
            display: flex;
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
        }}
        
        .tab {{
            flex: 1;
            padding: 15px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: 600;
            border-bottom: 3px solid transparent;
        }}
        
        .tab:hover {{ background: #e9ecef; }}
        .tab.active {{ background: white; border-bottom-color: #667eea; color: #667eea; }}
        
        .tab-content {{
            display: none;
            padding: 30px;
        }}
        
        .tab-content.active {{ display: block; }}
        
        /* Leaderboard */
        .leaderboard {{
            display: grid;
            gap: 15px;
        }}
        
        .leaderboard-item {{
            display: grid;
            grid-template-columns: 60px 1fr 100px;
            align-items: center;
            padding: 20px;
            background: white;
            border-radius: 8px;
            border: 2px solid #e9ecef;
            transition: all 0.3s;
        }}
        
        .leaderboard-item:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }}
        
        .rank {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            text-align: center;
        }}
        
        .rank.gold {{ color: #FFD700; }}
        .rank.silver {{ color: #C0C0C0; }}
        .rank.bronze {{ color: #CD7F32; }}
        
        .model-info {{
            padding: 0 20px;
        }}
        
        .model-name {{
            font-size: 1.3em;
            font-weight: 600;
            margin-bottom: 8px;
        }}
        
        .model-details {{
            font-size: 0.9em;
            color: #6c757d;
        }}
        
        .model-score {{
            text-align: right;
        }}
        
        .score-big {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .score-label {{
            font-size: 0.8em;
            color: #6c757d;
        }}
        
        /* Category Performance */
        .category-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .category-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        
        .category-card h3 {{
            color: #667eea;
            margin-bottom: 15px;
        }}
        
        .category-winner {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            background: white;
            border-radius: 6px;
            margin-top: 10px;
        }}
        
        /* Matrix/Heatmap */
        .matrix-container {{
            overflow-x: auto;
        }}
        
        .matrix-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9em;
        }}
        
        .matrix-table th {{
            background: #667eea;
            color: white;
            padding: 12px 8px;
            text-align: center;
            font-weight: 600;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        
        .matrix-table th.prompt-header {{
            text-align: left;
            min-width: 250px;
        }}
        
        .matrix-table td {{
            padding: 8px;
            text-align: center;
            border: 1px solid #e9ecef;
        }}
        
        .matrix-table td.prompt-cell {{
            text-align: left;
            font-weight: 500;
            background: #f8f9fa;
        }}
        
        .category-label {{
            font-size: 0.75em;
            color: #6c757d;
            margin-bottom: 4px;
        }}
        
        .score-cell {{
            cursor: pointer;
            transition: all 0.2s;
            font-weight: 600;
        }}
        
        .score-cell:hover {{
            transform: scale(1.1);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            z-index: 5;
        }}
        
        .excellent {{ background: #d4edda; color: #155724; }}
        .good {{ background: #fff3cd; color: #856404; }}
        .medium {{ background: #ffe5b4; color: #8b4513; }}
        .poor {{ background: #f8d7da; color: #721c24; }}
        .bad {{ background: #dc3545; color: white; }}
        .error {{ background: #e0e0e0; color: #666; }}
        
        /* Modal */
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgba(0,0,0,0.7);
        }}
        
        .modal-content {{
            background-color: #fefefe;
            margin: 2% auto;
            padding: 0;
            border-radius: 12px;
            width: 90%;
            max-width: 1200px;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        }}
        
        .modal-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 30px;
            border-radius: 12px 12px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .close {{
            color: white;
            font-size: 32px;
            font-weight: bold;
            cursor: pointer;
        }}
        
        .close:hover {{ transform: scale(1.2); }}
        
        .modal-body {{ padding: 30px; }}
        
        .prompt-info {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        
        .prompt-info h3 {{ color: #667eea; margin-bottom: 10px; }}
        
        .prompt-text, .ideal-response, .model-output {{
            background: white;
            padding: 15px;
            border-radius: 6px;
            margin: 10px 0;
            white-space: pre-wrap;
            line-height: 1.6;
        }}
        
        .prompt-text {{ border-left: 4px solid #667eea; }}
        .ideal-response {{ border-left: 4px solid #28a745; background: #d4edda; }}
        
        .model-result {{
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        
        .model-result h3 {{
            color: #667eea;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
        }}
        
        .score-badge {{
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        
        .criteria-item {{
            padding: 10px 15px;
            margin: 8px 0;
            border-radius: 6px;
            display: flex;
            justify-content: space-between;
        }}
        
        .criteria-item.passed {{ background: #d4edda; border-left: 4px solid #28a745; }}
        .criteria-item.failed {{ background: #f8d7da; border-left: 4px solid #dc3545; }}
        
        .legend {{
            display: flex;
            justify-content: center;
            gap: 20px;
            padding: 20px;
            background: #f8f9fa;
            margin-top: 20px;
            border-radius: 8px;
        }}
        
        .legend-item {{ display: flex; align-items: center; gap: 8px; }}
        .legend-color {{ width: 30px; height: 20px; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Mittelhochdeutsch Evaluation</h1>
            <p>Übersetzungsqualität und Faktentreue - {len(prompts)} Prompts × {len(models)} Modelle</p>
        </div>
        
        <div class="tabs">
            <div class="tab active" onclick="showTab('leaderboard')">🏆 Leaderboard</div>
            <div class="tab" onclick="showTab('detailed')">📋 Detailliert</div>
            <div class="tab" onclick="showTab('categories')">📊 Kategorien</div>
            <div class="tab" onclick="showTab('heatmap')">🔥 Heatmap</div>
        </div>
        
        <div id="leaderboard" class="tab-content active">
            <h2 style="margin-bottom: 10px; color: #667eea;">🏆 Model Ranking</h2>
            <p style="margin-bottom: 20px; color: #6c757d; font-size: 0.95em;">
                Beste Konfiguration pro Modell (von {len(detailed_ranking)} getesteten Konfigurationen)
            </p>
            <div class="leaderboard">
'''
    
    # Consolidated Leaderboard
    for idx, (model_id, stats) in enumerate(consolidated_ranking, 1):
        model_name = simplify_model_name(model_id)
        rank_class = ''
        if idx == 1:
            rank_class = 'gold'
        elif idx == 2:
            rank_class = 'silver'
        elif idx == 3:
            rank_class = 'bronze'
        
        # Berechne Success Rate
        total_tests = stats['count'] + stats['errors']
        success_rate = (stats['count'] / total_tests * 100) if total_tests > 0 else 0
        
        html += f'''
                <div class="leaderboard-item">
                    <div class="rank {rank_class}">{idx}</div>
                    <div class="model-info">
                        <div class="model-name">{model_name}</div>
                        <div class="model-details">
                            {stats['sp_info']}<br>
                            Min: {stats['min']:.1f}% | Max: {stats['max']:.1f}% | 
                            Erfolgreiche Tests: {stats['count']}/{total_tests} ({success_rate:.1f}%)
                            {f' | <span style="color: #dc3545; font-weight: bold;">⚠️ {stats["errors"]} Fehler</span>' if stats['errors'] > 0 else ''}
                        </div>
                    </div>
                    <div class="model-score">
                        <div class="score-big">{stats['avg']:.1f}%</div>
                        <div class="score-label">Durchschnitt</div>
                    </div>
                </div>
'''
    
    html += '''
            </div>
        </div>
        
        <div id="detailed" class="tab-content">
            <h2 style="margin-bottom: 10px; color: #667eea;">📋 Alle Konfigurationen</h2>
            <p style="margin-bottom: 20px; color: #6c757d; font-size: 0.95em;">
                Vergleich aller System-Prompt-Varianten pro Modell
            </p>
            <div class="leaderboard">
'''
    
    # Detailed Leaderboard
    for idx, (model_id, stats) in enumerate(detailed_ranking, 1):
        model_name = simplify_model_name(model_id)
        
        # Berechne Success Rate
        total_tests = stats['count'] + stats['errors']
        success_rate = (stats['count'] / total_tests * 100) if total_tests > 0 else 0
        
        html += f'''
                <div class="leaderboard-item">
                    <div class="rank">{idx}</div>
                    <div class="model-info">
                        <div class="model-name">{model_name}</div>
                        <div class="model-details">
                            {stats['sp_info']}<br>
                            Min: {stats['min']:.1f}% | Max: {stats['max']:.1f}% | 
                            Erfolgreiche Tests: {stats['count']}/{total_tests} ({success_rate:.1f}%)
                            {f' | <span style="color: #dc3545; font-weight: bold;">⚠️ {stats["errors"]} Fehler</span>' if stats['errors'] > 0 else ''}
                        </div>
                    </div>
                    <div class="model-score">
                        <div class="score-big">{stats['avg']:.1f}%</div>
                        <div class="score-label">Durchschnitt</div>
                    </div>
                </div>
'''
    
    html += '''
            </div>
        </div>
        
        <div id="categories" class="tab-content">
            <h2 style="margin-bottom: 20px; color: #667eea;">📊 Leistung nach Kategorien</h2>
            <div class="category-grid">
'''
    
    # Category Performance
    for category, (best_model, best_score) in category_best.items():
        model_name = simplify_model_name(best_model)
        html += f'''
                <div class="category-card">
                    <h3>{category}</h3>
                    <div class="category-winner">
                        <span><strong>Bestes Modell:</strong> {model_name}</span>
                        <span style="font-size: 1.5em; font-weight: bold; color: #667eea;">{best_score:.1f}%</span>
                    </div>
'''
        
        # Show all models for this category
        html += '<div style="margin-top: 15px; font-size: 0.9em;">'
        for model in models:
            if category in model_stats[model]['category_avg']:
                score = model_stats[model]['category_avg'][category]
                model_name_short = simplify_model_name(model)
                color = get_color_class(score)
                html += f'<div style="display: flex; justify-content: space-between; padding: 5px; margin: 3px 0; background: white; border-radius: 4px;"><span>{model_name_short}</span><span class="{color}" style="padding: 2px 8px; border-radius: 3px;">{score:.1f}%</span></div>'
        html += '</div></div>'
    
    html += '''
            </div>
        </div>
        
        <div id="heatmap" class="tab-content">
            <h2 style="margin-bottom: 20px; color: #667eea;">🔥 Detaillierte Heatmap</h2>
            <div class="matrix-container">
                <table class="matrix-table">
                    <thead>
                        <tr>
                            <th class="prompt-header">Prompt</th>
'''
    
    for header in model_headers:
        html += f'                            <th>{header}</th>\n'
    
    html += '''
                        </tr>
                    </thead>
                    <tbody>
'''
    
    # Heatmap rows
    for prompt_id in prompts:
        category = prompts_data[prompt_id]['category']
        html += f'''
                        <tr>
                            <td class="prompt-cell">
                                <div class="category-label">{category}</div>
                                <div>{prompt_id}</div>
                            </td>
'''
        
        for model_id in models:
            if prompt_id in results and model_id in results[prompt_id]:
                result = results[prompt_id][model_id]
                score = result['score']
                color_class = get_color_class(score)
                score_display = f"{score:.0f}%" if score is not None else "N/A"
                
                html += f'                            <td class="score-cell {color_class}" onclick="showDetails(\'{prompt_id}\', \'{model_id}\')">{score_display}</td>\n'
            else:
                html += '                            <td class="score-cell error">N/A</td>\n'
        
        html += '                        </tr>\n'
    
    html += '''
                    </tbody>
                </table>
                
                <div class="legend">
                    <div class="legend-item">
                        <div class="legend-color excellent"></div>
                        <span>Exzellent (≥90%)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color good"></div>
                        <span>Gut (70-89%)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color medium"></div>
                        <span>Mittel (50-69%)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color poor"></div>
                        <span>Schwach (1-49%)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color error"></div>
                        <span>Fehler</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div id="detailModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="modalTitle">Details</h2>
                <span class="close" onclick="closeModal()">&times;</span>
            </div>
            <div class="modal-body" id="modalBody"></div>
        </div>
    </div>
    
    <script>
        const promptsData = ''' + json.dumps(prompts_data, ensure_ascii=False) + ''';
        const resultsData = ''' + json.dumps(results, ensure_ascii=False) + ''';
        
        function showTab(tabName) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById(tabName).classList.add('active');
        }
        
        function simplifyModelName(modelId) {
            const name = modelId.split('[')[0].trim();
            return name.includes(':') ? name.split(':').pop() : name;
        }
        
        function getColorClass(score) {
            if (!score) return 'error';
            if (score >= 90) return 'excellent';
            if (score >= 70) return 'good';
            if (score >= 50) return 'medium';
            if (score > 0) return 'poor';
            return 'bad';
        }
        
        function showDetails(promptId, modelId) {
            const modal = document.getElementById('detailModal');
            const modalBody = document.getElementById('modalBody');
            const modalTitle = document.getElementById('modalTitle');
            
            const promptData = promptsData[promptId];
            const result = resultsData[promptId][modelId];
            
            const modelName = simplifyModelName(modelId);
            const score = result.score;
            const colorClass = getColorClass(score);
            const scoreDisplay = score !== null ? score.toFixed(1) + '%' : 'N/A';
            
            modalTitle.textContent = promptId;
            
            let html = `
                <div class="prompt-info">
                    <h3>Prompt</h3>
                    <div class="prompt-text">${promptData.prompt}</div>
                    
                    <h3 style="margin-top: 20px;">Ideale Antwort</h3>
                    <div class="ideal-response">${promptData.ideal}</div>
                </div>
                
                <div class="model-result">
                    <h3>
                        <span>${modelName}</span>
                        <span class="score-badge ${colorClass}">${scoreDisplay}</span>
                    </h3>
                    
                    <h4>Modell-Antwort:</h4>
                    <div class="model-output">${result.output || 'Keine Antwort'}</div>
                    
                    ${result.passed && result.passed.length > 0 ? `
                    <div style="margin-top: 20px;">
                        <h4 style="color: #28a745;">Erfüllte Kriterien (${result.passed.length})</h4>
                        ${result.passed.map(c => `
                            <div class="criteria-item passed">
                                <span>${c.text}</span>
                                <span><strong>${c.score.toFixed(0)}%</strong></span>
                            </div>
                        `).join('')}
                    </div>
                    ` : ''}
                    
                    ${result.failed && result.failed.length > 0 ? `
                    <div style="margin-top: 20px;">
                        <h4 style="color: #dc3545;">Nicht erfüllte Kriterien (${result.failed.length})</h4>
                        ${result.failed.map(c => `
                            <div class="criteria-item failed">
                                <span>${c.text}</span>
                                <span><strong>${c.score.toFixed(0)}%</strong></span>
                            </div>
                        `).join('')}
                    </div>
                    ` : ''}
                </div>
            `;
            
            modalBody.innerHTML = html;
            modal.style.display = 'block';
        }
        
        function closeModal() {
            document.getElementById('detailModal').style.display = 'none';
        }
        
        window.onclick = function(event) {
            const modal = document.getElementById('detailModal');
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        }
        
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                closeModal();
            }
        });
    </script>
</body>
</html>'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✅ Vollständige Visualisierung erstellt!")
    print(f"📊 {len(prompts)} Prompts x {len(models)} Modelle ({len(detailed_ranking)} Konfigurationen)")
    print(f"🏆 Top 3: {', '.join([simplify_model_name(m) for m, _ in consolidated_ranking[:3]])}")
    print(f"📁 Datei: {output_path}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python create_complete_visualization.py <path_to_comparison_json>")
        sys.exit(1)
    
    json_path = Path(sys.argv[1])
    if not json_path.exists():
        print(f"Error: File not found at {json_path}")
        sys.exit(1)
    
    output_dir = Path('c:/Users/fnies/cursortest/weval/upload-to-weval')
    output_dir.mkdir(parents=True, exist_ok=True)
    output_html_path = output_dir / 'mittelhochdeutsch-complete.html'
    
    print("Lade JSON-Daten...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    create_html(data, output_html_path)

if __name__ == "__main__":
    main()

