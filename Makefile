.PHONY: help validate-registry validate-mapping check-mapping-collisions check-templates-no-topics render-template validate-development-rules validate-observations nodered-backup-ssh nodered-restore-ssh nodered-backup-api nodered-restore-api nodered-status nodered-logs

PY?=python3

help:
	@echo "Targets:"
	@echo "  make validate-registry            # validate modules/enums/workpieces/topics/mapping against schemas"
	@echo "  make validate-mapping             # validate mapping.yml against schema"
	@echo "  make check-mapping-collisions     # ensure no topic matches multiple entries"
	@echo "  make check-templates-no-topics    # ensure templates don't contain topic strings"
	@echo "  make render-template TOPIC=...    # resolve a topic to template + vars (dry-run)"
	@echo "  make validate-development-rules   # validate OMF Development Rules compliance"
	@echo "  make validate-observations        # validate observations against schema"
	@echo ""
	@echo "Node-RED Integration:"
	@echo "  make nodered-backup-ssh           # backup Node-RED via SSH (NR_HOST=pi@192.168.0.100)"
	@echo "  make nodered-restore-ssh          # restore Node-RED via SSH (NR_HOST=... SRC=...)"
	@echo "  make nodered-backup-api           # backup Node-RED via Admin API (NR_BASE=... TOKEN=...)"
	@echo "  make nodered-restore-api          # restore Node-RED via Admin API (NR_BASE=... FILE=... TOKEN=...)"
	@echo "  make nodered-status               # check Node-RED service status"
	@echo "  make nodered-logs                 # show Node-RED logs"

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

validate-observations:
	$(PY) tools/validate_observations.py

# Node-RED Integration Targets
NR_HOST ?= ff22@192.168.0.100
NR_BASE ?= http://192.168.0.100:1880
NR_SSH_KEY ?= ~/.ssh/nodered_key

nodered-backup-ssh:
	HOST=$(NR_HOST) SSH_KEY=$(NR_SSH_KEY) ./integrations/node_red/scripts/nodered_backup_ssh.sh

nodered-restore-ssh:
	@if [ -z "$(SRC)" ]; then echo "Usage: make nodered-restore-ssh SRC=integrations/node_red/backups/20250915T090000Z"; exit 1; fi
	HOST=$(NR_HOST) SRC=$(SRC) SSH_KEY=$(NR_SSH_KEY) ./integrations/node_red/scripts/nodered_restore_ssh.sh

nodered-backup-api:
	BASE=$(NR_BASE) TOKEN=$(TOKEN) ./integrations/node_red/scripts/nodered_backup_adminapi.sh

nodered-restore-api:
	@if [ -z "$(FILE)" ]; then echo "Usage: make nodered-restore-api FILE=integrations/node_red/backups/20250915T090000Z/flows.json"; exit 1; fi
	BASE=$(NR_BASE) FILE=$(FILE) TOKEN=$(TOKEN) ./integrations/node_red/scripts/nodered_restore_adminapi.sh

nodered-status:
	ssh -i $(NR_SSH_KEY) $(NR_HOST) "systemctl --user status nodered"

nodered-logs:
	ssh -i $(NR_SSH_KEY) $(NR_HOST) "journalctl --user -u nodered -f"

validate-development-rules:
	$(PY) src_orbis/scripts/validate_development_rules.py
