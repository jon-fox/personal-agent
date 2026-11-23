"""Read-only repository security review: the hardening checks this repo applies to itself."""

import argparse
import re
import subprocess
from pathlib import Path

SENSITIVE_PATH = re.compile(r"(^|/)(\.env[^/]*|[^/]*\.(pem|key|p12|pfx)|id_rsa[^/]*|[^/]*\.pyc|\.DS_Store)$")
SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "AWS access key ID": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    "Slack token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
}
USES_REF = re.compile(r"^\s*-?\s*uses:\s*([\w.-]+/[\w./-]+)@([\w.-]+)", re.MULTILINE)
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__"}
MAX_SCAN_BYTES = 1_000_000


def _finding(severity: str, check: str, detail: str, location: str = "") -> dict:
    return {"severity": severity, "check": check, "detail": detail, "location": location}


def _tracked_files(repo: Path) -> list[Path] | None:
    try:
        out = subprocess.run(
            ["git", "ls-files"], cwd=repo, capture_output=True, text=True, check=True, timeout=30
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return [repo / line for line in out.stdout.splitlines() if line and (repo / line).is_file()]


def run_review(path: str = ".") -> list[dict]:
    repo = Path(path).resolve()
    findings: list[dict] = []

    files = _tracked_files(repo)
    if files is None:
        files = [p for p in repo.rglob("*") if p.is_file() and not any(part in SKIP_DIRS for part in p.parts)]
        findings.append(
            _finding(
                "info", "not-a-git-repo", "not a git repository; scanned all files instead of tracked ones"
            )
        )

    for f in files:
        rel = f.relative_to(repo).as_posix()
        if SENSITIVE_PATH.search(rel):
            findings.append(_finding("high", "sensitive-file", "sensitive file should not be committed", rel))
        if f.stat().st_size > MAX_SCAN_BYTES:
            continue
        try:
            text = f.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                findings.append(
                    _finding("critical", "possible-secret", f"possible {name} in file contents", rel)
                )

    gitignore = repo / ".gitignore"
    ignored = gitignore.read_text() if gitignore.is_file() else ""
    for needed in (".env", "__pycache__"):
        if needed not in ignored:
            findings.append(_finding("medium", "gitignore-gap", f"{needed} is not covered by .gitignore"))

    workflows_dir = repo / ".github" / "workflows"
    workflows = sorted(workflows_dir.glob("*.yml")) + sorted(workflows_dir.glob("*.yaml"))
    ci_has_secret_scan = False
    for wf in workflows:
        rel = wf.relative_to(repo).as_posix()
        text = wf.read_text()
        if "permissions:" not in text:
            findings.append(
                _finding(
                    "medium",
                    "workflow-permissions",
                    "no permissions block; token gets broad default grants",
                    rel,
                )
            )
        if "pull_request_target" in text:
            findings.append(
                _finding(
                    "high", "dangerous-trigger", "pull_request_target runs with secrets on untrusted PRs", rel
                )
            )
        for match in USES_REF.finditer(text):
            action, ref = match.groups()
            if not SHA40.match(ref) and not action.startswith("actions/"):
                findings.append(
                    _finding(
                        "medium", "unpinned-action", f"{action}@{ref} is not pinned to a commit SHA", rel
                    )
                )
        if re.search(r"gitleaks|trufflehog", text, re.IGNORECASE):
            ci_has_secret_scan = True
    if workflows and not ci_has_secret_scan:
        findings.append(_finding("low", "no-ci-secret-scan", "no secret-scanning job found in CI workflows"))
    if workflows and not (repo / ".github" / "dependabot.yml").is_file():
        findings.append(_finding("low", "no-dependabot", "no Dependabot config; dependencies will go stale"))

    return findings


def format_report(findings: list[dict]) -> str:
    if not findings:
        return "No security findings."
    order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    lines = []
    for f in sorted(findings, key=lambda f: order.get(f["severity"], 9)):
        location = f" ({f['location']})" if f["location"] else ""
        lines.append(f"[{f['severity']}] {f['check']}: {f['detail']}{location}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "path", nargs="?", default=".", help="repository to review (default: current directory)"
    )
    args = parser.parse_args()
    findings = run_review(args.path)
    print(format_report(findings))
    if any(f["severity"] in ("critical", "high") for f in findings):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
