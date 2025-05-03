import json
import os

def save_candidate_data(data):
    if os.path.exists('candidates.json'):
        with open('candidates.json', 'r', encoding='utf-8') as f:
            candidates = json.load(f)
    else:
        candidates = []
    candidates.append(data)
    with open('candidates.json', 'w', encoding='utf-8') as f:
        json.dump(candidates, f, ensure_ascii=False, indent=2)