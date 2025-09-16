#!/usr/bin/env python3
"""
Orbis Modellfabrik - Dokumentationsindex Generator

Generiert automatisch INDEX.html und INDEX.json aus allen Markdown-Dateien.
"""

import json
from datetime import datetime
from pathlib import Path


def find_markdown_files():
    """Finde alle Markdown-Dateien im docs_orbis Verzeichnis."""
    docs_dir = Path("docs_orbis")
    md_files = []

    for md_file in docs_dir.rglob("*.md"):
        if md_file.name != "README.md":  # README.md separat behandeln
            relative_path = md_file.relative_to(docs_dir)
            md_files.append(
                {"path": str(relative_path), "name": md_file.stem, "category": _get_category(relative_path)}
            )

    return sorted(md_files, key=lambda x: x["path"])


def _get_category(relative_path):
    """Bestimme Kategorie basierend auf Pfad."""
    path_str = str(relative_path)

    if "node-red" in path_str:
        return "Node-RED Dokumentation"
    elif "guides/communication" in path_str:
        return "MQTT & Kommunikation"
    elif "guides/configuration" in path_str:
        return "Konfiguration"
    elif "analysis" in path_str:
        return "Analyse & Dokumentation"
    elif "implementation" in path_str or "development" in path_str:
        return "Entwicklung & Implementation"
    elif "releases" in path_str:
        return "Releases & Changelog"
    elif "guides/troubleshooting" in path_str:
        return "Troubleshooting & Support"
    elif "requirements" in path_str:
        return "Requirements & Specifications"
    elif "helper_apps" in path_str:
        return "Helper Apps"
    elif "factory" in path_str or "fts" in path_str:
        return "Factory & Production"
    else:
        return "Projekt-Übersicht"


def generate_keywords(file_info):
    """Generiere Keywords basierend auf Dateiname und Pfad."""
    keywords = []

    # Aus Pfad extrahieren
    path_parts = file_info["path"].lower().replace(".md", "").split("/")
    keywords.extend(path_parts)

    # Aus Dateiname extrahieren
    name_parts = file_info["name"].lower().replace("-", " ").replace("_", " ").split()
    keywords.extend(name_parts)

    # Spezielle Keywords
    if "mqtt" in file_info["path"].lower():
        keywords.extend(["mqtt", "communication", "broker"])
    if "dashboard" in file_info["path"].lower():
        keywords.extend(["dashboard", "ui", "interface"])
    if "node-red" in file_info["path"].lower():
        keywords.extend(["node-red", "flows", "automation"])
    if "release" in file_info["path"].lower():
        keywords.extend(["release", "version", "changelog"])
    if "troubleshooting" in file_info["path"].lower():
        keywords.extend(["troubleshooting", "debug", "problem"])

    return list(set(keywords))  # Duplikate entfernen


def generate_html_index(md_files):
    """Generiere INDEX.html."""
    html_content = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Orbis Modellfabrik - Dokumentationsindex</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6; margin: 0; padding: 20px; background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px; margin: 0 auto; background: white;
            padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        .search-container {{ margin: 20px 0; position: relative; }}
        #search {{
            width: 100%; padding: 12px; font-size: 16px;
            border: 2px solid #ddd; border-radius: 6px; box-sizing: border-box;
        }}
        .category {{ margin: 30px 0; }}
        .category h2 {{
            color: #34495e; background: #ecf0f1;
            padding: 10px 15px; margin: 0 0 15px 0; border-radius: 4px;
        }}
        .doc-list {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
        }}
        .doc-item {{
            border: 1px solid #ddd; border-radius: 6px;
            padding: 15px; background: #fafafa; transition: all 0.3s ease;
        }}
        .doc-item:hover {{
            background: #e8f4f8; border-color: #3498db;
            transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .doc-item.hidden {{ display: none; }}
        .doc-title {{ font-weight: bold; color: #2c3e50; margin-bottom: 8px; }}
        .doc-title a {{ color: #2c3e50; text-decoration: none; }}
        .doc-title a:hover {{ color: #3498db; text-decoration: underline; }}
        .doc-path {{ color: #7f8c8d; font-size: 0.9em; margin-bottom: 5px; }}
        .doc-description {{ color: #555; font-size: 0.9em; }}
        .stats {{ background: #e8f4f8; padding: 15px; border-radius: 6px; margin-bottom: 20px; text-align: center; }}
        .no-results {{ text-align: center; color: #7f8c8d; font-style: italic; padding: 40px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 Orbis Modellfabrik - Dokumentationsindex</h1>

        <div class="stats">
            <strong>{len(md_files)} Dokumente</strong> verfügbar |
            <strong>Volltext-Suche</strong> aktiviert |
            <strong>Kategorisiert</strong> nach Themen
        </div>

        <div class="search-container">
            <input type="text" id="search"
                   placeholder="🔍 Suche in allen Dokumenten... (z.B. 'MQTT', 'Dashboard', 'Node-RED')">
        </div>
"""

    # Gruppiere nach Kategorien
    categories = {}
    for file_info in md_files:
        category = file_info["category"]
        if category not in categories:
            categories[category] = []
        categories[category].append(file_info)

    # Generiere HTML für jede Kategorie
    for category, files in categories.items():
        html_content += f"""
        <div class="category">
            <h2>📋 {category}</h2>
            <div class="doc-list">
"""

        for file_info in files:
            keywords = " ".join(generate_keywords(file_info))
            title = file_info["name"].replace("-", " ").replace("_", " ").title()
            path = file_info["path"]

            html_content += f"""
                <div class="doc-item" data-keywords="{keywords}">
                    <div class="doc-title"><a href="{path}" target="_blank">{title}</a></div>
                    <div class="doc-path">{path}</div>
                    <div class="doc-description">Dokumentation: {title}</div>
                </div>
"""

        html_content += """
            </div>
        </div>
"""

    html_content += """
        <div class="no-results" id="no-results" style="display: none;">
            Keine Dokumente gefunden. Versuche andere Suchbegriffe.
        </div>
    </div>

    <script>
        const searchInput = document.getElementById('search');
        const docItems = document.querySelectorAll('.doc-item');
        const noResults = document.getElementById('no-results');

        function search() {
            const query = searchInput.value.toLowerCase().trim();
            let visibleCount = 0;

            docItems.forEach(item => {
                const keywords = item.getAttribute('data-keywords').toLowerCase();
                const title = item.querySelector('.doc-title').textContent.toLowerCase();
                const path = item.querySelector('.doc-path').textContent.toLowerCase();
                const description = item.querySelector('.doc-description').textContent.toLowerCase();

                const matches = keywords.includes(query) ||
                              title.includes(query) ||
                              path.includes(query) ||
                              description.includes(query);

                if (matches || query === '') {
                    item.classList.remove('hidden');
                    visibleCount++;
                } else {
                    item.classList.add('hidden');
                }
            });

            if (visibleCount === 0 && query !== '') {
                noResults.style.display = 'block';
            } else {
                noResults.style.display = 'none';
            }
        }

        searchInput.addEventListener('input', search);
        search();
    </script>
</body>
</html>
"""

    return html_content


def generate_json_index(md_files):
    """Generiere INDEX.json."""
    categories = {}
    for file_info in md_files:
        category = file_info["category"]
        if category not in categories:
            categories[category] = []

        keywords = generate_keywords(file_info)
        title = file_info["name"].replace("-", " ").replace("_", " ").title()

        categories[category].append(
            {"title": title, "path": file_info["path"], "keywords": keywords, "description": f"Dokumentation: {title}"}
        )

    return {
        "metadata": {
            "title": "Orbis Modellfabrik - Dokumentationsindex",
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "total_documents": len(md_files),
            "description": "Maschinenlesbarer Index aller Dokumentation im docs_orbis Verzeichnis",
        },
        "categories": categories,
        "search_index": {
            "all_keywords": list({kw for file_info in md_files for kw in generate_keywords(file_info)}),
            "file_paths": [file_info["path"] for file_info in md_files],
        },
    }


def main():
    """Hauptfunktion."""
    print("🔍 Suche Markdown-Dateien...")
    md_files = find_markdown_files()
    print(f"✅ {len(md_files)} Dokumente gefunden")

    print("📝 Generiere INDEX.html...")
    html_content = generate_html_index(md_files)
    with open("docs_orbis/INDEX.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("✅ INDEX.html erstellt")

    print("📝 Generiere INDEX.json...")
    json_content = generate_json_index(md_files)
    with open("docs_orbis/INDEX.json", "w", encoding="utf-8") as f:
        json.dump(json_content, f, indent=2, ensure_ascii=False)
    print("✅ INDEX.json erstellt")

    print("\n🎉 Index erfolgreich generiert!")
    print(f"   📄 INDEX.html: {len(html_content)} Zeichen")
    print(f"   📄 INDEX.json: {len(json.dumps(json_content))} Zeichen")
    print(f"   📚 {len(md_files)} Dokumente indiziert")


if __name__ == "__main__":
    main()
