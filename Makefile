# ORBIS Modellfabrik - Makefile

.PHONY: help validate-structure fix-structure test format lint clean install docs-index

help: ## Zeige verfügbare Befehle
	@echo "ORBIS Modellfabrik - Verfügbare Befehle:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

validate-structure: ## Validiere Projekt-Struktur
	@echo "🔍 Validiere Projekt-Struktur..."
	@python src_orbis/scripts/validate_project_structure.py

fix-structure: ## Versuche automatische Struktur-Korrektur
	@echo "🔧 Versuche automatische Struktur-Korrektur..."
	@python src_orbis/scripts/validate_project_structure.py --fix

test: ## Führe Tests aus
	@echo "🧪 Führe Tests aus..."
	@python -m pytest tests_orbis/ -v

test-helper: ## Führe nur Helper-App Tests aus
	@echo "🧪 Führe Helper-App Tests aus..."
	@python -m pytest tests_orbis/test_helper_apps/ -v

format: ## Formatiere Code mit Black
	@echo "🎨 Formatiere Code..."
	@black src_orbis/ tests_orbis/

lint: ## Führe Linting mit Ruff aus
	@echo "🔍 Führe Linting aus..."
	@ruff check src_orbis/ tests_orbis/

clean: ## Bereinige temporäre Dateien
	@echo "🧹 Bereinige temporäre Dateien..."
	@find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -r {} + 2>/dev/null || true

install: ## Installiere Dependencies
	@echo "📦 Installiere Dependencies..."
	@pip install -r requirements.txt

docs-index: ## Generiere Dokumentationsindex
	@echo "📚 Generiere Dokumentationsindex..."
	@python src_orbis/scripts/generate_docs_index.py

pre-commit: ## Installiere Pre-commit Hooks
	@echo "🪝 Installiere Pre-commit Hooks..."
	@pre-commit install

session-manager: ## Starte Session Manager
	@echo "🚀 Starte Session Manager..."
	@streamlit run src_orbis/helper_apps/session_manager/session_manager.py --server.port=8507

all-checks: validate-structure lint test ## Führe alle Checks aus
	@echo "✅ Alle Checks erfolgreich!"

# Branch-spezifische Test-Ausführung
test-by-branch: ## Führe Tests basierend auf Branch aus
	@echo "🌿 Führe branch-spezifische Tests aus..."
	@python run_tests_by_branch.py
