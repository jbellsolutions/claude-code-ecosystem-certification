#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import imageio_ffmpeg


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "site" / "data" / "course-data.json"
SOURCE_DIR = Path("/Users/home/Downloads/Descript videos")
BRAND_DIR = ROOT / "site" / "assets" / "brand"
SLATE_DIR = BRAND_DIR / "slates"
OUTPUT_DIR = ROOT / "edited_videos"
TEMP_DIR = OUTPUT_DIR / ".tmp"


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def safe_slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def build_still_clip(ffmpeg: str, image_path: Path, output_path: Path, seconds: int = 3) -> None:
    run(
        [
            ffmpeg,
            "-y",
            "-loop",
            "1",
            "-i",
            str(image_path),
            "-f",
            "lavfi",
            "-i",
            "anullsrc=channel_layout=stereo:sample_rate=48000",
            "-t",
            str(seconds),
            "-r",
            "30",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            "-ar",
            "48000",
            "-shortest",
            str(output_path),
        ]
    )


def clean_body(ffmpeg: str, source_path: Path, output_path: Path) -> None:
    run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(source_path),
            "-vf",
            "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
            "-af",
            "loudnorm=I=-16:LRA=11:TP=-1.5",
            "-r",
            "30",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "20",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            "-ar",
            "48000",
            str(output_path),
        ]
    )


def concat_clips(ffmpeg: str, files: list[Path], output_path: Path) -> None:
    list_path = TEMP_DIR / f"{output_path.stem}-concat.txt"
    list_path.write_text("".join(f"file '{path.as_posix()}'\n" for path in files))
    run(
        [
            ffmpeg,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_path),
            "-c",
            "copy",
            str(output_path),
        ]
    )


def main() -> None:
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    data = json.loads(DATA_PATH.read_text())

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    outro_image = BRAND_DIR / "outro-slate.png"
    outro_clip = TEMP_DIR / "outro-clip.mp4"
    build_still_clip(ffmpeg, outro_image, outro_clip)

    for index, module in enumerate(data["modules"], start=1):
        source_path = SOURCE_DIR / module["source"]
        if not source_path.exists() or source_path.stat().st_size == 0:
            continue

        slug = f"{index:02d}-{safe_slug(module['title'])}"
        intro_image = SLATE_DIR / f"{module['id']}.png"
        intro_clip = TEMP_DIR / f"{slug}-intro.mp4"
        body_clip = TEMP_DIR / f"{slug}-body.mp4"
        final_clip = OUTPUT_DIR / f"{slug}.mp4"

        build_still_clip(ffmpeg, intro_image, intro_clip)
        clean_body(ffmpeg, source_path, body_clip)
        concat_clips(ffmpeg, [intro_clip, body_clip, outro_clip], final_clip)
        print(f"Rendered {final_clip.name}")


if __name__ == "__main__":
    main()
