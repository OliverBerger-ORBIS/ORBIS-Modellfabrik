.PHONY: help nodered-backup-ssh nodered-restore-ssh nodered-backup-api nodered-restore-api nodered-status nodered-logs

PY?=python3

help:
	@echo "Targets:"
	@echo ""
	@echo "Node-RED Integration (APS-NodeRED):"
	@echo "  make nodered-backup-ssh           # backup Node-RED via SSH (NR_HOST=ff22@192.168.0.100)"
	@echo "  make nodered-restore-ssh          # restore Node-RED via SSH (NR_HOST=... SRC=...)"
	@echo "  make nodered-backup-api           # backup Node-RED via Admin API (NR_BASE=... TOKEN=...)"
	@echo "  make nodered-restore-api          # restore Node-RED via Admin API (NR_BASE=... FILE=... TOKEN=...)"
	@echo "  make nodered-status               # check Node-RED service status"
	@echo "  make nodered-logs                 # show Node-RED logs"
	@echo ""
	@echo "Veraltete Registry-Tools siehe tools/OBSOLETE_REGISTRY_README.md"

# Node-RED Integration Targets
NR_HOST ?= ff22@192.168.0.100
NR_BASE ?= http://192.168.0.100:1880
NR_SSH_KEY ?= ~/.ssh/nodered_key

nodered-backup-ssh:
	HOST=$(NR_HOST) SSH_KEY=$(NR_SSH_KEY) ./integrations/APS-NodeRED/scripts/nodered_backup_ssh.sh

nodered-restore-ssh:
	@if [ -z "$(SRC)" ]; then echo "Usage: make nodered-restore-ssh SRC=integrations/APS-NodeRED/backups/20250915T090000Z"; exit 1; fi
	HOST=$(NR_HOST) SRC=$(SRC) SSH_KEY=$(NR_SSH_KEY) ./integrations/APS-NodeRED/scripts/nodered_restore_ssh.sh

nodered-backup-api:
	BASE=$(NR_BASE) TOKEN=$(TOKEN) ./integrations/APS-NodeRED/scripts/nodered_backup_adminapi.sh

nodered-restore-api:
	@if [ -z "$(FILE)" ]; then echo "Usage: make nodered-restore-api FILE=integrations/APS-NodeRED/backups/20250915T090000Z/flows.json"; exit 1; fi
	BASE=$(NR_BASE) FILE=$(FILE) TOKEN=$(TOKEN) ./integrations/APS-NodeRED/scripts/nodered_restore_adminapi.sh

nodered-status:
	ssh -i $(NR_SSH_KEY) $(NR_HOST) "systemctl --user status nodered"

nodered-logs:
	ssh -i $(NR_SSH_KEY) $(NR_HOST) "journalctl --user -u nodered -f"
