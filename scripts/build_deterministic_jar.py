from __future__ import annotations

import argparse
import zipfile
from pathlib import Path


def add_bytes(archive: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    archive.writestr(info, data)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("classes", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    files = sorted(path for path in args.classes.rglob("*") if path.is_file())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, "w") as archive:
        add_bytes(archive, "META-INF/MANIFEST.MF", b"Manifest-Version: 1.0\r\n\r\n")
        for path in files:
            add_bytes(archive, path.relative_to(args.classes).as_posix(), path.read_bytes())


if __name__ == "__main__":
    main()
