#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import urllib.request
import urllib.error


DEFAULT_FILE_PROMPT = (
    "You are the file master agent for an enterprise DApp platform. Review the file for:\\n"
    "- broken or missing routes/CTAs\\n"
    "- missing API endpoints or contract mismatches\\n"
    "- placeholders, mock data, or TODOs blocking production\\n"
    "- security issues (secrets, auth gaps, validation, unsafe eval)\\n"
    "- production readiness gaps\\n\\n"
    "Return JSON ONLY with this schema:\\n"
    "{\\n"
    "  \\\"status\\\": \\\"pass\\\" | \\\"fail\\\",\\n"
    "  \\\"changes\\\": [\\\"required change\\\", ...],\\n"
    "  \\\"checks\\\": [\\\"cta\\\", \\\"api\\\", \\\"security\\\", \\\"data\\\", \\\"config\\\"],\\n"
    "  \\\"notes\\\": \\\"short summary\\\"\\n"
    "}\\n\\n"
    "Rules:\\n"
    "- If you are unsure, set status to \\\"fail\\\" and list the missing change.\\n"
    "- Keep changes concrete and actionable.\\n"
    "- Do not include markdown or extra text."
)

DEFAULT_SUPERVISOR_PROMPT = (
    "You are the master supervisor agent. You receive a summary of file-level audits and static checks.\\n"
    "Return JSON ONLY with this schema:\\n"
    "{\\n"
    "  \\\"status\\\": \\\"pass\\\" | \\\"fail\\\",\\n"
    "  \\\"notes\\\": \\\"short summary\\\",\\n"
    "  \\\"required_actions\\\": [\\\"action\\\", ...]\\n"
    "}\\n\\n"
    "Rules:\\n"
    "- Return \\\"pass\\\" only if all file audits and static checks passed.\\n"
    "- Keep required_actions empty on pass.\\n"
    "- Do not include markdown or extra text."
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_text(path: Optional[Path], fallback: str) -> str:
    if path and path.exists():
        return path.read_text(encoding="utf-8")
    return fallback


def run_script(root: Path, script_rel: str, args: Optional[List[str]] = None) -> Tuple[bool, str]:
    script_path = root / script_rel
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
    result = subprocess.run(cmd, cwd=root, capture_output=True, text=True, check=False)
    output = (result.stdout or "") + (result.stderr or "")
    return result.returncode == 0, output.strip()


def ensure_registry(root: Path, registry_path: Path) -> None:
    if registry_path.exists():
        return
    ok, output = run_script(root, "scripts/agent_dispatch.py", ["--write", "--root", str(root)])
    if not ok:
        raise RuntimeError(f"Failed to generate registry: {output}")


def load_registry(registry_path: Path) -> Dict[str, Any]:
    with registry_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def get_targets(root: Path, registry: Dict[str, Any], targets: str, use_git: bool) -> List[str]:
    if targets:
        return [item.strip() for item in targets.split(",") if item.strip()]
    if use_git:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return []
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return [entry["file"] for entry in registry.get("files", [])]


def call_anthropic(api_key: str, model: str, system_prompt: str, user_prompt: str) -> str:
    payload = {
        "model": model,
        "max_tokens": 600,
        "temperature": 0.2,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}],
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=data,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            response_data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Anthropic HTTP error: {exc.code} {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Anthropic connection error: {exc}") from exc

    content_blocks = response_data.get("content", [])
    text = ""
    for block in content_blocks:
        if isinstance(block, dict) and block.get("type") == "text":
            text += block.get("text", "")
    return text.strip()


def extract_json(text: str) -> Dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise


def safe_read_text(path: Path, max_chars: int) -> Tuple[Optional[str], bool]:
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None, False
    truncated = False
    if len(content) > max_chars:
        content = content[:max_chars]
        truncated = True
    return content, truncated


def normalize_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if value is None:
        return []
    return [str(value)]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run AI file-level audits with supervisor verification.")
    parser.add_argument("--root", default=None, help="Project root (default: repo root).")
    parser.add_argument("--registry", default="agents/registry.json", help="Registry path.")
    parser.add_argument("--targets", default="", help="Comma-separated file targets.")
    parser.add_argument("--use-git", action="store_true", help="Use git diff to infer targets.")
    parser.add_argument("--proof-dir", default="audit/proofs/files", help="Output directory for file proofs.")
    parser.add_argument("--workflow-proof", default="audit/proofs/workflows/verification.json", help="Workflow proof path.")
    parser.add_argument("--file-prompt", default="agents/prompts/file_audit_system.md", help="File audit prompt.")
    parser.add_argument("--supervisor-prompt", default="agents/prompts/supervisor_verification.md", help="Supervisor prompt.")
    parser.add_argument("--model", default="", help="Anthropic model for file audits.")
    parser.add_argument("--supervisor-model", default="", help="Anthropic model for supervisor.")
    parser.add_argument("--max-chars", type=int, default=20000, help="Max chars per file sent to AI.")
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    registry_path = root / args.registry
    ensure_registry(root, registry_path)
    registry = load_registry(registry_path)
    registry_index = {entry["file"]: entry for entry in registry.get("files", [])}

    targets = get_targets(root, registry, args.targets, args.use_git)
    if not targets:
        print("No targets to audit.")
        return

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("ANTHROPIC_API_KEY is required for AI pipeline.")

    model = args.model or os.getenv("OPTIK_AI_FILE_MODEL") or os.getenv("OPTIK_ASSISTANT_MODEL_ACCURATE") or "claude-3-sonnet-20240229"
    supervisor_model = args.supervisor_model or os.getenv("OPTIK_AI_SUPERVISOR_MODEL") or model

    file_prompt = load_text(root / args.file_prompt, DEFAULT_FILE_PROMPT)
    supervisor_prompt = load_text(root / args.supervisor_prompt, DEFAULT_SUPERVISOR_PROMPT)

    links_ok, links_output = run_script(root, "scripts/cta_route_audit.py")
    api_ok, api_output = run_script(root, "scripts/api_contract_audit.py")
    if not links_ok or not api_ok:
        print(links_output)
        print(api_output)
        raise SystemExit("Static audits failed.")

    proof_dir = root / args.proof_dir
    proof_dir.mkdir(parents=True, exist_ok=True)

    results = []
    failed_files = []
    skipped_files = []

    for target in targets:
        entry = registry_index.get(target)
        if not entry:
            raise SystemExit(f"File not found in registry: {target}")
        file_path = (root / target).resolve()
        if not file_path.exists():
            continue

        content, truncated = safe_read_text(file_path, args.max_chars)
        if content is None:
            skipped_files.append(target)
            proof = {
                "type": "file",
                "file": target,
                "owner_agent": entry.get("agent_id", ""),
                "changes": [],
                "checks": ["binary-skip"],
                "links_ok": links_ok,
                "api_ok": api_ok,
                "timestamp": now_iso(),
            }
            proof_path = root / entry.get("proof_path", f"audit/proofs/files/{target}.json")
            proof_path.parent.mkdir(parents=True, exist_ok=True)
            proof_path.write_text(json.dumps(proof, indent=2, sort_keys=False), encoding="utf-8")
            results.append({"file": target, "status": "pass", "changes": []})
            continue

        user_prompt = f"File: {target}\\nTruncated: {truncated}\\n\\n{content}"
        ai_text = call_anthropic(api_key, model, file_prompt, user_prompt)
        try:
            ai_data = extract_json(ai_text)
        except Exception as exc:
            ai_data = {"status": "fail", "changes": [f"AI response parse failure: {exc}"], "checks": ["ai_review"], "notes": ""}

        status = str(ai_data.get("status", "fail")).lower()
        changes = normalize_list(ai_data.get("changes"))
        checks = normalize_list(ai_data.get("checks")) or ["ai_review"]
        notes = str(ai_data.get("notes", ""))

        passed = status == "pass" and not changes
        if not passed:
            failed_files.append(target)

        proof = {
            "type": "file",
            "file": target,
            "owner_agent": entry.get("agent_id", ""),
            "changes": changes,
            "checks": checks,
            "links_ok": links_ok,
            "api_ok": api_ok,
            "timestamp": now_iso(),
        }
        proof_path = root / entry.get("proof_path", f"audit/proofs/files/{target}.json")
        proof_path.parent.mkdir(parents=True, exist_ok=True)
        proof_path.write_text(json.dumps(proof, indent=2, sort_keys=False), encoding="utf-8")
        results.append({"file": target, "status": "pass" if passed else "fail", "changes": changes, "notes": notes})

    summary = {
        "files_reviewed": len(results),
        "files_failed": len(failed_files),
        "files_skipped": len(skipped_files),
        "failed_files": failed_files,
        "links_ok": links_ok,
        "api_ok": api_ok,
    }
    supervisor_user = json.dumps(summary, indent=2, sort_keys=False)
    supervisor_text = call_anthropic(api_key, supervisor_model, supervisor_prompt, supervisor_user)
    supervisor_data = extract_json(supervisor_text)
    supervisor_status = str(supervisor_data.get("status", "fail")).lower()
    supervisor_notes = str(supervisor_data.get("notes", ""))
    required_actions = normalize_list(supervisor_data.get("required_actions"))

    workflow_steps = [
        {"id": "cta_audit", "status": "pass" if links_ok else "fail"},
        {"id": "api_contract_audit", "status": "pass" if api_ok else "fail"},
        {
            "id": "file_ai_review",
            "status": "pass" if not failed_files else "fail",
            "files_reviewed": len(results),
            "files_failed": len(failed_files),
        },
        {"id": "supervisor_verification", "status": "pass" if supervisor_status == "pass" else "fail"},
    ]

    workflow_proof = {
        "type": "workflow",
        "workflow_id": "ai_file_audit_v1",
        "status": "pass" if supervisor_status == "pass" else "fail",
        "steps": workflow_steps,
        "artifacts": {
            "summary": summary,
            "supervisor_notes": supervisor_notes,
            "required_actions": required_actions,
            "proof_dir": args.proof_dir,
            "workflow_proof": args.workflow_proof,
        },
        "timestamp": now_iso(),
    }

    workflow_path = root / args.workflow_proof
    workflow_path.parent.mkdir(parents=True, exist_ok=True)
    workflow_path.write_text(json.dumps(workflow_proof, indent=2, sort_keys=False), encoding="utf-8")

    if failed_files or supervisor_status != "pass":
        raise SystemExit("AI pipeline failed.")

    print(f"AI pipeline passed. Files reviewed: {len(results)}")


if __name__ == "__main__":
    main()
