"""HEIC/HEIF → JPEG Konvertierung."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()

HEIC_EXTENSIONS = {".heic", ".heif"}


@dataclass
class ConvertResult:
    source: Path
    output: Path | None
    success: bool
    error: str | None = None
    deleted_original: bool = False


def is_heic(path: Path) -> bool:
    return path.suffix.lower() in HEIC_EXTENSIONS


def collect_heic_files(paths: list[Path]) -> list[Path]:
    """Dateien und Ordner einsammeln; doppelte Einträge vermeiden."""
    found: list[Path] = []
    seen: set[Path] = set()

    for path in paths:
        path = path.resolve()
        if path in seen:
            continue
        if path.is_file() and is_heic(path):
            seen.add(path)
            found.append(path)
        elif path.is_dir():
            for child in sorted(path.rglob("*")):
                if child.is_file() and is_heic(child):
                    resolved = child.resolve()
                    if resolved not in seen:
                        seen.add(resolved)
                        found.append(resolved)
    return found


def convert_one(
    source: Path,
    output_dir: Path | None,
    *,
    quality: int = 95,
    delete_original: bool = False,
) -> ConvertResult:
    """Eine HEIC-Datei nach JPEG konvertieren."""
    try:
        if output_dir is None:
            target_dir = source.parent
        else:
            target_dir = output_dir
            target_dir.mkdir(parents=True, exist_ok=True)

        output = target_dir / (source.stem + ".jpg")

        # Bei Namenskollision nummerieren
        if output.exists() and output.resolve() != source.resolve():
            counter = 1
            while True:
                candidate = target_dir / f"{source.stem}_{counter}.jpg"
                if not candidate.exists():
                    output = candidate
                    break
                counter += 1

        with Image.open(source) as img:
            rgb = img.convert("RGB")
            rgb.save(output, "JPEG", quality=quality, optimize=True)

        deleted = False
        if delete_original:
            os.remove(source)
            deleted = True

        return ConvertResult(
            source=source,
            output=output,
            success=True,
            deleted_original=deleted,
        )
    except Exception as exc:  # noqa: BLE001 - Fehler an die GUI weiterreichen
        return ConvertResult(
            source=source,
            output=None,
            success=False,
            error=str(exc),
        )


def convert_many(
    sources: list[Path],
    output_dir: Path | None,
    *,
    quality: int = 95,
    delete_original: bool = False,
    on_progress: Callable[[int, int, ConvertResult], None] | None = None,
) -> list[ConvertResult]:
    results: list[ConvertResult] = []
    total = len(sources)
    for index, source in enumerate(sources, start=1):
        result = convert_one(
            source,
            output_dir,
            quality=quality,
            delete_original=delete_original,
        )
        results.append(result)
        if on_progress is not None:
            on_progress(index, total, result)
    return results
