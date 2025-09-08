import os
from typing import Dict, List

import yaml


def load_sequence_recipe(recipe_name: str) -> List[Dict]:
    path = os.path.join(os.path.dirname(__file__), "recipes.yml")
    with open(os.path.abspath(path)) as f:
        data = yaml.safe_load(f)
    return data[recipe_name]


def get_recipe_names() -> list:
    path = os.path.join(os.path.dirname(__file__), "recipes.yml")
    with open(os.path.abspath(path)) as f:
        data = yaml.safe_load(f)
    return list(data.keys())
