import json
import os

DB_PATH = "data/patients_db.json"

def load_patient_by_name(name):
    with open(DB_PATH, "r") as f:
        patients = json.load(f)
    return next((p for p in patients if p["name"].lower() == name.lower()), None)

def update_patient_record(name, updates):
    with open(DB_PATH, "r") as f:
        patients = json.load(f)

    for p in patients:
        if p["name"].lower() == name.lower():
            p.update(updates)
            break

    with open(DB_PATH, "w") as f:
        json.dump(patients, f, indent=4)
