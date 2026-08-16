#!/usr/bin/env python3
# SCRIPT-METADATA:
# name: make_reviewer
# description: Generate a model-tiered reviewer subagent TOML, register it in config.toml, and wire it into the system prompt, README, and review skill tier tables
# tags: config,reviewer,subagent

"""Generate a model-tiered reviewer subagent and wire it everywhere.

Each reviewer shares one prompt (prompts/reviewer.md) but runs on a different
model. Vibe CLI binds a subagent's model at config time, so model diversity
requires separate agent TOMLs. This script:

  1. Stamps agents/reviewer-<suffix>.toml from the canonical template.
  2. Registers the agent in config.toml's [tools.task] allowlist.
  3. Updates the tier tables in the system prompt, README, and review skill.
  4. Adds a generic delegation/agents/subagents table row.

Tier semantics:
  - Default (no flags): deep-only. The reviewer appears only in the Deep tier.
    Deep = Standard + sol, so a deep-only reviewer appends to the Deep row.
  - --standard: also add to Standard. Deep inherits Standard, so the Deep row
    is unchanged (the reviewer is in Deep via Standard).
  - --quick: also add to the Quick set.

Usage:
    make_reviewer.py <model-alias> <suffix> [--quick] [--standard] [--dry-run] [--force]

Examples:
    make_reviewer.py gpt-5.6-sol sol
        -> deep-only reviewer on gpt-5.6-sol
    make_reviewer.py claude-opus opus --quick --standard
        -> reviewer on claude-opus, in quick + standard + deep (via inheritance)
    make_reviewer.py mistral-small-latest small --dry-run
        -> preview only, write nothing

The <model-alias> must exist as an `alias` in config.toml's [[models]].
The <suffix> becomes the agent name: reviewer-<suffix>.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    sys.exit("error: this script requires Python 3.11+ (tomllib).")

VIBE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = VIBE_DIR / "config.toml"
TEMPLATE_PATH = VIBE_DIR / "agents" / "reviewer-deepseek.toml"
AGENTS_DIR = VIBE_DIR / "agents"
SYSTEM_PROMPT_PATH = VIBE_DIR / "prompts" / "system-prompt-large.md"
README_PATH = VIBE_DIR / "README.md"
SKILL_PATH = VIBE_DIR / "skills" / "review" / "SKILL.md"


# -- config.toml -------------------------------------------------------------

def load_model_aliases() -> dict[str, str]:
    """Return {alias: model_name} from config.toml's [[models]]."""
    with open(CONFIG_PATH, "rb") as fh:
        cfg = tomllib.load(fh)
    aliases: dict[str, str] = {}
    for model in cfg.get("models", []):
        alias = model.get("alias")
        if alias:
            aliases[alias] = model.get("name", alias)
    return aliases


def register_in_allowlist(agent_name: str) -> str:
    """Insert agent_name into config.toml's [tools.task] allowlist if absent.

    Returns the (possibly modified) config text. Idempotent.
    """
    text = CONFIG_PATH.read_text()

    section_match = re.search(r"^\[tools\.task\]\s*$", text, flags=re.MULTILINE)
    if not section_match:
        sys.exit("error: [tools.task] section not found in config.toml")
    section_start = section_match.end()

    allow_match = re.search(r"allowlist\s*=\s*\[", text[section_start:])
    if not allow_match:
        sys.exit("error: allowlist not found in [tools.task] section")
    allow_start = section_start + allow_match.end()

    bracket_depth = 1
    i = allow_start
    while i < len(text) and bracket_depth > 0:
        if text[i] == "[":
            bracket_depth += 1
        elif text[i] == "]":
            bracket_depth -= 1
        i += 1
    if bracket_depth != 0:
        sys.exit("error: unmatched brackets in [tools.task] allowlist")
    allow_body = text[allow_start : i - 1]

    if re.search(rf'"{re.escape(agent_name)}"\s*,?', allow_body):
        return text

    entry_match = re.search(r"^(\s*)\"\w+\"", allow_body, flags=re.MULTILINE)
    indent = entry_match.group(1) if entry_match else "    "

    insertion = f"\n{indent}\"{agent_name}\","
    return text[:allow_start] + insertion + text[allow_start:]


# -- agent TOML --------------------------------------------------------------

def stamp_template(alias: str, suffix: str, model_name: str) -> str:
    """Read the canonical reviewer TOML and swap the three model-specific fields."""
    if not TEMPLATE_PATH.exists():
        sys.exit(f"error: template not found: {TEMPLATE_PATH}")
    text = TEMPLATE_PATH.read_text()

    display = f"Reviewer ({suffix.capitalize()})"
    description = (
        f"Independent artifact reviewer on {model_name}; "
        "read-only review of code, docs, specs, plans"
    )

    def replace_field(body: str, field: str, value: str) -> str:
        pattern = rf'^({field}\s*=\s*)"[^"]*"\s*$'
        repl = lambda m: f'{m.group(1)}"{value}"'
        new, n = re.subn(pattern, repl, body, count=1, flags=re.MULTILINE)
        if n != 1:
            sys.exit(f"error: could not find {field!r} in template {TEMPLATE_PATH}")
        return new

    text = replace_field(text, "display_name", display)
    text = replace_field(text, "description", description)
    text = replace_field(text, "active_model", alias)
    return text


# -- tier tables (system prompt, README, skill) ------------------------------

def _find_tier_line(lines: list[str], keyword: str) -> int:
    """Return index of the tier table row whose first cell contains keyword."""
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = stripped.split("|")
        if len(cells) < 4:
            continue
        if keyword in cells[1] and "reviewer-" in line:
            return i
    return -1


def _append_to_composition(line: str, agent_name: str) -> str:
    """Append ' + agent_name' after the last reviewer-xxx before the trailing |."""
    return re.sub(
        r"(reviewer-\w+)(\s*\|\s*)$",
        r"\1 + " + agent_name + r"\2",
        line,
        count=1,
    )


def edit_tier_table(
    text: str, agent_name: str, quick: bool, standard: bool
) -> tuple[str, list[str]]:
    """Edit the Quick/Standard/Deep rows' Composition cells.

    Returns (new_text, list_of_changes).
    """
    lines = text.split("\n")
    changes: list[str] = []

    quick_i = _find_tier_line(lines, "Quick")
    if quick_i >= 0 and quick and agent_name not in lines[quick_i]:
        line = lines[quick_i]
        if "}" in line:
            lines[quick_i] = line.replace("}", ", " + agent_name + "}", 1)
            changes.append("quick")
        else:
            sys.exit(f"error: Quick tier row has no set notation: {line!r}")

    std_i = _find_tier_line(lines, "Standard")
    if std_i >= 0 and standard and agent_name not in lines[std_i]:
        lines[std_i] = _append_to_composition(lines[std_i], agent_name)
        changes.append("standard")

    deep_i = _find_tier_line(lines, "Deep")
    if deep_i >= 0 and not standard and agent_name not in lines[deep_i]:
        lines[deep_i] = _append_to_composition(lines[deep_i], agent_name)
        changes.append("deep")

    if quick_i < 0 or std_i < 0 or deep_i < 0:
        missing = []
        if quick_i < 0:
            missing.append("Quick")
        if std_i < 0:
            missing.append("Standard")
        if deep_i < 0:
            missing.append("Deep")
        sys.exit(
            f"error: tier row(s) not found: {', '.join(missing)} "
            f"(file may have been hand-edited)"
        )

    return "\n".join(lines), changes


# -- delegation / agents / subagents table rows ------------------------------

def add_row_after(
    text: str, anchor_pattern: str, new_row: str, exists_check: str, label: str
) -> tuple[str, bool]:
    """Insert new_row after the first line matching anchor_pattern.

    Idempotent: if exists_check is found in text, returns (text, False).
    Use a table-specific check (e.g. backtick-wrapped name, or `| name |`)
    to avoid false positives from other tables in the same file.
    """
    if exists_check in text:
        return text, False
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if re.search(anchor_pattern, line):
            lines.insert(i + 1, new_row)
            return "\n".join(lines), True
    sys.exit(f"error: {label} insertion anchor not found (pattern: {anchor_pattern!r})")


def add_delegation_row(text: str, agent_name: str, model_name: str) -> tuple[str, bool]:
    """Add a generic reviewer row to the system-prompt delegation table."""
    row = (
        f"| `{agent_name}` | Markdown report | Independent review on {model_name} "
        f"| Verifying runtime behavior — it can't execute code |"
    )
    return add_row_after(
        text, r"`reviewer-sol`", row, f"`{agent_name}`", "delegation table"
    )


def add_agents_table_row(
    text: str, agent_name: str, alias: str
) -> tuple[str, bool]:
    """Add a generic reviewer row to the README agents table and bump the count."""
    row = f"| {agent_name} | Independent artifact review | {alias} | Safe |"
    text, inserted = add_row_after(
        text, r"reviewer-sol.*Independent artifact review", row, f"| {agent_name} |", "agents table"
    )
    if inserted:
        text = re.sub(
            r"(## Agents \()(\d+)(\))",
            lambda m: f"{m.group(1)}{int(m.group(2)) + 1}{m.group(3)}",
            text,
            count=1,
        )
    return text, inserted


def add_skill_subagent_row(
    text: str, agent_name: str, model_name: str, alias: str
) -> tuple[str, bool]:
    """Add a generic reviewer row to the review skill's subagents table."""
    model_display = f"{model_name} ({alias})" if model_name != alias else model_name
    row = f"| `{agent_name}` | {model_display} | — |"
    return add_row_after(
        text, r"`reviewer-sol`.*strongest", row, f"`{agent_name}`", "skill subagents table"
    )


# -- main --------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Generate a model-tiered reviewer subagent and wire it in.",
    )
    ap.add_argument("model_alias", help="Model alias from config.toml [[models]]")
    ap.add_argument("suffix", help="Agent name suffix -> reviewer-<suffix>")
    ap.add_argument("--quick", action="store_true", help="Also add to Quick tier")
    ap.add_argument("--standard", action="store_true", help="Also add to Standard tier (Deep inherits)")
    ap.add_argument("--dry-run", action="store_true", help="Preview without writing files")
    ap.add_argument("--force", action="store_true", help="Overwrite an existing reviewer TOML")
    args = ap.parse_args()

    aliases = load_model_aliases()
    if args.model_alias not in aliases:
        known = ", ".join(sorted(aliases)) or "(none)"
        sys.exit(f"error: model alias {args.model_alias!r} not found in config.toml. Known: {known}")
    model_name = aliases[args.model_alias]

    agent_name = f"reviewer-{args.suffix}"
    toml_path = AGENTS_DIR / f"{agent_name}.toml"

    exists = toml_path.exists()
    if exists and not args.force and not args.dry_run:
        sys.exit(f"error: {toml_path} already exists (use --force to overwrite)")

    tiers = ["deep"]
    if args.standard:
        tiers = ["standard", "deep (via standard)"]
    if args.quick:
        tiers.append("quick")

    # Compute all changes before writing anything.
    stamped = stamp_template(args.model_alias, args.suffix, model_name)
    new_config = register_in_allowlist(agent_name)

    sys_text = SYSTEM_PROMPT_PATH.read_text()
    sys_text, tier_changes = edit_tier_table(sys_text, agent_name, args.quick, args.standard)
    sys_text, deleg_added = add_delegation_row(sys_text, agent_name, model_name)

    readme_text = README_PATH.read_text()
    readme_text, readme_tier_changes = edit_tier_table(readme_text, agent_name, args.quick, args.standard)
    readme_text, agents_added = add_agents_table_row(readme_text, agent_name, args.model_alias)

    skill_text = SKILL_PATH.read_text()
    skill_text, skill_tier_changes = edit_tier_table(skill_text, agent_name, args.quick, args.standard)
    skill_text, subagent_added = add_skill_subagent_row(skill_text, agent_name, model_name, args.model_alias)

    # Summary
    print(f"model alias : {args.model_alias} (model name: {model_name})")
    print(f"agent name  : {agent_name}")
    print(f"display     : Reviewer ({args.suffix.capitalize()})")
    print(f"toml path   : {toml_path}")
    print(f"tiers       : {', '.join(tiers)}")
    config_changed = new_config != CONFIG_PATH.read_text()
    print(f"config      : {'add to allowlist' if config_changed else 'already in allowlist'}")
    if exists:
        print(f"toml        : {'overwrite' if args.force else 'exists (use --force)'}")
    else:
        print(f"toml        : create")
    print(f"system prompt: tiers={tier_changes or 'none'}, delegation row={'yes' if deleg_added else 'already present'}")
    print(f"README      : tiers={readme_tier_changes or 'none'}, agents row={'yes' if agents_added else 'already present'}")
    print(f"review skill: tiers={skill_tier_changes or 'none'}, subagents row={'yes' if subagent_added else 'already present'}")

    if args.dry_run:
        print("\n--- dry run: no files written ---")
        return 0

    toml_path.write_text(stamped)
    if config_changed:
        CONFIG_PATH.write_text(new_config)
    SYSTEM_PROMPT_PATH.write_text(sys_text)
    README_PATH.write_text(readme_text)
    SKILL_PATH.write_text(skill_text)

    print(f"\ncreated {toml_path}")
    if config_changed:
        print(f"registered {agent_name!r} in {CONFIG_PATH}")
    print(f"updated {SYSTEM_PROMPT_PATH}")
    print(f"updated {README_PATH}")
    print(f"updated {SKILL_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
