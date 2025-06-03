import json
import os
import time

DATA_FILE = "income_data.json"


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as fh:
            try:
                return json.load(fh)
            except json.JSONDecodeError:
                return {}
    return {}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def add_income_entry(category, amount, desc=""):
    data = load_data()
    entry = {"amount": amount, "desc": desc, "time": time.time()}
    data.setdefault(category, []).append(entry)
    save_data(data)


def summarize_totals():
    data = load_data()
    summary = {}
    for cat, entries in data.items():
        total = sum(e.get("amount", 0) for e in entries)
        summary[cat] = total
    return summary
