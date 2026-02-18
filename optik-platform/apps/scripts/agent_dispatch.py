#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import re

IGNORE_DIRS = {
    "node_modules",
    ".next",
    ".git",
    ".playwright",
    ".ruff_cache",
    ".vscode",
    ".devcontainer",
    ".claude",
    "test_suite_analysis"
}

IGNORE_FILES = {
    ".DS_Store",
    "npm-debug.log",
    "yarn-error.log"
}


def load_manifest(manifest_path: Path) -> dict:
    if not manifest_path.exists():
        return {}
    with manifest_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def should_ignore(path: Path) -> bool:
    for part in path.parts:
        if part in IGNORE_DIRS:
            return True
    if path.name in IGNORE_FILES:
        return True
    if path.name.startswith(".env") and path.name != ".env.example":
        return True
    return False


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "_", value)
    return value.strip("_").lower()


def determine_domain(rel_path: str, domain_rules: dict) -> str:
    for domain, prefixes in domain_rules.items():
        for prefix in prefixes:
            if rel_path.startswith(prefix):
                return domain
    return "platform"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate file-level agent registry.")
    parser.add_argument("--root", default=None, help="Project root (default: repo root).")
    parser.add_argument("--manifest", default="agents/manifest.json", help="Manifest path.")
    parser.add_argument("--output", default="agents/registry.json", help="Registry output path.")
    parser.add_argument("--write", action="store_true", help="Write registry to disk.")
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    manifest_path = root / args.manifest
    manifest = load_manifest(manifest_path)
    domain_rules = manifest.get("domain_rules", {})

    files = []
    top_level_dirs = set()

    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if should_ignore(path):
            continue
        rel_path = path.relative_to(root)
        rel_posix = rel_path.as_posix()
        top_level = rel_path.parts[0] if len(rel_path.parts) > 0 else "root"
        if path.is_file() and path.parent == root:
            top_level = "root"
        top_level_dirs.add(top_level)
        superagent_id = f"folder_superagent_{slugify(top_level)}"
        domain = determine_domain(rel_posix + ("/" if path.is_dir() else ""), domain_rules)
        agent_id = f"file_master_{slugify(rel_posix)}"
        proof_path = f"audit/proofs/files/{slugify(rel_posix)}.json"
        files.append({
            "file": rel_posix,
            "agent_id": agent_id,
            "superagent": superagent_id,
            "domain": domain,
            "proof_path": proof_path
        })

    folder_superagents = []
    for folder in sorted(top_level_dirs):
        folder_superagents.append({
            "id": f"folder_superagent_{slugify(folder)}",
            "folder": folder
        })

    registry = {
        "version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": root.as_posix(),
        "files": sorted(files, key=lambda item: item["file"]),
        "folder_superagents": folder_superagents
    }

    if args.write:
        output_path = root / args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as handle:
            json.dump(registry, handle, indent=2, sort_keys=False)
        print(f"Registry written to {output_path}")
    else:
        print(json.dumps(registry, indent=2, sort_keys=False))


if __name__ == "__main__":
    main()
