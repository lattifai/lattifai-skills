#!/usr/bin/env python3
"""Probe a media file for video dimensions and recommend karaoke rendering params.

Usage:
    probe_media.py <media_path> [--target-platform tiktok|youtube|...]

Outputs JSON to stdout so the agent can drive `laicap-convert` directly:

    {
      "width": 3840, "height": 2160,
      "aspect": "landscape",
      "font_size": 151,
      "play_res_x": 3840, "play_res_y": 2160,
      "source": "probe"
    }

If the file has no video stream (audio-only), falls back to a target-platform
default. Platforms & resolutions:

  tiktok / douyin / reels / shorts   1080x1920   (9:16 portrait)
  youtube                             1920x1080   (16:9 landscape)
  instagram / square                  1080x1080   (1:1 square)
  cinematic                           3840x1634   (2.35:1 landscape)
  default                             1920x1080   (16:9 landscape)

Font-size heuristic (tuned from TikTok/Reels best practices and Netflix-tier
broadcast subtitling):

  portrait  (aspect<0.85) : font_size = width  * 0.08   (big, punchy)
  square    (0.85-1.4)    : font_size = height * 0.075
  landscape (aspect>1.4)  : font_size = height * 0.07
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

PLATFORM_DEFAULTS: dict[str, tuple[int, int]] = {
    "tiktok":    (1080, 1920),
    "douyin":    (1080, 1920),
    "reels":     (1080, 1920),
    "shorts":    (1080, 1920),
    "youtube":   (1920, 1080),
    "instagram": (1080, 1080),
    "square":    (1080, 1080),
    "cinematic": (3840, 1634),
    "default":   (1920, 1080),
}


def probe_dimensions(path: Path) -> tuple[int, int] | None:
    """Return (width, height) of the first video stream, or None if absent."""
    try:
        out = subprocess.check_output(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height",
             "-of", "csv=p=0", str(path)],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    if not out:
        return None
    # ffprobe may emit "w,h\n" or multiple streams; take the first row.
    first = out.splitlines()[0]
    parts = [p for p in first.split(",") if p.strip()]
    if len(parts) < 2:
        return None
    w, h = int(parts[0]), int(parts[1])
    if w <= 0 or h <= 0:
        return None
    return w, h


def classify_aspect(w: int, h: int) -> str:
    ratio = w / h
    if ratio < 0.85:
        return "portrait"
    if ratio > 1.4:
        return "landscape"
    return "square"


def recommend_font_size(w: int, h: int, aspect: str) -> int:
    if aspect == "portrait":
        return int(round(w * 0.08))
    if aspect == "square":
        return int(round(h * 0.075))
    return int(round(h * 0.07))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("media", type=Path, help="Media file (.mp4, .mov, .mp3, ...)")
    ap.add_argument("--target-platform", default="default",
                    choices=sorted(PLATFORM_DEFAULTS.keys()),
                    help="Fallback when media has no video stream (audio-only)")
    args = ap.parse_args()

    dims = probe_dimensions(args.media) if args.media.exists() else None
    if dims is None:
        dims = PLATFORM_DEFAULTS[args.target_platform]
        source = f"platform-default:{args.target_platform}"
    else:
        source = "probe"

    w, h = dims
    aspect = classify_aspect(w, h)
    font_size = recommend_font_size(w, h, aspect)

    result = {
        "width": w,
        "height": h,
        "aspect": aspect,
        "font_size": font_size,
        "play_res_x": w,
        "play_res_y": h,
        "source": source,
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
