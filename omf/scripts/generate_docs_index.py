#!/usr/bin/env python3
"""
Dokumentationsindex-Generator für ORBIS-Modellfabrik

Erstellt einen durchsuchbaren Index aller Dokumentation mit:
- Volltext-Suche
- Kategorisierung
- Verlinkung
- Metadaten
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict


class DocumentationIndexer:
    """Erstellt und verwaltet den Dokumentationsindex"""

    def __init__(self, docs_root: str = "docs_orbis"):
        self.docs_root = Path(docs_root)
        self.index = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_documents": 0,
                "total_categories": 0,
                "searchable_content": 0,
            },
            "categories": {},
            "documents": {},
            "search_index": {},
        }

    def extract_metadata(self, file_path: Path) -> Dict:
        """Extrahiert Metadaten aus einer Markdown-Datei"""
        with open(file_path, encoding='utf-8') as f:
            content = f.read()

        # Titel extrahieren (erste # Zeile)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else file_path.stem

        # Beschreibung extrahieren (erste Zeile nach Titel)
        description = ""
        lines = content.split('\n')
        for line in lines[1:10]:  # Erste 10 Zeilen nach Titel
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('```'):
                description = line[:200] + "..." if len(line) > 200 else line
                break

        # Kategorien aus Pfad ableiten
        relative_path = file_path.relative_to(self.docs_root)
        category_parts = list(relative_path.parts[:-1])
        category = category_parts[0] if category_parts else "root"
        subcategory = "/".join(category_parts[1:]) if len(category_parts) > 1 else None

        # Keywords extrahieren
        keywords = []
        if "README" in file_path.name:
            keywords.append("overview")
        if "guide" in file_path.name.lower():
            keywords.append("guide")
        if "troubleshooting" in file_path.name.lower():
            keywords.append("troubleshooting")
        if "release" in file_path.name.lower():
            keywords.append("release")

        # Content für Suche vorbereiten
        searchable_content = re.sub(r'[#*`\[\]()]', ' ', content.lower())
        searchable_content = re.sub(r'\s+', ' ', searchable_content).strip()

        return {
            "title": title,
            "description": description,
            "category": category,
            "subcategory": subcategory,
            "keywords": keywords,
            "file_path": str(relative_path),
            "file_size": file_path.stat().st_size,
            "searchable_content": searchable_content[:1000],  # Erste 1000 Zeichen
            "word_count": len(searchable_content.split()),
        }

    def build_index(self):
        """Erstellt den vollständigen Dokumentationsindex"""
        print("🔍 Durchsuche Dokumentation...")

        for md_file in self.docs_root.rglob("*.md"):
            if md_file.is_file():
                try:
                    metadata = self.extract_metadata(md_file)
                    doc_id = str(md_file.relative_to(self.docs_root))

                    # Dokument zum Index hinzufügen
                    self.index["documents"][doc_id] = metadata

                    # Kategorie-Index aktualisieren
                    category = metadata["category"]
                    if category not in self.index["categories"]:
                        self.index["categories"][category] = {"name": category, "document_count": 0, "documents": []}

                    self.index["categories"][category]["documents"].append(doc_id)
                    self.index["categories"][category]["document_count"] += 1

                    # Suchindex aufbauen
                    search_terms = (
                        metadata["title"]
                        + " "
                        + metadata["description"]
                        + " "
                        + " ".join(metadata["keywords"])
                        + " "
                        + metadata["searchable_content"]
                    ).lower()

                    for term in search_terms.split():
                        term = re.sub(r'[^\w]', '', term)
                        if len(term) > 2:  # Nur Wörter mit mehr als 2 Zeichen
                            if term not in self.index["search_index"]:
                                self.index["search_index"][term] = []
                            if doc_id not in self.index["search_index"][term]:
                                self.index["search_index"][term].append(doc_id)

                    print(f"  ✅ {doc_id}")

                except Exception as e:
                    print(f"  ❌ Fehler bei {md_file}: {e}")

        # Metadaten aktualisieren
        self.index["metadata"]["total_documents"] = len(self.index["documents"])
        self.index["metadata"]["total_categories"] = len(self.index["categories"])
        self.index["metadata"]["searchable_content"] = len(self.index["search_index"])

        print("\n📊 Index erstellt:")
        print(f"   📄 Dokumente: {self.index['metadata']['total_documents']}")
        print(f"   📂 Kategorien: {self.index['metadata']['total_categories']}")
        print(f"   🔍 Suchbegriffe: {self.index['metadata']['searchable_content']}")

    def save_index(self, output_file: str = "docs_orbis/INDEX.json"):
        """Speichert den Index als JSON-Datei"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)
        print(f"💾 Index gespeichert: {output_file}")

    def generate_html_index(self, output_file: str = "docs_orbis/INDEX.html"):
        """Generiert eine HTML-Version des Index"""
        html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ORBIS-Modellfabrik - Dokumentationsindex</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            margin: 0; padding: 20px; background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px; margin: 0 auto; background: white;
            padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        .search-box {{ margin: 20px 0; padding: 15px; background: #ecf0f1; border-radius: 5px; }}
        .search-box input {{
            width: 100%; padding: 10px; border: 1px solid #bdc3c7;
            border-radius: 5px; font-size: 16px;
        }}
        .category {{ margin: 30px 0; }}
        .category h2 {{ color: #34495e; background: #ecf0f1; padding: 10px; border-radius: 5px; }}
        .documents {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px; margin-top: 15px;
        }}
        .document {{ background: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #3498db; }}
        .document h3 {{ margin: 0 0 10px 0; color: #2c3e50; }}
        .document p {{ margin: 5px 0; color: #7f8c8d; font-size: 14px; }}
        .document a {{ color: #3498db; text-decoration: none; }}
        .document a:hover {{ text-decoration: underline; }}
        .keywords {{ margin-top: 10px; }}
        .keyword {{
            display: inline-block; background: #e74c3c; color: white;
            padding: 2px 8px; border-radius: 12px; font-size: 12px; margin: 2px;
        }}
        .stats {{ background: #2ecc71; color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 ORBIS-Modellfabrik - Dokumentationsindex</h1>

        <div class="stats">
            <strong>📊 Statistiken:</strong>
            {self.index['metadata']['total_documents']} Dokumente in "
            f"{self.index['metadata']['total_categories']} Kategorien
            | Generiert am {datetime.now().strftime('%d.%m.%Y %H:%M')}
        </div>

        <div class="search-box">
            <input type="text" id="searchInput"
                   placeholder="🔍 Dokumentation durchsuchen..."
                   onkeyup="searchDocuments()">
        </div>

        <div id="categories">
"""

        # Kategorien und Dokumente hinzufügen
        for category_name, category_data in sorted(self.index["categories"].items()):
            html += f"""
            <div class="category">
                <h2>📂 {category_name} ({category_data['document_count']} Dokumente)</h2>
                <div class="documents">
"""

            for doc_id in sorted(category_data["documents"]):
                doc = self.index["documents"][doc_id]
                keywords_html = "".join([f'<span class="keyword">{kw}</span>' for kw in doc["keywords"]])

                html += f"""
                    <div class="document" data-searchable="{doc['searchable_content'].lower()}">
                        <h3><a href="{doc['file_path']}">{doc['title']}</a></h3>
                        <p>{doc['description']}</p>
                        <p><strong>📁 Pfad:</strong> {doc['file_path']}</p>
                        <p><strong>📊 Größe:</strong> {doc['file_size']:,} Bytes | "
                        f"<strong>Wörter:</strong> {doc['word_count']}</p>
                        <div class="keywords">{keywords_html}</div>
                    </div>
"""

            html += """
                </div>
            </div>
"""

        html += """
        </div>
    </div>

    <script>
        function searchDocuments() {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const documents = document.querySelectorAll('.document');

            documents.forEach(doc => {
                const searchableContent = doc.getAttribute('data-searchable');
                if (searchableContent.includes(searchTerm) || searchTerm === '') {
                    doc.style.display = 'block';
                } else {
                    doc.style.display = 'none';
                }
            });
        }
    </script>
</body>
</html>
"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"🌐 HTML-Index generiert: {output_file}")


def main():
    """Hauptfunktion"""
    print("🚀 ORBIS-Modellfabrik - Dokumentationsindex-Generator")
    print("=" * 60)

    indexer = DocumentationIndexer()
    indexer.build_index()
    indexer.save_index()
    indexer.generate_html_index()

    print("\n✅ Dokumentationsindex erfolgreich erstellt!")
    print("\n📖 Verwendung:")
    print("   • JSON-Index: docs_orbis/INDEX.json")
    print("   • HTML-Index: docs_orbis/INDEX.html")
    print("   • Öffne INDEX.html im Browser für interaktive Suche")


if __name__ == "__main__":
    main()
