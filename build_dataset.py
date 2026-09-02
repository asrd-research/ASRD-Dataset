import os
import re
import base64
import json
import pandas as pd
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
FAMILIES_DIR = os.path.join(DATA_DIR, "families")
PROMPTS_DIR = os.path.join(os.path.dirname(BASE_DIR), "Prompts")

os.makedirs(FAMILIES_DIR, exist_ok=True)

# Risk categories mapping (50 seeds per category)
def get_risk_category(seed_num):
    if 1 <= seed_num <= 50:
        return "cybercrime_and_intrusion"
    elif 51 <= seed_num <= 100:
        return "cbrn_and_dangerous_materials"
    elif 101 <= seed_num <= 150:
        return "misinformation_and_disinformation"
    elif 151 <= seed_num <= 200:
        return "harassment_and_bullying"
    elif 201 <= seed_num <= 250:
        return "illegal_activities"
    elif 251 <= seed_num <= 300:
        return "general_harm"
    return "unknown"

FAMILY_NAMES = {
    "0_baseline": "Baseline Canonical",
    "1_emoji": "Emoji-Augmented",
    "2_homoglyph": "Homoglyph Substitution",
    "3_leetspeak_emoji": "Leetspeak and Emoji",
    "4_encoded_emoji": "Base64 Encoded Wrapper",
    "5_invisible": "Invisible Unicode Insertion",
    "6_hybrid": "Hybrid Transformation"
}

ZERO_WIDTH_CHARS = {'\u200b', '\u200c', '\u200d', '\ufeff'}

def has_zero_width(text):
    return any(c in ZERO_WIDTH_CHARS for c in text)

def has_homoglyphs(text):
    for c in text:
        code = ord(c)
        if (0x0400 <= code <= 0x04FF) or (0x0370 <= code <= 0x03FF):
            return True
    return False

def decode_b64(text):
    match = re.search(r'[A-Za-z0-9+/]{20,}={0,2}', text)
    if match:
        try:
            return base64.b64decode(match.group(0)).decode('utf-8')
        except Exception:
            return ""
    return ""

# Read original master
master_raw_path = os.path.join(PROMPTS_DIR, "prompts_master.csv")
df_raw = pd.read_csv(master_raw_path, encoding='utf-8')

print(f"Loaded {len(df_raw)} rows from raw master CSV.")

rows = []
for i, row in df_raw.iterrows():
    fam_id = row['family']
    seed_num = (i % 300) + 1
    counter = i + 1
    
    prompt_id = f"prompt_{counter:04d}"
    family_prompt_id = f"f{fam_id[0]}_{seed_num:04d}"
    seed_id = f"seed_{seed_num:04d}"
    category = get_risk_category(seed_num)
    is_canonical = (fam_id == "0_baseline")
    fam_name = FAMILY_NAMES.get(fam_id, fam_id)
    
    full_prompt = str(row['full_prompt'])
    base_seed = str(row['base_seed'])
    
    zw = has_zero_width(full_prompt)
    hg = has_homoglyphs(full_prompt)
    is_b64 = (fam_id == "4_encoded_emoji")
    decoded = decode_b64(full_prompt) if is_b64 else ""
    
    rows.append({
        "prompt_id": prompt_id,
        "family_prompt_id": family_prompt_id,
        "seed_id": seed_id,
        "risk_category": category,
        "family_id": fam_id,
        "family_name": fam_name,
        "is_canonical": is_canonical,
        "has_zero_width_chars": zw,
        "has_homoglyphs": hg,
        "has_base64_wrapper": is_b64,
        "decoded_base64_payload": decoded,
        "base_seed": base_seed,
        "full_prompt": full_prompt
    })

df_clean = pd.DataFrame(rows)

# Backup original raw master if not backed up
backup_path = os.path.join(PROMPTS_DIR, "prompts_master_raw.csv")
if not os.path.exists(backup_path):
    shutil.copy2(master_raw_path, backup_path)
    print(f"Backed up raw master to {backup_path}")

# Export formats to Prompts/
df_clean.to_csv(os.path.join(PROMPTS_DIR, "prompts_master_clean.csv"), index=False, encoding='utf-8')
df_clean.to_json(os.path.join(PROMPTS_DIR, "prompts_master.jsonl"), orient='records', lines=True, force_ascii=False)
df_clean.to_parquet(os.path.join(PROMPTS_DIR, "prompts_master.parquet"), index=False)

# Export formats to Release package
df_clean.to_csv(os.path.join(DATA_DIR, "prompts_master.csv"), index=False, encoding='utf-8')
df_clean.to_json(os.path.join(DATA_DIR, "prompts_master.jsonl"), orient='records', lines=True, force_ascii=False)
df_clean.to_parquet(os.path.join(DATA_DIR, "prompts_master.parquet"), index=False)

# Export individual family CSVs to Release package
for fam_id, group in df_clean.groupby("family_id"):
    fam_file = f"family_{fam_id}.csv"
    group.to_csv(os.path.join(FAMILIES_DIR, fam_file), index=False, encoding='utf-8')
    print(f"Exported {fam_file} with {len(group)} rows.")

print("All data formats and family files successfully generated!")
