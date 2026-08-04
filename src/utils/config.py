from pathlib import Path
import yaml

def load_config(path: str | Path = "configs/config.yaml") -> dict:
    with Path(path).open(encoding="utf-8") as f:
        return yaml.safe_load(f)
