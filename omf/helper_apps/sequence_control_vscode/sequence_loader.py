import os
from typing import Any, Dict, List

import yaml

from omf.tools.logging_config import get_logger

logger = get_logger("omf.helper_apps.sequence_control_vscode.sequence_loader")


class SequenceLoader:
    """Lädt und parst Sequenz-Definitionen aus YML-Dateien."""

    def __init__(self, recipes_dir: str):
        self.recipes_dir = recipes_dir

    def load_sequence(self, name: str) -> Dict[str, Any]:
        path = os.path.join(self.recipes_dir, f"{name}.yml")
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def list_sequences(self) -> List[str]:
        return [f[:-4] for f in os.listdir(self.recipes_dir) if f.endswith(".yml")]


# Beispiel-Nutzung:
# loader = SequenceLoader("omf/sequence_control/recipes")
# seq = loader.load_sequence("mill_sequence")
# logger.debug(seq)
