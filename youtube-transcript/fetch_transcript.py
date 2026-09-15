#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

import requests
import yt_dlp

from cleaner import clean_captions


def resolve_caption_url(info: dict, lang: str) -> tuple[str, str]:
    """Pick a json3 caption track for `lang`, preferring manual subs over auto-generated.

    Returns (url, source) where source is "manual" or "automatic".
    """
    for key, source in (("subtitles", "manual"), ("automatic_captions", "automatic")):
        tracks = info.get(key) or {}
        for fmt in tracks.get(lang, []):
            if fmt.get("ext") == "json3":
                return fmt["url"], source

    available = sorted(set(info.get("subtitles") or {}) | set(info.get("automatic_captions") or {}))
    raise SystemExit(
        f"No '{lang}' captions (manual or automatic) found for this video.\n"
        f"Available languages: {', '.join(available) if available else '(none)'}"
    )


def fetch(video_url: str, lang: str, output_dir: Path) -> tuple[Path, Path]:
    ydl_opts = {
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": [lang],
        "subtitlesformat": "json3",
        "quiet": True,
        "no_warnings": True,
        # The default web client is frequently blocked by YouTube's bot checks
        # ("The page needs to be reloaded"); android/mweb reliably work instead.
        "extractor_args": {"youtube": {"player_client": ["android", "mweb"]}},
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)

    video_id = info["id"]
    caption_url, source = resolve_caption_url(info, lang)

    response = requests.get(caption_url, timeout=30)
    response.raise_for_status()
    raw = response.json()

    raw_dir = output_dir / "raw"
    clean_dir = output_dir / "clean"
    raw_dir.mkdir(parents=True, exist_ok=True)
    clean_dir.mkdir(parents=True, exist_ok=True)

    raw_path = raw_dir / f"{video_id}.json"
    raw_path.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")

    meta_path = raw_dir / f"{video_id}.meta.json"
    meta = {
        "id": video_id,
        "title": info.get("title"),
        "channel": info.get("channel") or info.get("uploader"),
        "upload_date": info.get("upload_date"),
        "url": info.get("webpage_url", video_url),
        "lang": lang,
        "caption_source": source,
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    clean_path = clean_dir / f"{video_id}.txt"
    clean_path.write_text(clean_captions(raw), encoding="utf-8")

    return raw_path, clean_path


def main():
    parser = argparse.ArgumentParser(description="Fetch and clean a YouTube video's transcript.")
    parser.add_argument("video_url", help="YouTube video URL")
    parser.add_argument("--lang", default="ru", help="Caption language code (default: ru)")
    parser.add_argument("--output-dir", default="output", help="Output directory (default: output)")
    args = parser.parse_args()

    raw_path, clean_path = fetch(args.video_url, args.lang, Path(args.output_dir))
    print(f"Raw captions:    {raw_path}")
    print(f"Cleaned transcript: {clean_path}")


if __name__ == "__main__":
    sys.exit(main())
