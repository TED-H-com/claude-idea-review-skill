import yaml
from pathlib import Path

def test_skill_md_frontmatter():
    skill_file = Path("SKILL.md")
    assert skill_file.exists(), "SKILL.md should exist in the root directory."

    content = skill_file.read_text(encoding="utf-8")

    # Check that it starts with YAML frontmatter
    assert content.startswith("---"), "SKILL.md should start with '---'"

    parts = content.split("---", 2)
    assert len(parts) >= 3, "SKILL.md should contain valid YAML frontmatter blocks separated by '---'"

    frontmatter_text = parts[1]
    metadata = yaml.safe_load(frontmatter_text)

    assert isinstance(metadata, dict), "Frontmatter should be a dictionary"
    assert "name" in metadata, "Frontmatter should contain 'name'"
    assert "description" in metadata, "Frontmatter should contain 'description'"
    assert metadata["name"] == "idea-review-panel", "Name should be idea-review-panel"
