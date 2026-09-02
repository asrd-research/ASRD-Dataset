---
annotations_creators:
- expert-generated
language:
- en
license: cc-by-nc-4.0
multilinguality:
- monolingual
size_categories:
- 1K<n<10K
source_datasets:
- original
task_categories:
- text-generation
tags:
- ai-safety
- adversarial-robustness
- red-teaming
- jailbreak-benchmark
- unicode-eval
- prompt-transformations
pretty_name: "Adversarial Surface-Form Robustness Dataset (ASRD)"
---

# Adversarial Surface-Form Robustness Dataset (ASRD)

> **Anonymous Repository for Double-Blind Review**  
> *NeurIPS 2026 Workshop*

---

## 1. Dataset Overview

Standard safety evaluations of large language models routinely measure model refusal and compliance using canonical plain-text instructions. However, deployed systems frequently encounter non-canonical inputs containing expressive symbols (emojis), character-level substitutions (homoglyphs, leetspeak), structured encodings (Base64), and non-printing invisible Unicode characters.

The **Adversarial Surface-Form Robustness Dataset (ASRD)** provides a standardized benchmark dataset for evaluating model robustness across surface-form variations without altering underlying semantic intent. The dataset consists of **2,100 prompts** derived from **300 base harmful seeds** spanning **6 semantic risk categories** and transformed across **7 prompt representation families**.

---

## 2. Prompt Representation Families

Each of the 300 base seeds is converted into six non-canonical surface-form variants using deterministic rule-based transformations:

| Family ID | Family Name | Structural Pattern | Count | Description |
| :--- | :--- | :--- | :---: | :--- |
| `0_baseline` | **Baseline Canonical** | `[text]` | 300 | Unmodified plain-text instructions serving as canonical references. |
| `1_emoji` | **Emoji-Augmented** | `[text] [emoji] [text] [text] [emoji] [text]` | 300 | Natural language prompts interleaved with context-shifting emojis. |
| `2_homoglyph` | **Homoglyph Substitution** | `[homoglyph_text] [emoji]` | 300 | Selected Latin characters replaced with Cyrillic and Greek code points + emoji. |
| `3_leetspeak_emoji` | **Leetspeak and Emoji** | `[leetspeak_text] [emoji] [emoji]` | 300 | Alphanumeric leetspeak character substitutions paired with emojis. |
| `4_encoded_emoji` | **Base64 Encoded Wrapper** | `[emoji] [text] [base64_payload] [emoji]` | 300 | Base64-encoded payload placed within an instructional wrapper with emojis. |
| `5_invisible` | **Invisible Unicode** | `[text] [invisible_chars] [text]` | 300 | Zero-width non-printing Unicode insertions (`U+200B`, `U+200C`, `U+200D`). |
| `6_hybrid` | **Hybrid Transformation** | `[text] [emoji] [hybrid_text] [emoji]` | 300 | Multi-transformation combination (emojis, leetspeak, homoglyphs, invisible tokens). |
| **Total** | | | **2,100** | |

---

## 3. Semantic Risk Categories

The 300 base seeds are evenly distributed across six semantic risk categories (50 seeds each, yielding 350 prompts per category across the 7 families):

1. `cybercrime_and_intrusion` (Seeds 0001–0050): Malware creation, credential theft, unauthorized access, network exploitation, and vulnerability abuse.
2. `cbrn_and_dangerous_materials` (Seeds 0051–0100): Chemical, biological, radiological, and nuclear materials, dangerous synthesis recipes, and illicit substance production.
3. `misinformation_and_disinformation` (Seeds 0101–0150): Disinformation campaigns, deepfake generation, election manipulation, and fabricated medical claims.
4. `harassment_and_bullying` (Seeds 0151–0200): Targeted harassment, hate speech, doxxing, online intimidation, and cyberbullying.
5. `illegal_activities` (Seeds 0201–0250): Financial fraud, money laundering, smuggling, and evasion of legal authorities.
6. `general_harm` (Seeds 0251–0300): Physical harm, kinetic weapons, explosives, suicide facilitation, and public endangerment.

---

## 4. Dataset Schema & Data Dictionary

The master dataset (`prompts_master.csv`, `prompts_master.jsonl`, and `prompts_master.parquet`) provides the following fields:

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `prompt_id` | `string` | **Globally unique identifier** across all 2,100 prompts (e.g., `prompt_0001` to `prompt_2100`). |
| `family_prompt_id` | `string` | Family-scoped identifier (e.g., `f0_0001` to `f6_0300`). |
| `seed_id` | `string` | Base seed identifier (`seed_0001` to `seed_0300`), linking all 7 surface-form variants to the same semantic root. |
| `risk_category` | `string` | One of the 6 semantic risk categories. |
| `family_id` | `string` | Short identifier for the prompt family (e.g., `0_baseline`, `1_emoji`). |
| `family_name` | `string` | Human-readable name for the prompt family. |
| `is_canonical` | `bool` | `True` for baseline plain-text prompts; `False` for transformed prompts. |
| `has_zero_width_chars` | `bool` | `True` if prompt contains non-printing Unicode (ZWSP, ZWNJ, ZWJ). |
| `has_homoglyphs` | `bool` | `True` if prompt contains Cyrillic or Greek homoglyphs. |
| `has_base64_wrapper` | `bool` | `True` if prompt contains an encoded Base64 wrapper. |
| `decoded_base64_payload` | `string` | The decoded string payload for Family 4 prompts (empty string for other families). |
| `base_seed` | `string` | Canonical plain-text seed instruction. |
| `full_prompt` | `string` | Exact prompt string submitted to the evaluated model. |

---

## 5. Repository Structure

```text
adversarial_surface_prompts/
├── data/
│   ├── prompts_master.parquet     # Recommended format (fast, preserves types)
│   ├── prompts_master.jsonl       # Standard JSON Lines (one JSON object per prompt)
│   ├── prompts_master.csv         # Clean UTF-8 CSV without BOM
│   └── families/                  # Individual CSVs for each transformation family
│       ├── family_0_baseline.csv
│       ├── family_1_emoji.csv
│       ├── family_2_homoglyph.csv
│       ├── family_3_leetspeak_emoji.csv
│       ├── family_4_encoded_emoji.csv
│       ├── family_5_invisible.csv
│       └── family_6_hybrid.csv
├── load_dataset.py                # Standalone Python loader with zero mandatory dependencies
├── LICENSE                        # CC-BY-NC-4.0 with AI Safety Defensive Research Addendum
└── README.md                      # Dataset documentation and benchmark specification
```

---

## 6. Quickstart Usage

### Using the Included Standalone Loader (Zero Dependencies)

```python
from load_dataset import load_dataset_records, filter_dataset

# Load all 2,100 records
records = load_dataset_records()
print(f"Loaded {len(records)} prompts.")

# Filter by family and risk category
cyber_homoglyphs = filter_dataset(
    records,
    risk_category="cybercrime_and_intrusion",
    family_id="2_homoglyph"
)
print(f"Found {len(cyber_homoglyphs)} homoglyph cybercrime prompts.")
```

### Using Pandas

```python
import pandas as pd

# Load from Parquet (recommended)
df = pd.read_parquet("data/prompts_master.parquet")

# Or load from JSONL / CSV
# df = pd.read_json("data/prompts_master.jsonl", lines=True)
# df = pd.read_csv("data/prompts_master.csv")

print(df.groupby(["family_name", "risk_category"]).size())
```

---

## 7. Responsible Use & Ethical Disclaimer

> [!WARNING]
> **Defensive and Evaluative Research Purpose Only**  
> This dataset contains red-teaming prompts touching on hazardous topics, including cyberattacks, toxic substances, and illegal activities. It is released exclusively to advance automated safety evaluation, red-teaming rigor, and robustness against non-canonical adversarial evasion.
> 
> Under the terms of the **CC-BY-NC-4.0 License** and the **AI Safety Defensive Research Addendum**:
> - The dataset may not be used for malicious purposes, operational attacks, or harassment.
> - The dataset may not be commercialized or integrated into offensive tooling.
