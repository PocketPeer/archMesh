import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Optional

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "..", "..", "logs")
LOG_DIR = os.path.abspath(LOG_DIR)
LOG_PATH = os.path.join(LOG_DIR, "llm_interactions.jsonl")


def _ensure_log_dir() -> None:
    os.makedirs(LOG_DIR, exist_ok=True)


def log_interaction(entry: Dict[str, Any]) -> None:
    _ensure_log_dir()
    entry_with_ts = {
        **entry,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry_with_ts, ensure_ascii=False) + "\n")


def read_interactions(
    *,
    stage: Optional[str] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    limit: int = 200,
) -> Iterable[Dict[str, Any]]:
    if not os.path.exists(LOG_PATH):
        return []

    results = []
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
            except Exception:
                continue
            if stage and data.get("stage") != stage:
                continue
            if provider and data.get("provider") != provider:
                continue
            if model and data.get("model") != model:
                continue
            results.append(data)
    # newest first
    results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return results[: max(1, min(limit, 1000))]


