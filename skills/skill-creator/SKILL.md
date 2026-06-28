---
name: skill-creator
description: Use to create or update Skills for Mistral Vibe CLI. Guides through defining, optionally researching, creating, enabling, and testing minimal skills in ~/.vibe/skills/.
user-invocable: true
allowed-tools:
  - read_file
  - write_file
  - edit
  - bash
  - grep
  - web_search
---

# Skill Creator

## Workflow

Ask the user in order:

1. What is the skill's name? (single word or hyphenated)
2. What specific user request should trigger it? (description)
3. What task should it perform? (instructions - be concise)
4. Research similar skills? (n/y)

If yes to research:
- Search local skills: `find ~/.vibe/skills/ -name "SKILL.md" -exec grep -l "{keywords}" {} \;`
- Or web_search: `site:github.com "{task}" SKILL.md` or `{task} agent skill`
- Present findings briefly, ask if they want to adapt anything

## Create

```bash
mkdir -p ~/.vibe/skills/{name}
cat > ~/.vibe/skills/{name}/SKILL.md << EOF
---
name: {name}
description: {description}
---

# {Name}

{instructions}
EOF
```

## Enable

Add to config:
```bash
grep -q enabled ~/.vibe/config.toml && sed -i "/enabled/a\  - \"{name}\"" ~/.vibe/config.toml || echo '[skills]\nenabled = ["{name}"]' >> ~/.vibe/config.toml
```

## Test

```bash
vibe -p "/{name} {realistic-test-prompt}"
```
Show output, ask: "Does this work as expected? (y/n)" - if no, refine and retest.
