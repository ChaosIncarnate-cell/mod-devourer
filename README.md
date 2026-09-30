# mod-devourer

**The Devourer: a shapeshifter class that becomes what it eats**, as a real WotLK 3.3.5a class (id 10, next to
the normal classes) for AzerothCore with mod-playerbots, built to be removable.

Status: porting from the owner's CoA repack version. See `docs/design.md` for the plan and `docs/tasks/` for
the work items. `docs/coa-original/README.md` describes how the class plays.

Layers: a small dormant-safe core patch (`core-patch/`), this module (`src/`, switch `Devourer.Enable`),
SQL with uninstall (`data/sql/`), and one client MPQ built locally from the owner's client files.
