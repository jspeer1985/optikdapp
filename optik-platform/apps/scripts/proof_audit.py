#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_schema(root: Path, schema_path: str) -> Dict[str, Any]:
    path = root / schema_path
    if not path.exists():
        raise FileNotFoundError(f"Schema not found: {path}")
    return load_json(path)


def collect_proofs(proof_dir: Path) -> List[Path]:
    if not proof_dir.exists():
        return []
    return sorted([p for p in proof_dir.rglob("*.json") if p.is_file()])


def get_targets_from_git(root: Path) -> List[str]:
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return []
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def validate_proof(proof: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    errors = []
    proof_type = proof.get("type")
    if proof_type == schema.get("file_proof", {}).get("type"):
        required = schema.get("file_proof", {}).get("required", [])
    elif proof_type == schema.get("workflow_proof", {}).get("type"):
        required = schema.get("workflow_proof", {}).get("required", [])
    else:
        return [f"Unknown proof type: {proof_type}"]

    for key in required:
        if key not in proof:
            errors.append(f"Missing field: {key}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit proof-of-completion artifacts.")
    parser.add_argument("--root", default=None, help="Project root (default: repo root).")
    parser.add_argument("--schema", default="agents/proofs/schema.json", help="Schema path.")
    parser.add_argument("--proof-dir", default="audit/proofs", help="Proof directory.")
    parser.add_argument("--targets", default="", help="Comma-separated file targets.")
    parser.add_argument("--use-git", action="store_true", help="Use git diff to infer targets.")
    parser.add_argument("--strict-registry", action="store_true", help="Require proofs for all registry files.")
    parser.add_argument("--registry", default="agents/registry.json", help="Registry path.")
    parser.add_argument("--workflow", default="", help="Workflow file with proof bundle requirements.")
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    schema = load_schema(root, args.schema)

    proof_dir = root / args.proof_dir
    proof_files = collect_proofs(proof_dir)
    proofs = []
    errors = []

    for proof_file in proof_files:
        try:
            proof = load_json(proof_file)
            proof_errors = validate_proof(proof, schema)
            if proof_errors:
                errors.append(f"{proof_file}: {', '.join(proof_errors)}")
            proofs.append(proof)
        except Exception as exc:
            errors.append(f"{proof_file}: {exc}")

    targets = []
    if args.targets:
        targets = [t.strip() for t in args.targets.split(",") if t.strip()]
    elif args.use_git:
        targets = get_targets_from_git(root)

    if args.strict_registry:
        registry_path = root / args.registry
        if registry_path.exists():
            registry = load_json(registry_path)
            targets = [entry["file"] for entry in registry.get("files", [])]

    if targets:
        proof_index = {}
        for proof in proofs:
            if proof.get("type") == "file" and proof.get("file"):
                proof_index[proof["file"]] = proof

        for target in targets:
            if target not in proof_index:
                errors.append(f"Missing proof for file: {target}")

    if args.workflow:
        workflow_path = root / args.workflow
        if workflow_path.exists():
            workflow = load_json(workflow_path)
            required_artifacts = workflow.get("proof_bundle", {}).get("required_artifacts", [])
            for artifact in required_artifacts:
                artifact_path = root / artifact
                if not artifact_path.exists():
                    errors.append(f"Missing workflow artifact: {artifact}")
        else:
            errors.append(f"Workflow file not found: {workflow_path}")

    if errors:
        print("Proof audit failed:")
        for item in errors:
            print(f"- {item}")
        raise SystemExit(1)

    print(f"Proof audit passed. Proof files checked: {len(proof_files)}")


if __name__ == "__main__":
    main()
