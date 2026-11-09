#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import re
import stat
from pathlib import Path, PurePosixPath
from zipfile import ZIP_STORED, ZipFile

ROOT = Path(__file__).resolve().parent.parent
MODULE = ROOT / "module"
DIST = ROOT / "dist"
FIXED_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
FILES = (
    ("customize.sh", MODULE / "customize.sh", 0o755),
    ("LICENSE", ROOT / "LICENSE", 0o644),
    ("module.prop", MODULE / "module.prop", 0o644),
    ("service.sh", MODULE / "service.sh", 0o755),
    ("skip_mount", MODULE / "skip_mount", 0o644),
    ("uninstall.sh", MODULE / "uninstall.sh", 0o755),
)
REQUIRED_METADATA = {
    "id",
    "name",
    "version",
    "versionCode",
    "author",
    "description",
}


def fail(message: str) -> None:
    raise SystemExit(f"verification failed: {message}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def metadata() -> dict[str, str]:
    values: dict[str, str] = {}
    for number, line in enumerate((MODULE / "module.prop").read_text(encoding="utf-8").splitlines(), 1):
        if not line or "=" not in line:
            fail(f"invalid module.prop line {number}")
        key, value = line.split("=", 1)
        if key in values:
            fail(f"duplicate module.prop key: {key}")
        values[key] = value

    if set(values) != REQUIRED_METADATA:
        fail("module.prop keys do not match the required set")
    if values["id"] != "wifi_power_save_off":
        fail("unexpected module id")
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9._-]+", values["id"]):
        fail("invalid module id")
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", values["version"]):
        fail("version is not semantic X.Y.Z")
    if not values["versionCode"].isdigit():
        fail("versionCode is not an integer")
    if values["author"] != "sergej19882906":
        fail("unexpected module author")
    return values


def verify_sources() -> None:
    for archive_name, source, _ in FILES:
        data = source.read_bytes()
        if data.startswith(b"\xef\xbb\xbf"):
            fail(f"UTF-8 BOM in {source.relative_to(ROOT)}")
        if b"\r" in data:
            fail(f"CRLF in {source.relative_to(ROOT)}")
        if data and not data.endswith(b"\n"):
            fail(f"missing final newline in {source.relative_to(ROOT)}")
        if archive_name.endswith(".sh") and not data.startswith(b"#!/system/bin/sh\n"):
            fail(f"invalid shebang in {source.relative_to(ROOT)}")


def verify_zip(version: str) -> Path:
    archive_path = DIST / f"magisk-wifi-power-save-off-v{version}.zip"
    if not archive_path.is_file():
        fail(f"missing {archive_path.relative_to(ROOT)}")

    expected_names = [entry[0] for entry in FILES]
    with ZipFile(archive_path) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if names != expected_names:
            fail(f"unexpected ZIP entries or order: {names}")
        if len(set(names)) != len(names):
            fail("duplicate ZIP entries")

        for info, (archive_name, source, expected_mode) in zip(infos, FILES, strict=True):
            path = PurePosixPath(info.filename)
            if path.is_absolute() or ".." in path.parts or "\\" in info.filename:
                fail(f"unsafe ZIP path: {info.filename}")
            if info.is_dir():
                fail(f"unexpected directory entry: {info.filename}")
            if info.create_system != 3:
                fail(f"non-Unix ZIP entry: {info.filename}")
            if info.date_time != FIXED_TIMESTAMP:
                fail(f"non-reproducible timestamp: {info.filename}")
            if info.compress_type != ZIP_STORED:
                fail(f"compressed ZIP entry: {info.filename}")

            raw_mode = info.external_attr >> 16
            if stat.S_IFMT(raw_mode) != stat.S_IFREG:
                fail(f"non-regular ZIP entry: {info.filename}")
            if stat.S_IMODE(raw_mode) != expected_mode:
                fail(f"wrong mode for {info.filename}")
            if archive.read(archive_name) != source.read_bytes():
                fail(f"ZIP content differs from source: {info.filename}")

    return archive_path


def verify_checksum(archive_path: Path) -> str:
    digest = sha256(archive_path)
    checksum_path = DIST / "SHA256SUMS"
    expected = f"{digest}  {archive_path.name}\n"
    if not checksum_path.is_file() or checksum_path.read_text(encoding="utf-8") != expected:
        fail("SHA256SUMS does not match the release ZIP")
    return digest


def main() -> None:
    verify_sources()
    values = metadata()
    archive_path = verify_zip(values["version"])
    digest = verify_checksum(archive_path)
    print(f"Verified {archive_path.relative_to(ROOT)}")
    print(f"SHA-256 {digest}")


if __name__ == "__main__":
    main()
