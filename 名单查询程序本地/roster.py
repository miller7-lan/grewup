import json
import os
import re


DEFAULT_ROSTER = {"group_party": [], "group_a": [], "group_b": []}


def normalize_name(value):
    """Keep only Chinese characters so noisy OCR names can still match."""
    return re.sub(r"[^\u4e00-\u9fa5]", "", str(value or "")).strip()


def clean_name_lines(text):
    names = []
    seen = set()
    for line in str(text or "").splitlines():
        name = normalize_name(line)
        if len(name) >= 2 and name not in seen:
            names.append(name)
            seen.add(name)
    return names


def clean_roster(group_party, group_a, group_b):
    """Deduplicate and resolve identity conflicts: party > member > other."""
    party = list(dict.fromkeys(normalize_name(n) for n in group_party if normalize_name(n)))
    party_set = set(party)

    raw_a = list(dict.fromkeys(normalize_name(n) for n in group_a if normalize_name(n)))
    members = [name for name in raw_a if name not in party_set]
    member_set = set(members)

    raw_b = list(dict.fromkeys(normalize_name(n) for n in group_b if normalize_name(n)))
    others = [name for name in raw_b if name not in party_set and name not in member_set]

    return {"group_party": party, "group_a": members, "group_b": others}


def load_roster(data_file="class_roster.json"):
    if not os.path.exists(data_file):
        return DEFAULT_ROSTER.copy()

    try:
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return DEFAULT_ROSTER.copy()

    return clean_roster(
        data.get("group_party", []),
        data.get("group_a", []),
        data.get("group_b", []),
    )


def save_roster(group_party, group_a, group_b, data_file="class_roster.json"):
    data = clean_roster(group_party, group_a, group_b)
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return data


def target_names(roster, mode):
    if mode == "仅核查党员":
        return roster["group_party"]
    if mode == "仅核查团员":
        return roster["group_a"]
    return roster["group_party"] + roster["group_a"] + roster["group_b"]
