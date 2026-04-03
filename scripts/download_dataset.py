#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

DATASET = "thoughtvector/customer-support-on-twitter"
OUTPUT_DIR = Path("data/tickets/raw")


def _has_kaggle_credentials() -> bool:
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    env_auth = bool(os.getenv("KAGGLE_USERNAME") and os.getenv("KAGGLE_KEY"))
    return kaggle_json.exists() or env_auth


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not _has_kaggle_credentials():
        print(
            "[ERROR] Kaggle credentials not found. Configure either "
            "~/.kaggle/kaggle.json or KAGGLE_USERNAME/KAGGLE_KEY environment variables."
        )
        sys.exit(1)

    scripts_dir = Path(sys.executable).resolve().parent
    kaggle_exe = scripts_dir / ("kaggle.exe" if os.name == "nt" else "kaggle")

    # Prefer the venv executable, fall back to PATH if needed.
    cmd = [
        str(kaggle_exe) if kaggle_exe.exists() else "kaggle",
        "datasets",
        "download",
        "-d",
        DATASET,
        "-p",
        str(OUTPUT_DIR),
        "--unzip",
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"[INFO] Dataset downloaded to {OUTPUT_DIR}/")
    except subprocess.CalledProcessError as exc:
        print(f"[ERROR] Kaggle download failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
