"""
Adversarial Surface-Form Robustness Dataset (ASRD) - Dataset Loader
Anonymous Submission - NeurIPS 2026 Workshop
"""

import os
import csv
import json
from typing import List, Dict, Any, Optional

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
MASTER_CSV = os.path.join(DATA_DIR, "prompts_master.csv")
MASTER_JSONL = os.path.join(DATA_DIR, "prompts_master.jsonl")
MASTER_PARQUET = os.path.join(DATA_DIR, "prompts_master.parquet")


def load_dataset_pandas(format_type: str = "auto"):
    """
    Load dataset as a pandas DataFrame.
    format_type: 'auto', 'parquet', 'jsonl', or 'csv'
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("pandas is required for load_dataset_pandas. Run `pip install pandas pyarrow` or use load_dataset_records().")

    if format_type == "auto":
        if os.path.exists(MASTER_PARQUET):
            return pd.read_parquet(MASTER_PARQUET)
        elif os.path.exists(MASTER_JSONL):
            return pd.read_json(MASTER_JSONL, orient="records", lines=True)
        else:
            return pd.read_csv(MASTER_CSV, encoding="utf-8")
    elif format_type == "parquet":
        return pd.read_parquet(MASTER_PARQUET)
    elif format_type == "jsonl":
        return pd.read_json(MASTER_JSONL, orient="records", lines=True)
    elif format_type == "csv":
        return pd.read_csv(MASTER_CSV, encoding="utf-8")
    else:
        raise ValueError(f"Unknown format_type: {format_type}")


def load_dataset_records() -> List[Dict[str, Any]]:
    """
    Zero-dependency loader returning list of prompt records.
    Uses built-in json and standard libraries.
    """
    if os.path.exists(MASTER_JSONL):
        records = []
        with open(MASTER_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
        return records
    elif os.path.exists(MASTER_CSV):
        records = []
        with open(MASTER_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Cast booleans
                for bool_col in ["is_canonical", "has_zero_width_chars", "has_homoglyphs", "has_base64_wrapper"]:
                    if bool_col in row:
                        row[bool_col] = str(row[bool_col]).lower() in ("true", "1", "yes")
                records.append(row)
        return records
    else:
        raise FileNotFoundError("Master dataset file not found in data directory.")


def filter_dataset(
    records: List[Dict[str, Any]],
    risk_category: Optional[str] = None,
    family_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Filter records by risk_category and/or family_id.
    """
    filtered = records
    if risk_category:
        filtered = [r for r in filtered if r.get("risk_category") == risk_category]
    if family_id:
        filtered = [r for r in filtered if r.get("family_id") == family_id]
    return filtered


if __name__ == "__main__":
    records = load_dataset_records()
    print(f"Loaded {len(records)} benchmark prompt records.")
    
    # Summary of families
    from collections import Counter
    fam_counts = Counter(r["family_id"] for r in records)
    cat_counts = Counter(r["risk_category"] for r in records)
    
    print("\n--- Prompt Counts by Representation Family ---")
    for fam, count in sorted(fam_counts.items()):
        print(f"  {fam}: {count}")

    print("\n--- Prompt Counts by Risk Category ---")
    for cat, count in sorted(cat_counts.items()):
        print(f"  {cat}: {count}")

    print("\nSample Prompt (prompt_0001):")
    p1 = records[0]
    for k, v in p1.items():
        print(f"  {k}: {v}")
