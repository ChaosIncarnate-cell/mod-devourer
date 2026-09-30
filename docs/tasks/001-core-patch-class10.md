# 001 — Core patch: class 10 becomes playable

Status: open

## Goal
The smallest possible, self-contained change to azerothcore-wotlk (Playerbot branch) and, if needed,
mod-playerbots so that a character of class 10 can be created, logs in, has rage as power, gets sane stats,
and nothing breaks for the other classes. With no class-10 characters, the patched server behaves exactly
like the unpatched one.

## Deliverables
- `core-patch/class-devourer.patch` (unified diff against a named upstream commit; the local checkout is at
  azerothcore-wotlk `7f12e89` and mod-playerbots `7bae1b5`; say which commits you diffed against).
- `core-patch/apply.ps1` and `core-patch/revert.ps1` (git apply / git apply -R with a dry-run check first).
- `core-patch/README.md`: every hunk, why it is needed.

## Find and handle (search the whole core, not just these)
- `SharedDefines.h`: `CLASS_DEVOURER = 10`, `CLASSMASK_ALL_PLAYABLE` includes it.
- Class-indexed arrays (`StatSystem.cpp` m_diminishing_k, miss/parry/dodge caps; `Player.cpp` dodge_base,
  crit_to_dodge; any others): give index 10 warrior-like values.
- `switch (getClass())` in stat and power code (attack power, rage, crit, block, parry, dual wield...):
  class 10 behaves like a warrior unless the module overrides it.
- Anything that validates or loops over classes and would reject or crash on 10.
- mod-playerbots: random bot creation / class choice must skip class 10 (config or code, prefer config).

## Done when (local session tests)
Patch applies cleanly to the local checkout, builds, the server starts with no new errors, and existing
characters/bots are unaffected. (Creating a class-10 character needs task 003 + 004 as well.)
