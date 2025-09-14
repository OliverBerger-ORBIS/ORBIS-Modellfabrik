.PHONY: help validate-registry validate-mapping check-mapping-collisions check-templates-no-topics render-template

PY?=python3

help:
	@echo "Targets:"
	@echo "  make validate-registry            # validate modules/enums/workpieces/topics/mapping against schemas"
	@echo "  make validate-mapping             # validate mapping.yml against schema"
	@echo "  make check-mapping-collisions     # ensure no topic matches multiple entries"
	@echo "  make check-templates-no-topics    # ensure templates don't contain topic strings"
	@echo "  make render-template TOPIC=...    # resolve a topic to template + vars (dry-run)"

validate-registry: validate-mapping
	$(PY) tools/validate_registry.py

validate-mapping:
	$(PY) tools/validate_mapping.py

check-mapping-collisions:
	$(PY) tools/check_mapping_collisions.py

check-templates-no-topics:
	$(PY) tools/check_templates_no_topics.py

render-template:
	@if [ -z "$(TOPIC)" ]; then echo "Usage: make render-template TOPIC=<mqtt/topic>"; exit 1; fi
	$(PY) tools/render_template.py --topic "$(TOPIC)"
