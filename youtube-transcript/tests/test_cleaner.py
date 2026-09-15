import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cleaner import clean_captions

REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_JSON = REPO_ROOT / "SourceFiles" / "2025" / "2025_1_2.json"
EXPECTED_TXT = REPO_ROOT / "Transcript" / "2025" / "2025_1_2_cl.txt"


def test_clean_captions_matches_existing_archive():
    raw = json.loads(RAW_JSON.read_text(encoding="utf-8"))
    expected = EXPECTED_TXT.read_text(encoding="utf-8")
    assert clean_captions(raw) == expected


if __name__ == "__main__":
    test_clean_captions_matches_existing_archive()
    print("OK: clean_captions() matches Transcript/2025/2025_1_2_cl.txt exactly")
