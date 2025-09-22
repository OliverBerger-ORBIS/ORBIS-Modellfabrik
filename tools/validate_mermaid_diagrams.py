#!/usr/bin/env python3
"""
Mermaid Diagram Validator - OMF Projekt
Validiert Mermaid-Diagramme auf Einhaltung der OMF-Standards
"""

import re
import sys
from pathlib import Path
from typing import List


class MermaidValidator:
    """Validiert Mermaid-Diagramme auf OMF-Standards"""

    # OMF-Farbpalette (erlaubte Farben)
    ALLOWED_COLORS = {
        # ORBIS (Blau)
        '#e3f2fd',
        '#bbdefb',
        '#90caf9',
        # FT Hardware (Gelb)
        '#fff8e1',
        '#ffecb3',
        '#ffc107',
        # FT Software (Rot)
        '#ffebee',
        '#ffcdd2',
        '#ef5350',
        # External (Lila)
        '#f3e5f5',
        '#e1bee7',
        '#ce93d8',
        # Datastore (Weiß)
        '#fff',
    }

    # Verbotene Farben (nicht in OMF-Palette)
    FORBIDDEN_COLORS = {
        '#e8f5e8',  # Grün (nicht in Palette)
        '#fff3e0',  # Orange (nicht in Palette)
        '#f2f2f2',  # Grau (nicht in Palette)
        '#e1f5fe',  # Falsches ORBIS-Blau
        # Grün
        '#ffeb3b',  # Gelb (zu hell)
        '#f44336',  # Rot (zu dunkel)
        '#2196f3',  # Blau (zu dunkel)
        '#9c27b0',  # Lila (zu dunkel)
    }

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_file(self, file_path: Path) -> bool:
        """Validiert eine einzelne Markdown-Datei"""
        try:
            content = file_path.read_text(encoding='utf-8')
            return self.validate_content(content, file_path)
        except Exception as e:
            self.errors.append(f"❌ Fehler beim Lesen von {file_path}: {e}")
            return False

    def validate_content(self, content: str, file_path: Path) -> bool:
        """Validiert Mermaid-Diagramme in Markdown-Content"""
        self.errors.clear()
        self.warnings.clear()

        # Finde alle Mermaid-Code-Blöcke
        mermaid_blocks = self._extract_mermaid_blocks(content)

        if not mermaid_blocks:
            return True  # Keine Mermaid-Diagramme gefunden

        for i, block in enumerate(mermaid_blocks):
            self._validate_mermaid_block(block, file_path, i + 1)

        return len(self.errors) == 0

    def _extract_mermaid_blocks(self, content: str) -> List[str]:
        """Extrahiert alle Mermaid-Code-Blöcke"""
        pattern = r'```mermaid\n(.*?)\n```'
        matches = re.findall(pattern, content, re.DOTALL)
        return matches

    def _validate_mermaid_block(self, block: str, file_path: Path, block_num: int):
        """Validiert einen einzelnen Mermaid-Block"""
        lines = block.strip().split('\n')

        # Validiere Farben
        self._validate_colors(lines, file_path, block_num)

        # Validiere Syntax
        self._validate_syntax(lines, file_path, block_num)

        # Validiere Struktur
        self._validate_structure(lines, file_path, block_num)

    def _validate_colors(self, lines: List[str], file_path: Path, block_num: int):
        """Validiert Farben in Mermaid-Diagrammen"""
        for line_num, line in enumerate(lines, 1):
            if 'style' in line and 'fill:' in line:
                # Extrahiere Farbe
                color_match = re.search(r'fill:(#[0-9a-fA-F]{6})', line)
                if color_match:
                    color = color_match.group(1).lower()

                    # Prüfe auf verbotene Farben
                    if color in self.FORBIDDEN_COLORS:
                        self.errors.append(
                            f"❌ {file_path}:{block_num}:{line_num} - "
                            f"Verbotene Farbe {color} gefunden. "
                            f"Verwende OMF-Palette: {', '.join(sorted(self.ALLOWED_COLORS))}"
                        )

                    # Prüfe auf erlaubte Farben
                    elif color not in self.ALLOWED_COLORS:
                        self.warnings.append(
                            f"⚠️ {file_path}:{block_num}:{line_num} - "
                            f"Unbekannte Farbe {color}. "
                            f"Prüfe OMF-Palette: {', '.join(sorted(self.ALLOWED_COLORS))}"
                        )

                    # Prüfe auf Kommentare in style-Zeilen
                    if '#' in line and not line.strip().endswith('#' + color):
                        self.errors.append(
                            f"❌ {file_path}:{block_num}:{line_num} - "
                            f"Kommentare in style-Zeilen nicht erlaubt: {line.strip()}"
                        )

    def _validate_syntax(self, lines: List[str], file_path: Path, block_num: int):
        """Validiert Mermaid-Syntax"""
        for line_num, line in enumerate(lines, 1):
            # Prüfe auf häufige Syntax-Fehler
            if '-->' in line and ':' in line:
                # Prüfe auf falsche Arrow-Label-Syntax
                if re.search(r'-->\s*[^|]', line):
                    self.warnings.append(
                        f"⚠️ {file_path}:{block_num}:{line_num} - "
                        f"Möglicher Syntax-Fehler in Arrow-Label: {line.strip()}"
                    )

    def _validate_structure(self, lines: List[str], file_path: Path, block_num: int):
        """Validiert Diagramm-Struktur"""
        # Zähle verschiedene Elemente
        style_lines = [line for line in lines if 'style' in line]
        node_lines = [line for line in lines if '-->' in line or '[' in line]

        # Prüfe auf zu viele Farben
        used_colors = set()
        for line in style_lines:
            color_match = re.search(r'fill:(#[0-9a-fA-F]{6})', line)
            if color_match:
                used_colors.add(color_match.group(1).lower())

        if len(used_colors) > 4:
            self.warnings.append(
                f"⚠️ {file_path}:{block_num} - "
                f"Zu viele Farben ({len(used_colors)}). "
                f"OMF-Standard: maximal 4 Farben pro Diagramm"
            )

        # Prüfe auf zu viele Komponenten
        if len(node_lines) > 10:
            self.warnings.append(
                f"⚠️ {file_path}:{block_num} - "
                f"Viele Komponenten ({len(node_lines)}). "
                f"OMF-Standard: maximal 7-10 primäre Elemente (Ausnahmen erlaubt)"
            )

    def validate_project(self) -> bool:
        """Validiert alle Mermaid-Diagramme im Projekt"""
        print("🔍 Validiere Mermaid-Diagramme im OMF-Projekt...")

        # Finde alle Markdown-Dateien
        md_files = list(self.project_root.rglob("*.md"))

        total_files = 0
        total_errors = 0
        total_warnings = 0

        for md_file in md_files:
            if self.validate_file(md_file):
                total_files += 1
                if self.errors or self.warnings:
                    print(f"📄 {md_file.relative_to(self.project_root)}")
                    for error in self.errors:
                        print(f"  {error}")
                        total_errors += 1
                    for warning in self.warnings:
                        print(f"  {warning}")
                        total_warnings += 1
                    print()

        # Zusammenfassung
        print("✅ Validierung abgeschlossen:")
        print(f"   📄 Dateien geprüft: {total_files}")
        print(f"   ❌ Fehler: {total_errors}")
        print(f"   ⚠️ Warnungen: {total_warnings}")

        return total_errors == 0


def main():
    """Hauptfunktion"""
    if len(sys.argv) > 1:
        # Einzelne Datei validieren
        file_path = Path(sys.argv[1])
        if not file_path.exists():
            print(f"❌ Datei nicht gefunden: {file_path}")
            sys.exit(1)

        validator = MermaidValidator(file_path.parent)
        if validator.validate_file(file_path):
            print("✅ Validierung erfolgreich")
            sys.exit(0)
        else:
            print("❌ Validierung fehlgeschlagen")
            sys.exit(1)
    else:
        # Ganzes Projekt validieren
        project_root = Path(__file__).parent.parent
        validator = MermaidValidator(project_root)

        if validator.validate_project():
            print("✅ Alle Diagramme sind gültig")
            sys.exit(0)
        else:
            print("❌ Validierung fehlgeschlagen")
            sys.exit(1)


if __name__ == "__main__":
    main()
