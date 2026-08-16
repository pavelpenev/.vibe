#!/usr/bin/env python3
# SCRIPT-METADATA:
# name: make_reviewer
# description: Generate a model-tiered reviewer subagent TOML from a model alias, sharing the reviewer prompt; optionally register it in config.toml's [tools.task] allowlist
# tags: config,reviewer,subagent

"""Generate a model-tiered reviewer subagent.

Each reviewer shares one prompt (prompts/reviewer.md) but runs on a different
model. Vibe CLI binds a subagent's model at config time, so model diversity
requires separate agent TOMLs. This script stamps a new one from the canonical
template (agents/reviewer-deepseek.toml) and registers it in config.toml.

Usage:
    make_reviewer.py <model-alias> <suffix> [--dry-run] [--force]

Examples:
    make_reviewer.py gpt-5.6-sol sol
        -> agents/reviewer-sol.toml (active_model="gpt-5.6-sol", display "Reviewer (Sol)")
    make_reviewer.py claude-opus opus --dry-run
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


def register_in_allowlist(agent_name: str) -> str:
    """Insert agent_name into config.toml's [tools.task] allowlist if absent.

    Returns the (possibly modified) config text. Idempotent: if already present,
    returns the original text unchanged.
    """
    text = CONFIG_PATH.read_text()

    # Locate the [tools.task] section, then its allowlist array.
    section_match = re.search(r"^\[tools\.task\]\s*$", text, flags=re.MULTILINE)
    if not section_match:
        sys.exit("error: [tools.task] section not found in config.toml")
    section_start = section_match.end()

    allow_match = re.search(
        r"allowlist\s*=\s*\[", text[section_start:]
    )
    if not allow_match:
        sys.exit("error: allowlist not found in [tools.task] section")
    allow_start = section_start + allow_match.end()
    # Find the closing bracket for this array.
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

    # Already registered?
    if re.search(rf'"{re.escape(agent_name)}"\s*,?', allow_body):
        return text

    # Determine indent from an existing entry, fall back to 4 spaces.
    entry_match = re.search(r"^(\s*)\"\w+\"", allow_body, flags=re.MULTILINE)
    indent = entry_match.group(1) if entry_match else "    "

    # Insert the new entry right after "allowlist = [".
    insertion = f"\n{indent}\"{agent_name}\","
    new_text = text[:allow_start] + insertion + text[allow_start:]
    return new_text


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Generate a model-tiered reviewer subagent TOML.",
    )
    ap.add_argument("model_alias", help="Model alias from config.toml [[models]] (e.g. gpt-5.6-sol)")
    ap.add_argument("suffix", help="Agent name suffix -> reviewer-<suffix> (e.g. sol)")
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

    stamped = stamp_template(args.model_alias, args.suffix, model_name)
    new_config = register_in_allowlist(agent_name)

    print(f"model alias : {args.model_alias} (model name: {model_name})")
    print(f"agent name  : {agent_name}")
    print(f"display     : Reviewer ({args.suffix.capitalize()})")
    print(f"toml path   : {toml_path}")
    config_changed = new_config != CONFIG_PATH.read_text()
    if config_changed:
        print(f"config      : would add {agent_name!r} to [tools.task] allowlist")
    else:
        print(f"config      : {agent_name!r} already in allowlist (no change)")
    if exists:
        action = "overwrite" if args.force else "exists (use --force to overwrite)"
        print(f"toml        : {action}")
    else:
        print(f"toml        : create")

    if args.dry_run:
        print("\n--- dry run: no files written ---")
        print("\n# Generated TOML:\n")
        print(stamped)
        return 0

    toml_path.write_text(stamped)
    if config_changed:
        CONFIG_PATH.write_text(new_config)
    print(f"\ncreated {toml_path}")
    if config_changed:
        print(f"registered {agent_name!r} in {CONFIG_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
