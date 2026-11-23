from pathlib import Path

from agent.security_review import format_report, run_review

ROOT = Path(__file__).resolve().parent.parent


def _checks(findings):
    return {f["check"] for f in findings}


def test_flags_insecure_directory(tmp_path):
    (tmp_path / ".env").write_text("SECRET=1")
    # Assembled so this test file never contains a literal secret-shaped string.
    fake_aws_key = "AKIA" + "IOSFODNN7EXAMPLE"
    (tmp_path / "config.py").write_text(f'key = "{fake_aws_key}"')
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "ci.yml").write_text(
        "on: pull_request_target\njobs:\n  b:\n    steps:\n      - uses: someorg/some-action@v1\n"
    )

    checks = _checks(run_review(str(tmp_path)))

    assert {
        "not-a-git-repo",
        "sensitive-file",
        "possible-secret",
        "gitignore-gap",
        "workflow-permissions",
        "dangerous-trigger",
        "unpinned-action",
        "no-ci-secret-scan",
        "no-dependabot",
    } <= checks


def test_clean_directory_reports_nothing_actionable(tmp_path):
    (tmp_path / ".gitignore").write_text(".env\n__pycache__/\n")
    (tmp_path / "main.py").write_text("print('hello')\n")
    findings = [f for f in run_review(str(tmp_path)) if f["severity"] != "info"]
    assert findings == []


def test_own_repo_has_no_critical_or_high_findings():
    findings = [f for f in run_review(str(ROOT)) if f["severity"] in ("critical", "high")]
    assert findings == [], format_report(findings)


def test_format_report_orders_by_severity_and_handles_empty():
    assert format_report([]) == "No security findings."
    report = format_report(
        [
            {"severity": "low", "check": "a", "detail": "d", "location": ""},
            {"severity": "critical", "check": "b", "detail": "d", "location": "f.py"},
        ]
    )
    assert report.splitlines()[0] == "[critical] b: d (f.py)"
