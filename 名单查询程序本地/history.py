import json
import os
from datetime import datetime


HISTORY_FILE = "attendance_history.json"


def load_history(history_file=HISTORY_FILE):
    if not os.path.exists(history_file):
        return []
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return []
    return data if isinstance(data, list) else []


def save_history_item(mode, result, history_file=HISTORY_FILE):
    history = load_history(history_file)
    item = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mode": mode,
        "source": result.source,
        "total": result.total,
        "done_count": result.done_count,
        "missing_count": result.missing_count,
        "percent": round(result.percent, 1),
        "done": result.done,
        "missing": result.missing,
        "unknown": result.unknown,
        "corrections": result.corrections,
        "reminder": result.reminder,
    }
    history.insert(0, item)
    history = history[:30]
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)
    return item


def clear_history(history_file=HISTORY_FILE):
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=4)
