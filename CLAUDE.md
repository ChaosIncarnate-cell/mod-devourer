# mod-devourer — notes for Claude sessions

Port of the **Devourer** class (a shapeshifter that becomes what it eats) from the owner's CoA repack to the
Chromaticaw server: AzerothCore WotLK 3.3.5a, **mod-playerbots fork** (`github.com/mod-playerbots/azerothcore-wotlk`,
branch `Playerbot`), standard 3.3.5a client (build 12340) with HD model patches. Owner: ChaosIncarnate-cell.

**Target is Chromaticaw only.** CoA is just where the code came from: do not keep CoA compatibility, class 20,
CoA schemas or anything "so it still works on CoA". Change or drop CoA-specific code freely.

Read `docs/design.md` first. It explains the target architecture and why.

## How work is split

- **Cloud sessions write code, SQL and tools.** No game client, no client data, no running server there.
  You may clone upstream azerothcore-wotlk (Playerbot branch) and mod-playerbots to read code and to
  compile-check (`tools/syntax-check.sh` does it).
- **The local session (owner's PC)** builds the server, generates the client patch from the real client
  files, installs, and tests in game. It writes what happened to `docs/results/`.
- Channel = this repo: tasks in `docs/tasks/NNN-name.md`, results in `docs/results/NNN-name.md`.
  Branch `task/NNN-name`, PR per task, PR text says what to test.

## The game client (owner's PC)

- **The one client to use:** `Z:\ChromaticawBots\WOW HD CLIENT` (the patch goes to its `Data\` folder,
  e.g. `Data\patch-Z.MPQ`; build the patch with `--client "Z:\ChromaticawBots\WOW HD CLIENT"`).
- **Never use** `Z:\AzerothCore\Chromatica\world of warcraft 3.3.5a hd older`: an old copy, kept only as a backup.
  Do not read from it, build from it or install into it.
- Always write the full path in notes and instructions (never just "world of warcraft 3.3.5a hd").

## Hard rules

1. **Removable.** Gameplay lives in this module; class data lives in SQL with a matching uninstall; client
   files live in one MPQ. The only core change is the small class-10 patch in `core-patch/`, which must be
   harmless when no character has class 10 (so removing the Devourer never requires rebuilding the core).
2. **Never commit Blizzard or Ascension/CoA assets** (MPQ, DBC, BLP, M2, extracted client Lua/XML). Tools may
   read them locally; the repo only holds our own code, SQL and small diffs/snippets we wrote.
3. **No CoA engine code.** `docs/coa-original/` describes the CoA version; its engine (`src/server/coa`,
   Ascension*) does not exist here. The module's only CoA dependencies were `getClass() == 20` and
   `GetAscensionActiveSpecialization()`; both get replaced (see design).
4. Class id **10** (unused in 3.3.5a, `//CLASS_UNK = 10` in SharedDefines.h, `MAX_CLASSES` already 12).
   Hunger = the normal rage bar (`POWER_RAGE`, stored x10).
5. Random playerbots must never be created as class 10 (there is no bot AI for it).

## Layout

- `src/` module code, `conf/`, `data/sql/` (install + `uninstall/`, see `data/sql/README.md`)
- `tools/build_class_dbc_sql.py` class-10 rows derived from the server's DBCs (output never committed)
- `tools/client/` the client patch: `build_client_patch.py` builds `patch-Z.MPQ` from the owner's client + CoA
  files (pure-Python MPQ/DBC/BLP, no StormLib); `selftest.py` checks it against a made-up client (task 004)
- `core-patch/` the class-10 core patch + apply/revert scripts (task 001)
- `tools/coa/` the CoA generators still in use: spells (`build_devourer_spells.py`), models, skins
- `docs/coa-original/` CoA README and the list of CoA core files it had to override (reference only)
