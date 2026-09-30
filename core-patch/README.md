# core-patch: class 10 (Devourer) becomes playable

Two small patches. Everything else about the class (name, power type, talents, spells, start data, stat rows)
is data (task 003) or module code (task 002).

| File | Target repo | Diffed against |
|---|---|---|
| `class-devourer.patch` | mod-playerbots/azerothcore-wotlk, branch `Playerbot` | `7f12e89ee5f467a50e62eba1d525eac7dc953d03` |
| `playerbots-class-devourer.patch` | mod-playerbots/mod-playerbots | `7bae1b5c58c76a0aa20381155edc08096d1485b2` |

```powershell
.\apply.ps1  -CorePath Z:\path\to\azerothcore-wotlk                  # mod-playerbots defaults to <core>\modules\mod-playerbots
.\revert.ps1 -CorePath Z:\path\to\azerothcore-wotlk [-PlayerbotsPath ...]
```

Both scripts dry-run both patches (`git apply --check`) before touching anything, detect an already applied /
not applied tree, and use `--ignore-whitespace` so CRLF checkouts work. `.gitattributes` keeps the patch files
LF. After applying: rebuild (SharedDefines.h changed, so nearly everything recompiles).

Checked in a cloud session: both patches apply to clean checkouts of the commits above, and every touched
file (plus `CharacterHandler.cpp`, `DBCStores.cpp`, `cs_lookup.cpp`) compiles with clang `-fsyntax-only`
against the real tree. Not built or run.

## azerothcore-wotlk hunks

1. **`SharedDefines.h` — `CLASS_DEVOURER = 10`** replaces the commented-out `//CLASS_UNK = 10`. `MAX_CLASSES`
   is already 12, so every `[MAX_CLASSES]` array already has a slot for class 10.
2. **`SharedDefines.h` — `CLASSMASK_ALL_PLAYABLE` gains bit `1<<9`.** Needed because:
   - `DBCStores.cpp` only builds `sTalentTabPages[class]` for talent tabs whose `ClassMask` hits this mask.
     Without it a Devourer has no talent trees (and the module's spec = talent tree rule has nothing to read).
   - quest `RequiredClasses`, `conditions` (CONDITION_CLASS), item `AllowableClass`, achievement class
     criteria and server mail class filters are validated against this mask; a class-10 value would
     be rejected at load with an error.
   Effect with no class-10 data: none. Stock data never uses bit `0x200`; the only difference is that bogus
   rows carrying just that bit would no longer be reported as errors.
3. **`enuminfo_SharedDefines.cpp`** — the generated `EnumUtils<Classes>` data gets the new value (Count 10→11,
   index 9 = Devourer, Druid moves to 10). Without it `EnumUtils::ToTitle(Classes(10))` throws
   `std::out_of_range`, e.g. in `.lookup player` (`cs_lookup.cpp`, which accepts any class `<= CLASS_DRUID`).
   Nothing iterates `EnumUtils<Classes>` by index in the core or mod-playerbots.
4. **`StatSystem.cpp` — `m_diminishing_k`, `miss_cap`, `parry_cap`, `dodge_cap`**: index 9 (class 10) was
   `0.0f` everywhere. `miss_cap` and `dodge_cap` are used unconditionally, so a class-10 player would get
   `x * 0 / (x + 0 * 0)` (0/0 = NaN when x = 0) as miss/dodge chance. Now warrior values.
5. **`Player.cpp` — `dodge_base`, `crit_to_dodge`** in `GetDodgeFromAgility`: index 9 was `0.0f`; warrior values.
6. **`ObjectMgr.cpp` — `BuildPlayerLevelInfo`**: `case CLASS_DEVOURER` shares the warrior stat growth used for
   levels above the highest `player_levelstats` row (only relevant when MaxPlayerLevel > DB data).

With no class-10 characters, hunks 4-6 are never reached with index 10, hunk 3 only changes the value list,
and hunk 2 is covered above: the server behaves as before.

## mod-playerbots hunks

The task preferred a config switch, but there is none that works: `CharacterCreating.Disabled.ClassMask` is
what `RandomPlayerbotFactory` honours, and it also blocks real players (without the RBAC skip permission)
from creating that class. So three one-line skips:

1. **`RandomPlayerbotFactory::CreateRandomBots`** — skip `CLASS_DEVOURER`. It loops over every class that
   is in `CLASSMASK_ALL_PLAYABLE` and has a `ChrClasses` row, so once task 003 adds the row it would create
   class-10 random bots. Bot accounts keep 10 characters (the other ten classes), exactly as now.
2. **`RandomItemMgr::InitWeaponProficiency`** and 3. **`RandomItemMgr::BuildCacheEquip`** — skip class 10.
   They loop over `CLASSMASK_ALL_PLAYABLE`; without the skip, the equip cache would get class-10 rows in
   the playerbots DB at the next rebuild. Harmless but not "unchanged".

Other class loops in mod-playerbots (`TravelMgr`, `ReviveFromCorpseAction`, `RandomItemMgr` weight scales)
already run over index 10 today and only act where a `playercreateinfo`/`ChrClasses` row exists; they need
no change. A player's *own* class-10 character logged in as a bot (`.playerbots bot add`) would have no class
AI; that is the owner's choice, not something random bots do.

## Not in the patch, on purpose

- **Warrior-like behaviour in `IsClass(...)` checks** (attack power from strength/agility in
  `StatSystem.cpp`, plate at 40 / shields in `PlayerStorage.cpp`, block value, ...). These go through
  `Player::IsClass`, which asks the `PlayerScript::OnPlayerIsClass` hook first, so the **module** answers
  "yes, warrior" for class 10 in the contexts it wants (`CLASS_CONTEXT_STATS`, `CLASS_CONTEXT_EQUIP_ARMOR_CLASS`,
  `CLASS_CONTEXT_EQUIP_SHIELDS`, ...). Warrior abilities (`CLASS_CONTEXT_ABILITY*`) stay off. This is in
  task 002; without the module a class-10 character just gets the generic defaults.
- **Rage as power** is data: `Player::Create` and `Player::InitDataForForm` take the power type from the `ChrClasses`
  row (`chrclasses_dbc.PowerType = 1`, task 003). Rage generation/decay then work via `HasActivePowerType`.
- **Class name colour** in `Player::GetPlayerName` — cosmetic, empty colour is fine.

## Data that must exist before a class-10 character is created (task 003)

The core looks these up by class and misbehaves if they are missing:

- `chrclasses_dbc` row 10 (character creation and `Player::Create` refuse the class without it).
- `playercreateinfo` rows **and** `player_class_stats` rows for class 10 together: `LoadPlayerInfo`
  dereferences the class stats for every race/class that has a `playercreateinfo` row
  (crash on a null pointer if class stats are missing) and `exit(1)`s if the start level has no stats.
- `gt*` tables are indexed `(class-1) * 100 + level-1`. The stock DBCs have class-10 rows, but they are
  probably zero. Zero `gtOCTClassCombatRatingScalar` makes every rating worthless; zero `gtChanceToMeleeCrit*`
  = no crit or dodge from agility. Copy the warrior rows into `gtchancetomeleecrit(base)_dbc`,
  `gtchancetospellcrit(base)_dbc`, `gtoctclasscombatratingscalar_dbc`, `gtoctregenhp_dbc`,
  `gtregenhpperspt_dbc`, `gtregenmpperspt_dbc` at the class-10 indices.
- `talenttab_dbc` with `ClassMask = 0x200`, `skillraceclassinfo_dbc` for armor/weapon skills.

## Removing the Devourer

Uninstall SQL (task 003) first, then either keep this patch (dormant) or run `revert.ps1` and rebuild.
