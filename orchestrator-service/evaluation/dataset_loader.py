import json
from typing import List, Dict, Any


def load_dataset(path: str) -> List[Dict[str, Any]]:
    with open(path, "r") as f:
        return json.load(f)