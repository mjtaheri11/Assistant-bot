import json
import logging
import os

from .config import config

_BO_DIR = config.get("bo_config_dir", {}).get("path", "/app/src")
_BO_FILENAME = "business-objects.json"


def load_bo(filename: str) -> dict | None:
    """Load a business-object file, or None if it has nothing to serve.

    "Nothing to serve" covers a missing file, a zero-byte file, a literal
    `{}` or `null`, and a document whose `boNames` is empty. All collapse to
    None — the same sentinel the session path uses for "no BO supplied" — so
    callers have exactly one absent case to handle.

    Malformed JSON is NOT absent. It is a deployment error and raises, because
    silently degrading to "no BO" would hide a typo'd config for weeks.

    There is deliberately no fallback to a secondary file. This loader reads
    one path and one path only; if it is empty, the system has no default BO.
    """
    path = os.path.join(_BO_DIR, filename)

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read().strip()
    except FileNotFoundError:
        logging.warning("[bo_loader] %s not found; running with no default BO", path)
        return None

    if not raw:
        logging.warning("[bo_loader] %s is empty; running with no default BO", path)
        return None

    data = json.loads(raw)  # malformed JSON is a real error — let it propagate

    if not isinstance(data, dict) or not data.get("boNames"):
        logging.warning(
            "[bo_loader] %s contains no business objects; running with no default BO", path
        )
        return None

    return data


ALL_BOS_RAW = load_bo(_BO_FILENAME)