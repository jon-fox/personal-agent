"""Structural checks that keep skills consistent with the conventions in AGENTS.md."""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
SKILLS = sorted(p.parent for p in SKILLS_DIR.glob("*/SKILL.md"))
REAL_SKILLS = [p for p in SKILLS if p.name != "_template"]
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


def _frontmatter(skill_md: Path) -> dict[str, str]:
    match = re.match(r"---\n(.*?)\n---\n", skill_md.read_text(), re.DOTALL)
    assert match, f"{skill_md} is missing YAML frontmatter"
    fields = {}
    for line in match.group(1).splitlines():
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields


@pytest.mark.parametrize("skill", SKILLS, ids=lambda p: p.name)
def test_frontmatter_has_name_and_description(skill):
    fields = _frontmatter(skill / "SKILL.md")
    assert fields.get("description")
    if skill.name != "_template":
        assert fields.get("name") == skill.name


@pytest.mark.parametrize("skill", SKILLS, ids=lambda p: p.name)
def test_skill_files_contain_no_email_addresses(skill):
    for path in skill.rglob("*"):
        if path.is_file():
            assert not EMAIL.search(path.read_text()), f"email address in {path}"


@pytest.mark.parametrize("skill", REAL_SKILLS, ids=lambda p: p.name)
def test_skill_is_listed_in_agents_md_and_readme(skill):
    for doc in ("AGENTS.md", "README.md"):
        assert f"`{skill.name}`" in (ROOT / doc).read_text() or (
            f"**{skill.name}**" in (ROOT / doc).read_text()
        ), f"{skill.name} missing from {doc}"


def test_claude_skill_links_resolve_to_portable_skills():
    for link in (ROOT / ".claude" / "skills").iterdir():
        assert (link / "SKILL.md").is_file(), f"{link} does not point at a skill"


@pytest.mark.parametrize("skill", SKILLS, ids=lambda p: p.name)
def test_skill_treats_external_content_as_untrusted(skill):
    body = (skill / "SKILL.md").read_text().lower()
    assert "untrusted" in body, f"{skill.name} must state that external content is untrusted"
