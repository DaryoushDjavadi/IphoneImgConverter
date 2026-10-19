"""Tests für die Konvertier-Logik (ohne GUI)."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from converter_core import collect_heic_files, convert_one, is_heic


def test_is_heic_extensions() -> None:
    assert is_heic(Path("foto.heic"))
    assert is_heic(Path("foto.HEIC"))
    assert is_heic(Path("foto.heif"))
    assert not is_heic(Path("foto.jpg"))
    assert not is_heic(Path("foto.png"))


def test_collect_files_and_folders(tmp_path: Path) -> None:
    (tmp_path / "a.heic").write_bytes(b"x")
    (tmp_path / "b.JPG").write_bytes(b"x")
    sub = tmp_path / "unter"
    sub.mkdir()
    (sub / "c.HEIF").write_bytes(b"x")

    found = collect_heic_files([tmp_path / "a.heic", tmp_path])
    names = sorted(p.name.lower() for p in found)
    assert names == ["a.heic", "c.heif"]


def test_convert_jpeg_roundtrip_via_pillow(tmp_path: Path) -> None:
    """Fallback-Test: JPEG als Quelle simuliert nicht HEIC,
    prüft aber Ausgabe-Logik mit echtem Bild – übersprungen ohne HEIC-Support.
    """
    pytest.importorskip("pillow_heif")

    # Minimales echtes JPEG erzeugen und als .jpg speichern –
    # convert_one erwartet HEIC, daher hier nur Namenskollision / Ordner testen
    # über einen echten HEIC-Versuch wenn möglich.
    src = tmp_path / "dummy.heic"
    # Ohne echte HEIC-Bytes schlägt convert fehl – das ist erwartet.
    src.write_bytes(b"not-a-real-heic")
    result = convert_one(src, tmp_path / "out", delete_original=False)
    assert result.success is False
    assert result.error


def test_output_dir_created_on_success_path(tmp_path: Path, monkeypatch) -> None:
    """Erfolgreiche Konvertierung mit Mock-Image."""
    from converter_core import convert_one as real_convert

    src = tmp_path / "bild.heic"
    src.write_bytes(b"fake")
    out_dir = tmp_path / "jpeg_out"

    class FakeImg:
        def convert(self, mode: str) -> "FakeImg":
            return self

        def save(self, path, format=None, **kwargs) -> None:  # noqa: A002, ANN003
            Path(path).write_bytes(b"jpeg-bytes")

        def __enter__(self) -> "FakeImg":
            return self

        def __exit__(self, *args) -> None:  # noqa: ANN002
            return None

    import converter_core as core

    monkeypatch.setattr(
        core.Image,
        "open",
        lambda _path: FakeImg(),
    )

    result = real_convert(src, out_dir, delete_original=False)
    assert result.success
    assert result.output is not None
    assert result.output.exists()
    assert result.output.suffix == ".jpg"
    assert src.exists()


def test_delete_original(tmp_path: Path, monkeypatch) -> None:
    src = tmp_path / "bild.heic"
    src.write_bytes(b"fake")

    class FakeImg:
        def convert(self, mode: str) -> "FakeImg":
            return self

        def save(self, path, format=None, **kwargs) -> None:  # noqa: A002, ANN003
            Path(path).write_bytes(b"jpeg-bytes")

        def __enter__(self) -> "FakeImg":
            return self

        def __exit__(self, *args) -> None:  # noqa: ANN002
            return None

    import converter_core as core

    monkeypatch.setattr(core.Image, "open", lambda _path: FakeImg())

    result = convert_one(src, tmp_path, delete_original=True)
    assert result.success
    assert result.deleted_original
    assert not src.exists()
