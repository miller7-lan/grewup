import re
from dataclasses import dataclass

from roster import normalize_name


@dataclass(frozen=True)
class AttendanceResult:
    target: list
    done: list
    missing: list
    unknown: list
    total: int
    done_count: int
    missing_count: int
    percent: float
    reminder: str
    source: str


def extract_by_turbo_match(raw_text, target_list):
    clean_text = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9]", "", raw_text or "")
    return [name for name in target_list if name in (raw_text or "") or name in clean_text]


def build_attendance_result(target_list, extracted_names, source):
    target = list(dict.fromkeys(normalize_name(n) for n in target_list if normalize_name(n)))
    target_set = set(target)

    extracted = list(dict.fromkeys(normalize_name(n) for n in extracted_names if normalize_name(n)))
    done = sorted(name for name in extracted if name in target_set)
    missing = sorted(name for name in target if name not in set(done))
    unknown = sorted(name for name in extracted if name not in target_set)

    total = len(target)
    done_count = len(done)
    missing_count = len(missing)
    percent = (done_count / total * 100) if total else 0
    reminder = f"未完成提醒：@{' @'.join(missing)}" if missing else ""

    return AttendanceResult(
        target=target,
        done=done,
        missing=missing,
        unknown=unknown,
        total=total,
        done_count=done_count,
        missing_count=missing_count,
        percent=percent,
        reminder=reminder,
        source=source,
    )
