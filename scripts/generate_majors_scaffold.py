"""
Generate `data/majors.json` from `Stanford Programs List.csv`.

Each major entry has:
- id: slugified program name (lowercase, underscores)
- name: program name
- link: URL from the CSV
- features: all keys initialized to null (None in Python)
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "Stanford Programs List.csv"
OUTPUT_PATH = ROOT / "data" / "majors.json"


FEATURE_KEYS = [
    "mathematical_rigor",
    "computational_intensity",
    "statistical_reasoning",
    "systems_thinking",
    "engineering_orientation",
    "experimental_lab_work",
    "empirical_fieldwork",
    "biological_focus",
    "physical_science_focus",
    "modeling_abstraction",
    "human_behavior_focus",
    "social_institutions_focus",
    "policy_relevance",
    "ethical_normative_reasoning",
    "historical_contextual_analysis",
    "reading_intensity",
    "writing_intensity",
    "argumentative_reasoning",
    "creative_design",
    "ambiguity_tolerance",
    "applied_problem_solving",
    "interdisciplinarity",
]


def slugify(name: str) -> str:
    """
    Turn a program name into a stable identifier.

    Rules:
    - lowercase
    - non-alphanumeric characters -> underscore
    - collapse multiple underscores
    - trim leading/trailing underscores
    """
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    name = re.sub(r"_+", "_", name)
    return name.strip("_")


def build_majors() -> list[dict]:
    majors: list[dict] = []

    with CSV_PATH.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            program = row.get("Program", "").strip()
            link = row.get("Link", "").strip()
            if not program:
                continue

            major_id = slugify(program)
            features = {key: None for key in FEATURE_KEYS}

            majors.append(
                {
                    "id": major_id,
                    "name": program,
                    "link": link,
                    "features": features,
                }
            )

    return majors


def main() -> None:
    majors = build_majors()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(majors, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(majors)} majors to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

