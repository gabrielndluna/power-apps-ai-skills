"""Pack PostAward and inject excel-icon-17 media (ProcTrack pattern)."""

from __future__ import annotations

import json
import shutil
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
PACKED = ROOT / "app.msapp"
PNG = ROOT / "media" / "excel-icon-17.png"
GUID = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
FILENAME = f"{GUID}.png"


def inject_excel(msapp: Path) -> None:
    if not PNG.exists():
        raise SystemExit(f"Missing {PNG}")

    tmp = ROOT / "_media_inject_tmp"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir()
    work = tmp / "app.zip"
    shutil.copy2(msapp, work)
    out = tmp / "contents"
    with zipfile.ZipFile(work) as z:
        z.extractall(out)

    assets = out / "Assets" / "Images"
    assets.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PNG, assets / FILENAME)

    res_path = out / "References" / "Resources.json"
    data = json.loads(res_path.read_text(encoding="utf-8")) if res_path.exists() else {"Resources": []}
    resources = [
        r
        for r in data.get("Resources", [])
        if not (isinstance(r, dict) and r.get("Name") == "excel-icon-17")
    ]
    resources.append(
        {
            "Name": "excel-icon-17",
            "Schema": "i",
            "IsSampleData": False,
            "IsWritable": False,
            "Type": "ResourceInfo",
            "FileName": FILENAME,
            "Path": f"Assets\\Images\\{FILENAME}",
            "Content": "Image",
            "ResourceKind": "LocalFile",
            "RootPath": f"msft-powerapps-canvas:///Assets/Images/{FILENAME}",
        }
    )
    data["Resources"] = resources
    res_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    # rewrite zip
    if msapp.exists():
        msapp.unlink()
    with zipfile.ZipFile(msapp, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for f in sorted(out.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(out).as_posix())

    shutil.rmtree(tmp)


def main() -> int:
    print("Running pac canvas pack...")
    subprocess.run(
        [
            "pac",
            "canvas",
            "pack",
            "--sources",
            str(SRC),
            "--msapp",
            str(PACKED),
            "--layout",
            "SourceCode",
            "--overwrite",
        ],
        check=True,
    )
    print("Injecting excel-icon-17 media...")
    inject_excel(PACKED)
    print(f"Done: {PACKED} ({PACKED.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
