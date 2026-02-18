#!/usr/bin/env python3
import argparse
import json
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

METHOD_PATTERN = re.compile(r"method\s*:\s*['\"](GET|POST|PUT|DELETE|PATCH)['\"]", re.IGNORECASE)


def should_ignore(path: Path) -> bool:
    return any(part in IGNORE_DIRS for part in path.parts)


def normalize_path(path: str) -> str:
    cleaned = path.split("?")[0].split("#")[0]
    cleaned = re.sub(r"\$\{[^}]+\}", ":param", cleaned)
    cleaned = re.sub(r":([a-zA-Z0-9_]+)", ":param", cleaned)
    return cleaned


def extract_api_calls(content: str) -> List[Tuple[str, str]]:
    calls = []
    token_pattern = re.compile(r"\b(api|fetch)\b", re.MULTILINE)

    for match in token_pattern.finditer(content):
        token = match.group(1)
        pos = match.end()

        while pos < len(content) and content[pos].isspace():
            pos += 1

        if token == "api" and pos < len(content) and content[pos] == "<":
            depth = 0
            while pos < len(content):
                ch = content[pos]
                if ch == "<":
                    depth += 1
                elif ch == ">":
                    depth -= 1
                    if depth == 0:
                        pos += 1
                        break
                pos += 1

            while pos < len(content) and content[pos].isspace():
                pos += 1

        if pos >= len(content) or content[pos] != "(":
            continue

        start = match.start()
        pos += 1
        depth = 1
        in_string = None
        escaped = False
        while pos < len(content) and depth > 0:
            ch = content[pos]
            if in_string:
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == in_string:
                    in_string = None
            else:
                if ch in ("'", "\"", "`"):
                    in_string = ch
                elif ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
            pos += 1

        call_text = content[start:pos]
        path_match = re.search(r"([`'\"])(?:\$\{API_BASE_URL\})?(/api/v1/[^`'\"]+)\1", call_text)
        if not path_match:
            continue
        path = path_match.group(2)
        method_match = METHOD_PATTERN.search(call_text)
        method = method_match.group(1).upper() if method_match else "GET"
        calls.append((method, path))

    return calls


def load_contract(contract_path: Path) -> Dict[str, List[Dict[str, str]]]:
    with contract_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_contract_set(contract: Dict[str, List[Dict[str, str]]]) -> Dict[Tuple[str, str], Dict[str, str]]:
    endpoints = {}
    for endpoint in contract.get("endpoints", []):
        method = endpoint.get("method", "GET").upper()
        path = endpoint.get("path", "")
        norm = normalize_path(path)
        endpoints[(method, norm)] = endpoint
    return endpoints


def generate_contract_entries(calls: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    unique = {}
    for method, path in calls:
        norm = normalize_path(path)
        unique[(method.upper(), norm)] = path
    entries = []
    for (method, norm) in sorted(unique.keys()):
        raw_path = unique[(method, norm)]
        endpoint_id = re.sub(r"[^a-zA-Z0-9]+", "_", f"{method}_{raw_path}").strip("_").lower()
        entries.append({"id": endpoint_id, "method": method, "path": norm})
    return entries


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit frontend API usage against contract list.")
    parser.add_argument("--root", default=None, help="Project root (default: repo root).")
    parser.add_argument("--contract", default="agents/contracts/api_endpoints.json", help="Contract path.")
    parser.add_argument("--write", action="store_true", help="Write contract file from current usage.")
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    contract_path = root / args.contract

    calls = []
    for file_path in root.rglob("*"):
        if file_path.suffix not in FILE_EXTENSIONS:
            continue
        if should_ignore(file_path):
            continue
        content = file_path.read_text(encoding="utf-8")
        calls.extend(extract_api_calls(content))

    if args.write:
        entries = generate_contract_entries(calls)
        contract = {
            "version": "1.0",
            "base_url_env": "NEXT_PUBLIC_API_URL",
            "endpoints": entries
        }
        contract_path.parent.mkdir(parents=True, exist_ok=True)
        with contract_path.open("w", encoding="utf-8") as handle:
            json.dump(contract, handle, indent=2, sort_keys=False)
        print(f"Contract written to {contract_path}")
        return

    if not contract_path.exists():
        raise SystemExit(f"Contract not found: {contract_path}")

    contract = load_contract(contract_path)
    contract_set = build_contract_set(contract)

    used = {}
    for method, path in calls:
        norm = normalize_path(path)
        used[(method.upper(), norm)] = path

    missing = []
    for key, raw_path in sorted(used.items()):
        if key not in contract_set:
            missing.append((key[0], raw_path))

    extras = []
    for key, endpoint in contract_set.items():
        if key not in used:
            extras.append((endpoint.get("method", "GET"), endpoint.get("path", "")))

    if missing or extras:
        if missing:
            print("Missing from contract:")
            for method, path in missing:
                print(f"- {method} {path}")
        if extras:
            print("Contract entries not used in code:")
            for method, path in extras:
                print(f"- {method} {path}")
        raise SystemExit(1)

    print(f"API contract audit passed. Endpoints checked: {len(used)}")


if __name__ == "__main__":
    main()
