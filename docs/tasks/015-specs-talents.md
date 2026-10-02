# 015 — The three specs: real talents, spec abilities and Anima costs

Status: open. Base: branch `task/006-007-devourer-start` (901bb5c). Branch: `task/015-specs-talents`.
Read `CLAUDE.md`, `docs/design.md`, `docs/talents.md`, `docs/coa-original/README.md` first.
Owner's rule: build only what is asked here; anything else goes into the proposal as a suggestion.

## Goal (owner, 2026-10-03)
Keep the three specs **Glutton, Skinchanger, Brood** and fill them: today every tree is 30 placeholder talents
plus 3 placeholder spec abilities per spec at 20/40/60 (`tools/placeholders.py` → SQL 07,
`DevourerPlaceholderIds.h`). Also: **shapes no longer cost Anima** (done: `Devourer.AnimaPerShift = 0`);
instead **strong abilities, spec abilities and talents cost Anima**.

## Step 1 — proposal first (no code yet)
Write `docs/specs-proposal.md` and open a PR with only that file. For each spec:
- role and core mechanic in 2-3 lines (Glutton: tank, eats/steals abilities, Devour Whole + Regurgitate;
  Skinchanger: shifting mid-fight, echoes, 3 sec shift cooldown; Brood: hatchlings that fight and feed the mother;
  see `docs/coa-original` and the owner's notes "Devourer Features.md" copied in docs if present);
- the 3 spec abilities (20/40/60) and ~20-30 talents (tiers every 5 levels, max ranks, prerequisites), each one
  line: name, effect, numbers, Anima cost if active;
- which existing kit abilities count as "strong" and get an Anima cost (and how much), keeping Concentrate (+30)
  and devouring as the ways to gain it.
Immersion rule: names and texts speak as Azeroth, no game jargon. Keep it buildable with stock 3.3.5a spell
templates + small SpellScripts like the existing ones.
**Stop after the proposal**: the owner marks what she wants in the PR, then step 2.

## Step 2 — after the owner's OK
Build the chosen talents/spec abilities (replace placeholders in place, same ids where possible; client patch rows
via the existing tools), apply the Anima costs, update `docs/talents.md`. Uninstall keeps working.

## Done when (local session tests in game)
Each spec plays differently; talents and spec abilities work and show real tooltips; strong abilities cost Anima.
