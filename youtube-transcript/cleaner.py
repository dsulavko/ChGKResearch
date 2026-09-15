import re

BRACKET_TAG_RE = re.compile(r"\[[^\]]*\]")
WHITESPACE_RE = re.compile(r"\s+")


def clean_captions(raw: dict) -> str:
    """Turn a raw YouTube json3/srv3 caption payload into one continuous line of text."""
    parts = []
    for event in raw.get("events", []):
        for seg in event.get("segs", []):
            parts.append(seg.get("utf8", ""))
    joined = "".join(parts)
    no_tags = BRACKET_TAG_RE.sub("", joined)
    return WHITESPACE_RE.sub(" ", no_tags).strip()
