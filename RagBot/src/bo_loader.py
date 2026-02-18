import json
import os
import pathlib

from .config import config

# _BO_DIR = os.getenv("BO_CONFIG_DIR", "/app/src")
_BO_DIR = config.get("bo_config_dir", {}).get("path", "/app/src")
# _BO_DIR = "{path}/business-objects.json".format(path=pathlib.Path(__file__).parent.resolve())

def load_bo(filename: str) -> dict:
    path = os.path.join(_BO_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


try:
    ALL_BOS_RAW = load_bo("business-objects.json")
except FileNotFoundError:
    from .business_objects import ALL_BOS_RAW  # type: ignore
    import pdb
    pdb.set_trace()
    print("[bo_loader] business-objects.json not found, using business_objects.py")
