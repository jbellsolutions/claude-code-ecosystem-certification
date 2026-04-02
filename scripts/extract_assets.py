#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import imageio_ffmpeg


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = Path("/Users/home/Downloads/Descript videos")
RAW_SRT_DIR = ROOT / "transcripts" / "raw_srt"
PLAIN_TEXT_DIR = ROOT / "transcripts" / "plain_text"
POSTER_DIR = ROOT / "site" / "assets" / "posters"
DATA_DIR = ROOT / "site" / "data"


def extract_duration(stderr_text: str) -> str:
    for line in stderr_text.splitlines():
        if "Duration:" in line:
            return line.split("Duration:", 1)[1].split(",", 1)[0].strip()
    return "Unknown"


def srt_to_text(contents: str) -> str:
    lines = []
    for raw_line in contents.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.isdigit():
            continue
        if "-->" in line:
            continue
        lines.append(line)

    text = " ".join(lines)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"([.!?])([A-Z])", r"\1 \2", text)
    return text


def main() -> None:
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    RAW_SRT_DIR.mkdir(parents=True, exist_ok=True)
    PLAIN_TEXT_DIR.mkdir(parents=True, exist_ok=True)
    POSTER_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    videos = []

    for video_path in sorted(SOURCE_DIR.glob("*.mp4")):
        if video_path.stat().st_size == 0:
            continue

        stem = video_path.stem
        safe_stem = re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-")
        srt_path = RAW_SRT_DIR / f"{stem}.srt"
        text_path = PLAIN_TEXT_DIR / f"{stem}.txt"
        poster_path = POSTER_DIR / f"{safe_stem}.jpg"

        inspect_result = subprocess.run(
            [ffmpeg, "-i", str(video_path)],
            capture_output=True,
            text=True,
        )
        inspect_text = inspect_result.stderr or inspect_result.stdout

        subprocess.run(
            [ffmpeg, "-y", "-i", str(video_path), "-map", "0:s:0", str(srt_path)],
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-ss",
                "00:00:05",
                "-i",
                str(video_path),
                "-frames:v",
                "1",
                "-q:v",
                "2",
                str(poster_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        text = srt_to_text(srt_path.read_text())
        text_path.write_text(text)

        videos.append(
            {
                "file_name": video_path.name,
                "stem": stem,
                "slug": safe_stem,
                "duration": extract_duration(inspect_text),
                "transcript_path": str(text_path.relative_to(ROOT)),
                "poster_path": str(poster_path.relative_to(ROOT / "site")),
            }
        )

    (DATA_DIR / "source-videos.json").write_text(json.dumps(videos, indent=2))
    print(f"Prepared {len(videos)} videos")


if __name__ == "__main__":
    main()
