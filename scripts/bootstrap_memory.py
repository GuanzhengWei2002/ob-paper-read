#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_PROFILE = {
    "user_id": "local-user",
    "domains_of_interest": [],
    "preferences": {
        "language": "zh-CN",
        "style": "intuition-first",
        "difficulty_default": "beginner",
        "depth_default": "standard",
    },
    "workspace": {
        "obsidian_vault_path": "",
        "raw_library_path": "",
        "guide_output_path": "",
    },
    "capabilities": {
        "pdf_upload_only": True,
    },
    "recent_papers": [],
    "recent_sessions": [],
}


def ensure_json(path: Path, payload: object) -> None:
    if not path.exists():
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a local ob-paper-read memory workspace.")
    parser.add_argument("--root", default=".", help="Workspace root. Default: current directory.")
    parser.add_argument(
        "--memory-dir",
        default=".ob-paper-read-memory",
        help="Memory directory name relative to root.",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    memory_root = root / args.memory_dir

    for subdir in ("papers", "concepts", "questions", "sessions", "compare", "recommendations"):
        (memory_root / subdir).mkdir(parents=True, exist_ok=True)

    ensure_json(memory_root / "user-profile.json", DEFAULT_PROFILE)

    print(f"Memory root: {memory_root}")
    print("Ready: papers, concepts, questions, sessions, compare, recommendations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
