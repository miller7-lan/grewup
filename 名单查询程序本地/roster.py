import json
import os
import re


DEFAULT_ROSTER = {"group_party": [], "group_a": [], "group_b": []}
DEFAULT_CLASS_NAME = "当前班级"


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


def empty_roster():
    return {key: [] for key in DEFAULT_ROSTER}


def load_roster(data_file="class_roster.json"):
    book = load_roster_book(data_file)
    return get_class_roster(book, book["active_class"])


def load_roster_book(data_file="class_roster.json"):
    if not os.path.exists(data_file):
        return {
            "active_class": DEFAULT_CLASS_NAME,
            "classes": {DEFAULT_CLASS_NAME: empty_roster()},
        }

    try:
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {
            "active_class": DEFAULT_CLASS_NAME,
            "classes": {DEFAULT_CLASS_NAME: empty_roster()},
        }

    if isinstance(data.get("classes"), dict):
        classes = {}
        for name, roster in data["classes"].items():
            clean_name = str(name or "").strip()
            if not clean_name or not isinstance(roster, dict):
                continue
            classes[clean_name] = clean_roster(
                roster.get("group_party", []),
                roster.get("group_a", []),
                roster.get("group_b", []),
            )

        if not classes:
            classes = {DEFAULT_CLASS_NAME: empty_roster()}

        active_class = str(data.get("active_class") or "").strip()
        if active_class not in classes:
            active_class = next(iter(classes))

        return {"active_class": active_class, "classes": classes}

    legacy_roster = clean_roster(
        data.get("group_party", []),
        data.get("group_a", []),
        data.get("group_b", []),
    )
    return {
        "active_class": DEFAULT_CLASS_NAME,
        "classes": {DEFAULT_CLASS_NAME: legacy_roster},
    }


def save_roster(group_party, group_a, group_b, data_file="class_roster.json"):
    return save_class_roster(DEFAULT_CLASS_NAME, group_party, group_a, group_b, data_file)


def save_roster_book(book, data_file="class_roster.json"):
    classes = book.get("classes", {})
    if not isinstance(classes, dict) or not classes:
        classes = {DEFAULT_CLASS_NAME: empty_roster()}

    cleaned_classes = {}
    for name, roster in classes.items():
        clean_name = str(name or "").strip()
        if not clean_name or not isinstance(roster, dict):
            continue
        cleaned_classes[clean_name] = clean_roster(
            roster.get("group_party", []),
            roster.get("group_a", []),
            roster.get("group_b", []),
        )

    if not cleaned_classes:
        cleaned_classes = {DEFAULT_CLASS_NAME: empty_roster()}

    active_class = str(book.get("active_class") or "").strip()
    if active_class not in cleaned_classes:
        active_class = next(iter(cleaned_classes))

    data = {"active_class": active_class, "classes": cleaned_classes}
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return data


def save_class_roster(class_name, group_party, group_a, group_b, data_file="class_roster.json"):
    book = load_roster_book(data_file)
    name = normalize_class_name(class_name)
    data = clean_roster(group_party, group_a, group_b)
    book["classes"][name] = data
    book["active_class"] = name
    save_roster_book(book, data_file)
    return data


def add_class_roster(class_name, data_file="class_roster.json"):
    book = load_roster_book(data_file)
    name = normalize_class_name(class_name)
    if name not in book["classes"]:
        book["classes"][name] = empty_roster()
    book["active_class"] = name
    return save_roster_book(book, data_file)


def delete_class_roster(class_name, data_file="class_roster.json"):
    book = load_roster_book(data_file)
    name = str(class_name or "").strip()
    if name in book["classes"] and len(book["classes"]) > 1:
        del book["classes"][name]
        if book["active_class"] == name:
            book["active_class"] = next(iter(book["classes"]))
    return save_roster_book(book, data_file)


def get_class_roster(book, class_name):
    classes = book.get("classes", {})
    if not classes:
        return empty_roster()
    name = str(class_name or "").strip()
    if name not in classes:
        name = book.get("active_class") or next(iter(classes))
    return clean_roster(
        classes.get(name, {}).get("group_party", []),
        classes.get(name, {}).get("group_a", []),
        classes.get(name, {}).get("group_b", []),
    )


def merge_class_rosters(book):
    merged = empty_roster()
    for roster in book.get("classes", {}).values():
        merged["group_party"].extend(roster.get("group_party", []))
        merged["group_a"].extend(roster.get("group_a", []))
        merged["group_b"].extend(roster.get("group_b", []))
    return clean_roster(merged["group_party"], merged["group_a"], merged["group_b"])


def normalize_class_name(value):
    name = re.sub(r"\s+", " ", str(value or "")).strip()
    return name or DEFAULT_CLASS_NAME


def target_names(roster, mode):
    if mode == "仅核查党员":
        return roster["group_party"]
    if mode == "仅核查团员":
        return roster["group_a"]
    return roster["group_party"] + roster["group_a"] + roster["group_b"]
