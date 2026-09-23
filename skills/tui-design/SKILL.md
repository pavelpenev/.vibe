---
name: tui-design
description: Load this skill before creating, modifying, or reviewing any Chartreux TUI screen, widget, dialog, or stylesheet — forms, pickers, selectors, model lists, modals, hints, and layout conventions.
---

# Chartreux TUI Design Conventions

The authoritative conventions for Chartreux TUI screens. The provider/setup flows must match the main-TUI house style. When this skill conflicts with ad-hoc patterns in existing setup code, this skill wins.

## Widget selection rules

| Need | Widget | Never |
|---|---|---|
| Visible single-choice picker (provider, model, theme) | `NavigableOptionList` (OptionList + j/k) | `Select` for primary choices; Tab traversal of list items |
| Multi-select (enable several models) | `SelectionList` with distinct selected/highlighted styling | Simulated checkboxes via text glyphs in an OptionList |
| Short compact single-choice field | `Select` (non-compact) | `Select` for the main choice of a screen |
| Single-line text entry | `Input` with border + persistent `Label` above | Borderless/compact inputs that look like static text; placeholder as the only label |
| Independent boolean | `Checkbox` | Hand-rendered `[x]` text |

## House style (copy these patterns)

- **Selectors**: `chartreux/ui/widgets/navigable_option_list.py` (j/k aliases). Rows: leading `› ` marker, green marker + bold label for the current item, `Default` label with dim `(currently ...)` hint. On mount: set `highlighted` to the current item and `focus()`. Lists are full-width, borderless, nowrap, ellipsized, `max-height: 50vh`. See `chartreux/cli/textual_ui/widgets/model_picker.py`, `chartreux/ui/widgets/theme_picker.py`.
- **Hints**: inline `NoMarkupStatic` help rows rendered via `shortcut()` / `shortcut_hint()` (`chartreux/ui/shortcut_hints.py`). House format: `↑↓/jk Navigate  Enter Select  Esc Cancel` (two-space separated, keys bold/primary). Do NOT use `Footer`.
- **Key semantics**: Enter selects/confirms/submits the primary action of the focused control — a completed form must submit on Enter without Tabbing to a button. Escape cancels a picker or goes back one step (never silently does nothing). Arrow keys and j/k navigate lists; Tab is for moving between form fields only.
- **Dialogs/panels**: bottom-app `Container` widgets (not bare `ModalScreen` where the house pattern exists): transparent full-width outer container, solid `$foreground-muted` border, `padding: 0 1`, inner `Vertical` content. Titles: short Title Case, bold, `$primary`.
- **Styling**: theme variables only — `$primary`, `$foreground`, `$foreground-muted`, `$text-muted`, `$success`, `$warning`, `$error`, `$surface`, `$chartreux_copper`. Help/status text: `$text-muted`, dim, `margin-top: 1`.
- **Text**: Title Case for titles and action labels; human-readable labels with dimmed/parenthesized metadata (never bare IDs alone); direct sentence-style errors prefixed with the failed operation (`Failed to save key: ...`); `NoMarkupStatic` for any literal or user/provider-supplied text.

## Form rules

1. Persistent `Label` above every `Input`; required fields marked in the label (`API key *`); placeholder is an example, never the identity.
2. Fields must be visibly editable: keep the border, add a distinct `:focus` treatment, use `-invalid` (red border) plus an adjacent error message.
3. Enter submits: route `Input.Submitted` from every single-line field to the same validate-and-save handler as the primary action. On validation failure: retain the dialog, keep typed values, focus the first invalid field, show the error.
4. One clearly primary action; Cancel/Escape adjacent and secondary; destructive actions (clear/reset/delete) visually separated and confirmed.
5. Group related fields into titled sections; one blank row between groups; labels above fields.
6. Validate on blur or submit — never flag incomplete typing as an error. After an error appears, revalidate live so recovery is visible. Use `Input.validate_on=["blur", "submitted"]`; reserve `changed` for cheap, non-disruptive feedback (e.g. live previews).
7. Conditional fields: drive visibility from reactive state — `display = False` removes the field from layout, `visible = False` reserves its space. Never show dependent controls before their prerequisite choice is made.
8. Persistence semantics: live-apply only when each change is safe and cheap; coordinated or atomic changes use explicit Save with a dirty-state indicator, defined Escape behavior, and confirmation before discarding meaningful edits.

## Layout discipline

- **Clutter audit (quantified, run on every layout change)**: count border-nesting depth from terminal edge to content — more than one is normally excessive. Count redundant signals for one state (color + label + icon + row marker) and markers repeated on every row. Apply the removal test to every decorative element: if removing it loses no information, remove it. Prefer whitespace over decorative borders.
- **Pressure-test the floor**: review each screen at wide (>120 cols), standard (80-120), narrow (60-80), and below its content-derived minimum. Know concretely what disappears first, what truncates, and when a truthful "terminal too small — need WxH" state replaces the UI. Multi-column layouts need a single-pane fallback. 80x24 is the compatibility test, not automatically the hard minimum.
- **Responsive priority, not shrinking**: at narrow widths hide previews first, then secondary columns and low-priority metadata — never the primary workflow or required controls. Detail-on-Enter is the escape hatch for removed information. Use relative TCSS sizing (`fr`, percentages, `auto`).
- **Density matches the task**: compact one-line rows for scan-oriented lists; a single column with generous spacing for forms and one-off decisions. Don't spend rows on padding in scan lists.
- **Borders have a job**: only to separate adjacent dynamic panes, establish a needed boundary, or communicate focus. Single-line borders by default; never frame the whole app for decoration.

## Selection-state affordances

- Cursor (highlight) and selection are different things — a highlight must never be the only indication of a selected state.
- Multi-select rows: selected state differs from unselected in glyph AND color/background (e.g. filled vs empty checkbox, `$success` tint). Include a `Space toggle` hint.
- Preselect the configured value; otherwise preselect a named default labeled `Default`/`Recommended` — never silently select the first row.
- Build hierarchy from multiple reliable monospace signals: position, bold/accent emphasis, reverse video, indentation, whitespace. Reverse video is the most reliable current-row signal; focused panels combine at least two cues (accent border + bold accent title). Avoid over-bolding — bold loses hierarchy when applied to much of the screen.
- Never rely on color alone: pair color with text, symbols, or placement, and keep the UI meaningful in monochrome/limited ANSI.

## Focus, keys, and confirmation

- **Focus is visible, contextual state**: the focused panel determines key handling and hint content. Make focus unmistakable with 2-3 combined cues (accent border, stronger title, distinct focused selection; unfocused selections muted). Tab traversal follows visual reading order; modal dialogs trap focus internally with Escape as the exit.
- **Reserved keys**: never bind Ctrl+C, Ctrl+Z, Ctrl+S, or Ctrl+Q as normal app actions — terminals reserve them. Printable navigation aliases (j/k) must yield while a text field owns input. Action-rich screens get a `?` help view; add a command palette only when the action set genuinely warrants one.
- **Confirmation friction scales with irreversibility**: default-No `y/N` for ordinary destructive or batch actions; typed-name confirmation only for high-impact targets; dual confirmation only for genuinely nuclear actions. Never impose typed confirmations on routine actions — habituation defeats the protection. Prefer undo over confirmation where practical.

## Model and provider list rules

- Deduplicate by canonical model ID: one row per actual target. Aliases are metadata on the row (dim), never separate rows.
- Persist canonical IDs; display friendly names; show `provider/model` display names.
- Interactive model pickers list chat-capable models only — filter out embed, moderation, OCR, voxtral/audio, labs/experimental, and other non-chat model families unless the user explicitly asks for them.
- Models already configured are shown selected/preselected by default, not annotated with "already configured" as a separate state.
- Search/filter behavior: filtering narrows the visible list fast (<100ms), shows a `filtered/total` count, highlights matching substrings, and clears on Escape. Smart-case is the default (lowercase query = case-insensitive; mixed-case = case-sensitive).

## Acceptance checklist (implementors self-check; reviewers verify)

- [ ] Lists navigate with arrows + j/k; Enter selects; no Tab required for list traversal
- [ ] Every editable field is visibly a field (border + focus change)
- [ ] Enter completes the primary action from any field
- [ ] Selected vs unselected states are unmistakable (glyph + color, not highlight-only)
- [ ] A hints row is present and accurate on every screen
- [ ] Escape behavior matches the screen's documented semantics
- [ ] No duplicate alias/ID rows in any picker
- [ ] Screen is completable by keyboard at 80x24
- [ ] All literal text uses NoMarkupStatic where markup could misrender
- [ ] Clutter audit passed: border depth ≤ 1, no redundant state signals, decorations survive the removal test
- [ ] Floor plan known: what degrades at narrow widths, and the primary workflow never disappears
- [ ] Validation does not fire while the user is typing; errors revalidate live once shown
