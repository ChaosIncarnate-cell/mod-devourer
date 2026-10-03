// Task 020: Wren's Derby, the witch races. Ids 9101360-9101379 belong to the quest thread (the sisters' generator
// keeps to 9101300-9101359); spawn guids 9910300-9910349. Keep in step with data/sql/db-world/*_devourer_derby.sql.
#ifndef DEVOURER_DERBY_IDS_H
#define DEVOURER_DERBY_IDS_H

#include <cstdint>

namespace Devourer::Derby
{
    constexpr uint32_t NpcWren = 9101360;          // Wren at the starting line: the races start and end with her
    constexpr uint32_t NpcHagatha = 9101361;       // Hagatha on her Kakapo, summoned for each race (only you see her)
    constexpr uint32_t NpcBeast = 9101362;         // the Derby Beast: its model is the look of the race body
    constexpr uint32_t GoWitchfire = 9101360;      // a checkpoint
    constexpr uint32_t QuestDerby = 9101360;       // race 1, offered by Wren in the In-Between
    constexpr uint32_t QuestRematch = 9101361;     // race 2
    constexpr uint32_t QuestLastLap = 9101362;     // race 3: Hagatha's Kakapo
    constexpr uint32_t MenuWren = 9101360;
    constexpr uint32_t OptionRace = 0;

    constexpr uint32_t VehicleSaddle = 102;        // one passenger seat on attachment 0, the saddle (Model scouting)
    constexpr uint32_t SpellSpeed = 22590;         // "15% speed bonus", hidden; cast with its amount set
    constexpr int32_t RaceSpeedPct = 60;           // as fast as an apprentice mount
    constexpr uint32_t SpellApprenticeRiding = 33388;
    constexpr uint32_t DisplayKakapo = 980033;     // creature 9301049, the race 3 prize (owner: "Kakapo will be the mount")
    constexpr uint32_t VisualTransform = 24085;    // the sisters' transform flash
    constexpr uint32_t PoiIcon = 7;                // the minimap flag pointing to the next checkpoint
    constexpr uint32_t ShapePrimalTallstrider = 0; // Wren's transformation unlocks this tier-2 form; 0 until the Devourer thread has its id

    constexpr float StartX = -800.0f, StartY = -2640.0f, StartZ = 92.0f;   // the Barrens, west of the Crossroads
    constexpr float CheckpointRadius = 10.0f;
    constexpr float LostDistance = 250.0f;         // this far from the next checkpoint: off the course

    struct Point { float X, Y; };

    // The three courses (x, y; the ground height is looked up). Each ends at the starting line.
    constexpr Point CourseDerby[] =                // about 780 yards: a short loop toward Lushwater Oasis
    {
        { -860.0f, -2580.0f }, { -950.0f, -2500.0f }, { -1040.0f, -2420.0f }, { -1000.0f, -2340.0f },
        { -920.0f, -2440.0f }, { -850.0f, -2540.0f }, { StartX, StartY },
    };
    constexpr Point CourseRematch[] =              // about 1270 yards: through the oasis shallows
    {
        { -900.0f, -2540.0f }, { -1020.0f, -2430.0f }, { -1100.0f, -2300.0f }, { -1060.0f, -2160.0f },
        { -1150.0f, -2230.0f }, { -1180.0f, -2380.0f }, { -1060.0f, -2500.0f }, { -920.0f, -2600.0f },
        { StartX, StartY },
    };
    constexpr Point CourseLastLap[] =              // about 1450 yards: the full course, about two minutes
    {
        { -900.0f, -2680.0f }, { -1050.0f, -2600.0f }, { -1180.0f, -2480.0f }, { -1200.0f, -2330.0f },
        { -1120.0f, -2200.0f }, { -1040.0f, -2120.0f }, { -960.0f, -2250.0f }, { -930.0f, -2400.0f },
        { -860.0f, -2540.0f }, { StartX, StartY },
    };

    // Hagatha's pace in yards per second. The race body runs 11.2 (7 x 1.6); she leaves room for the turns.
    constexpr float PaceDerby = 8.5f, PaceRematch = 9.5f, PaceLastLap = 10.3f;

    // creature_text groups
    enum Line : uint8_t
    {
        WrenChallenger = 0, WrenTransform = 1, WrenMarks = 2, WrenWonDerby = 3, WrenLost = 4, WrenDropped = 5,
        WrenNoRider = 6, WrenNoRace = 7, WrenWonRematch = 8, WrenWonLastLap = 9, WrenOffCourse = 10, WrenBusy = 11,
        HagathaArrives = 0, HagathaGo = 1, HagathaWins = 2, HagathaLoses = 3, HagathaGivesKakapo = 4,
    };
}

#endif
