from pathlib import Path
from typing import Dict, List

import yaml

def load_sequence_recipe(recipe_name: str) -> List[Dict]:
    path = str(Path(__file__).parent / "recipes.yml")
    with open(os.path.abspath(path)) as f:
        data = yaml.safe_load(f)
    return data[recipe_name]

def get_recipe_names() -> list:
    path = str(Path(__file__).parent / "recipes.yml")
    with open(os.path.abspath(path)) as f:
        data = yaml.safe_load(f)
    return list(data.keys())
