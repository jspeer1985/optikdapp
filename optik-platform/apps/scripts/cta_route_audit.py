#!/usr/bin/env python3
import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple

FILE_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx"}

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

PLACEHOLDER_TARGETS = {"#", "", "/#"}


def should_ignore(path: Path) -> bool:
    return any(part in IGNORE_DIRS for part in path.parts)


def collect_routes(app_dir: Path) -> List[str]:
    routes = []
    for page_file in app_dir.rglob("page.*"):
        if should_ignore(page_file):
            continue
        rel_path = page_file.relative_to(app_dir)
        segments = list(rel_path.parts[:-1])
        url_segments = []
        for segment in segments:
            if segment.startswith("(") and segment.endswith(")"):
                continue
            if segment.startswith("@"):
                continue
            if segment.startswith("[[...") and segment.endswith("]]"):
                url_segments.append("*")
                continue
            if segment.startswith("[...") and segment.endswith("]"):
                url_segments.append("*")
                continue
            if segment.startswith("[") and segment.endswith("]"):
                url_segments.append(":param")
                continue
            url_segments.append(segment)
        route = "/" + "/".join(url_segments)
        routes.append(route if route != "" else "/")
    return sorted(set(routes))


def route_to_regex(route: str) -> re.Pattern:
    if route == "/":
        return re.compile(r"^/$")
    escaped = re.escape(route)
    escaped = escaped.replace(r"\:param", r"[^/]+")
    escaped = escaped.replace(r"\*", r".+")
    return re.compile(r"^" + escaped.rstrip("/") + r"/?$")


def parse_targets(file_path: Path) -> List[Tuple[int, str]]:
    targets = []
    with file_path.open("r", encoding="utf-8") as handle:
        for idx, line in enumerate(handle, start=1):
            for match in re.finditer(r"href\s*=\s*\{?['\"]([^'\"]+)['\"]\}?", line):
                targets.append((idx, match.group(1)))
            for match in re.finditer(r"router\.(push|replace|prefetch)\(\s*['\"]([^'\"]+)['\"]", line):
                targets.append((idx, match.group(2)))
    return targets


def normalize_path(path: str) -> str:
    if path.startswith("http://") or path.startswith("https://"):
        return ""
    if path.startswith("mailto:") or path.startswith("tel:"):
        return ""
    if path.startswith("javascript:"):
        return "__placeholder__"
    if not path.startswith("/"):
        return ""
    cleaned = path.split("?")[0].split("#")[0]
    return cleaned


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit internal CTAs against Next routes.")
    parser.add_argument("--root", default=None, help="Project root (default: repo root).")
    parser.add_argument("--app-dir", default="app", help="Next app directory.")
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    app_dir = root / args.app_dir
    routes = collect_routes(app_dir)
    route_regexes = [route_to_regex(route) for route in routes]

    missing = []
    placeholders = []
    checked = 0

    for file_path in root.rglob("*"):
        if file_path.suffix not in FILE_EXTENSIONS:
            continue
        if should_ignore(file_path):
            continue
        targets = parse_targets(file_path)
        if not targets:
            continue
        for line_no, target in targets:
            normalized = normalize_path(target)
            if normalized == "":
                continue
            checked += 1
            if normalized == "__placeholder__" or normalized in PLACEHOLDER_TARGETS:
                placeholders.append((file_path, line_no, target))
                continue
            if not any(regex.match(normalized) for regex in route_regexes):
                missing.append((file_path, line_no, target))

    if missing or placeholders:
        if placeholders:
            print("Placeholder CTA targets:")
            for path, line_no, target in placeholders:
                print(f"- {path}:{line_no} -> {target}")
        if missing:
            print("Missing CTA routes:")
            for path, line_no, target in missing:
                print(f"- {path}:{line_no} -> {target}")
        raise SystemExit(1)

    print(f"CTA audit passed. Targets checked: {checked}")


if __name__ == "__main__":
    main()
