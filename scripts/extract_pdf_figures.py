#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import fitz


def slugify(value: str) -> str:
    lowered = value.strip().lower()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    lowered = re.sub(r"-{2,}", "-", lowered).strip("-")
    return lowered or "asset"


def load_card(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save_card(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def render_page(pdf_path: Path, page_number: int, out_path: Path, zoom: float) -> None:
    doc = fitz.open(pdf_path)
    try:
        page = doc.load_page(page_number - 1)
        matrix = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        pix.save(out_path)
    finally:
        doc.close()


def process_entries(entries: list[dict], kind: str, pdf_path: Path, assets_dir: Path, zoom: float) -> list[dict]:
    updated: list[dict] = []
    for index, entry in enumerate(entries, start=1):
        page = int(entry.get("page", 0) or 0)
        item = dict(entry)
        if page <= 0:
            updated.append(item)
            continue

        label = item.get("label") or f"{kind}-{index}"
        filename = f"{kind}-p{page:02d}-{slugify(label)}.png"
        out_path = assets_dir / filename
        render_page(pdf_path, page, out_path, zoom)
        item["image_path"] = f"./assets/{filename}"
        updated.append(item)
    return updated


def main() -> int:
    parser = argparse.ArgumentParser(description="Render key figure/table pages from a paper PDF into image assets.")
    parser.add_argument("paper_id", help="Paper id that already exists in memory.")
    parser.add_argument("--root", default=".", help="Workspace root.")
    parser.add_argument("--memory-dir", default=".ob-paper-read-memory", help="Memory directory name.")
    parser.add_argument("--vault-dir", default="reading-vault", help="Vault output directory.")
    parser.add_argument("--zoom", type=float, default=2.0, help="Render zoom factor. Default: 2.0")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    card_path = root / args.memory_dir / "papers" / f"{args.paper_id}.json"
    if not card_path.exists():
        raise FileNotFoundError(f"Paper card not found: {card_path}")

    card = load_card(card_path)
    pdf_path = Path(card.get("source", {}).get("path", "")).expanduser()
    if not pdf_path.exists():
        raise FileNotFoundError(f"Source PDF not found: {pdf_path}")

    assets_dir = root / args.vault_dir / "papers" / args.paper_id / "assets"
    key_figures = process_entries(card.get("key_figures", []), "figure", pdf_path, assets_dir, args.zoom)
    key_tables = process_entries(card.get("key_tables", []), "table", pdf_path, assets_dir, args.zoom)

    card["key_figures"] = key_figures
    card["key_tables"] = key_tables
    save_card(card_path, card)

    print(f"Rendered assets in: {assets_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
