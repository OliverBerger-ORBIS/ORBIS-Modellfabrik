#!/bin/bash
# OMF Modellfabrik - Development Setup Script
# Automatisches Setup für neue Entwickler

set -e

echo "🚀 OMF Modellfabrik - Development Setup"
echo "======================================"

# 1. Virtual Environment aktivieren
echo "📦 Aktiviere Virtual Environment..."
source .venv/bin/activate

# 2. Paket im editable mode installieren
echo "🔧 Installiere OMF Paket im editable mode..."
pip install -e .

# 3. Pre-commit Hooks installieren
echo "🪝 Installiere Pre-commit Hooks..."
pre-commit install

# 4. Tests ausführen
echo "🧪 Führe Tests aus..."
python -m pytest tests/ -v --tb=short

echo ""
echo "✅ Setup abgeschlossen!"
echo ""
echo "📋 Nächste Schritte:"
echo "  • Dashboard starten: streamlit run omf/dashboard/omf_dashboard.py"
echo "  • Session Manager: streamlit run omf/helper_apps/session_manager/session_manager.py"
echo "  • Tests ausführen: python -m pytest tests/"
echo ""
echo "🎉 Viel Erfolg mit der OMF Modellfabrik!"
