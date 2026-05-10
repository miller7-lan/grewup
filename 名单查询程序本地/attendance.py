import re
from dataclasses import dataclass
from difflib import SequenceMatcher

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
    corrections: list


def extract_by_turbo_match(raw_text, target_list):
    clean_text = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9]", "", raw_text or "")
    matched = [name for name in target_list if name in (raw_text or "") or name in clean_text]
    fuzzy_names, corrections = extract_by_fuzzy_name_match(clean_text, target_list, matched)
    return list(dict.fromkeys(matched + fuzzy_names)), corrections


def extract_by_fuzzy_name_match(clean_text, target_list, already_matched=None):
    already_matched = set(already_matched or [])
    chinese_text = re.sub(r"[^\u4e00-\u9fa5]", "", clean_text or "")
    corrections = []
    fuzzy_names = []

    for target in target_list:
        target = normalize_name(target)
        if not target or target in already_matched:
            continue

        best_candidate = ""
        best_score = 0
        min_len = len(target)
        max_len = min(len(target) + 1, 5)
        for size in range(min_len, max_len + 1):
            if len(chinese_text) < size:
                continue
            for start in range(0, len(chinese_text) - size + 1):
                candidate = chinese_text[start:start + size]
                if candidate[0] != target[0]:
                    continue
                score = name_similarity(target, candidate)
                if score > best_score:
                    best_score = score
                    best_candidate = candidate

        threshold = 0.66 if len(target) == 3 else 0.74
        if best_candidate and best_candidate != target and best_score >= threshold:
            fuzzy_names.append(target)
            corrections.append({
                "raw": best_candidate,
                "name": target,
                "score": round(best_score, 2),
            })

    return fuzzy_names, corrections


def name_similarity(target, candidate):
    sequence_score = SequenceMatcher(None, target, candidate).ratio()
    same_position = sum(1 for a, b in zip(target, candidate) if a == b)
    position_score = same_position / max(len(target), len(candidate))
    return max(sequence_score, position_score)


def build_attendance_result(target_list, extracted_names, source, corrections=None):
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
        corrections=corrections or [],
    )
