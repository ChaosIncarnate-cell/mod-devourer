/*
 * mod-devourer: Wren's Derby, the witch races (task 020).
 * Released under GNU AGPL v3, like AzerothCore.
 *
 * Wren bet Hagatha that her "pet" outruns Hagatha's Kakapo. Three races in the Barrens (level 20), each unlocking the
 * next: Wren's Derby, Hagatha Wants a Rematch, The Last Lap. At the starting line Wren turns the Devourer into the
 * Derby Beast, a body with a saddle (vehicle 102: one passenger seat on the saddle), and its companion (Bramble, or any
 * party member nearby) is put on its back. Then a countdown, and a course of witch-fires; Hagatha rides the same course
 * at a set pace. The Devourer wins by passing the last fire first with its rider still on its back.
 *
 * No client change: the race body is a display, a vehicle kit and a hidden stock speed aura. Data: DevourerDerbyIds.h
 * and data/sql/db-world/2026_10_03_20_devourer_derby.sql.
 */

#include "Devourer.h"
#include "DevourerDerbyIds.h"

#include "Config.h"
#include "CreatureAI.h"
#include "CreatureScript.h"
#include "GameObject.h"
#include "Group.h"
#include "Map.h"
#include "MotionMaster.h"
#include "ObjectAccessor.h"
#include "ObjectMgr.h"
#include "Opcodes.h"
#include "Player.h"
#include "PlayerScript.h"
#include "ScriptedGossip.h"
#include "TemporarySummon.h"
#include "Vehicle.h"
#include "WorldPacket.h"
#include "WorldScript.h"
#include "WorldSession.h"
#include <cmath>
#include <string>
#include <unordered_map>
#include <vector>

using namespace Devourer;
using namespace Devourer::Derby;

namespace
{
    constexpr uint32 UpdateEvery = 250;          // ms between two looks at a running race
    constexpr uint32 BeatEvery = 1500;           // ms between the countdown beats
    constexpr float RiderRange = 30.0f;          // a rider must stand this close when the race starts
    constexpr float LineRange = 40.0f;           // the Devourer must be this close to the starting line

    std::string companion = "Bramble";           // Devourer.WitchCompanion, the same option as the sisters'

    struct Race
    {
        enum Step : uint8 { Countdown, Running };

        uint32 Quest = 0;
        Step Now = Countdown;
        uint8 Beat = 0;
        uint32 Timer = 0;
        std::vector<Position> Points;
        float Pace = 0.0f;
        uint8 Next = 0;                           // the checkpoint to reach next
        ObjectGuid Wren, Hagatha, Rider;
        std::vector<ObjectGuid> Fires;
        uint32 FormSpell = 0;                     // the shape worn before the race, put back after it
    };

    std::unordered_map<ObjectGuid::LowType, Race> races;

    Race* RaceOf(Player* player)
    {
        auto itr = races.find(player->GetGUID().GetCounter());
        return itr == races.end() ? nullptr : &itr->second;
    }

    // The race this Devourer is signed up for (taken, not yet won), 0 = none.
    uint32 SignedUpFor(Player* player)
    {
        for (uint32 quest : { QuestDerby, QuestRematch, QuestLastLap })
            if (player->GetQuestStatus(quest) == QUEST_STATUS_INCOMPLETE)
                return quest;
        return 0;
    }

    template <size_t N>
    void Lay(Player* player, Point const (&course)[N], Race& race)
    {
        Map* map = player->GetMap();
        for (Point const& p : course)
        {
            float z = map->GetHeight(player->GetPhaseMask(), p.X, p.Y, StartZ + 40.0f, true, 100.0f);
            if (z <= INVALID_HEIGHT)
                z = StartZ;
            race.Points.emplace_back(p.X, p.Y, z);
        }
    }

    void LayCourse(Player* player, Race& race)
    {
        race.Points.clear();
        switch (race.Quest)
        {
            case QuestDerby: Lay(player, CourseDerby, race); race.Pace = PaceDerby; break;
            case QuestRematch: Lay(player, CourseRematch, race); race.Pace = PaceRematch; break;
            default: Lay(player, CourseLastLap, race); race.Pace = PaceLastLap; break;
        }
    }

    // Bramble if she is there, else any party member close by who is free to climb on.
    Player* FindRider(Player* player)
    {
        Group* group = player->GetGroup();
        if (!group)
            return nullptr;
        Player* anyone = nullptr;
        for (GroupReference* itr = group->GetFirstMember(); itr; itr = itr->next())
        {
            Player* member = itr->GetSource();
            if (!member || member == player || !member->IsInMap(player) || !member->IsAlive() ||
                member->GetVehicle() || member->GetVehicleKit() || !member->IsWithinDist(player, RiderRange))
                continue;
            if (member->GetName() == companion)
                return member;
            if (!anyone)
                anyone = member;
        }
        return anyone;
    }

    bool IsCompanion(Unit const* unit) { return unit && unit->GetName() == companion; }

    void RiderSays(Player* player, Race const& race, char const* text)
    {
        if (Player* rider = ObjectAccessor::GetPlayer(*player, race.Rider))
            if (IsCompanion(rider))
                rider->Say(text, LANG_UNIVERSAL);
    }

    void SendVehicleData(Player* player, uint32 vehicleId)
    {
        WorldPacket data(SMSG_PLAYER_VEHICLE_DATA, player->GetPackGUID().size() + 4);
        data << player->GetPackGUID();
        data << uint32(vehicleId);
        player->SendMessageToSet(&data, true);
        if (vehicleId)
        {
            WorldPacket expected(SMSG_ON_CANCEL_EXPECTED_RIDE_VEHICLE_AURA, 0);
            player->SendDirectMessage(&expected);
        }
    }

    // The minimap flag on the next checkpoint.
    void PointTo(Player* player, Race const& race)
    {
        Position const& p = race.Points[race.Next];
        std::string const name = race.Next + 1 == race.Points.size() ? "Finish line" :
            "Checkpoint " + std::to_string(race.Next + 1);
        WorldPacket data(SMSG_GOSSIP_POI, 4 + 4 + 4 + 4 + 4 + name.size() + 1);
        data << uint32(99) << float(p.GetPositionX()) << float(p.GetPositionY()) << uint32(PoiIcon) << uint32(0) << name;
        player->SendDirectMessage(&data);
    }

    // Wren's spell: the Derby Beast's look, a saddle for one passenger, an apprentice mount's speed.
    void PutOnBeast(Player* player, Race& race)
    {
        player->Dismount();
        player->RemoveAurasByType(SPELL_AURA_MOUNTED);
        race.FormSpell = player->getTransForm();
        if (race.FormSpell)
            player->RemoveAurasDueToSpell(race.FormSpell);

        if (CreatureTemplate const* beast = sObjectMgr->GetCreatureTemplate(NpcBeast))
            if (CreatureModel const* model = beast->GetFirstValidModel())
                player->SetDisplayId(model->CreatureDisplayID);

        if (player->CreateVehicleKit(VehicleSaddle, 0))
            SendVehicleData(player, VehicleSaddle);

        int32 const speed = RaceSpeedPct;
        player->CastCustomSpell(player, SpellSpeed, &speed, nullptr, nullptr, true);
    }

    void TakeOffBeast(Player* player, Race& race)
    {
        if (Player* rider = ObjectAccessor::GetPlayer(*player, race.Rider))
            if (rider->GetVehicleBase() == player)
                rider->ExitVehicle();
        if (player->GetVehicleKit())
        {
            player->RemoveVehicleKit();
            SendVehicleData(player, 0);
        }
        player->RemoveAurasDueToSpell(SpellSpeed);
        player->SetControlled(false, UNIT_STATE_ROOT);
        player->DeMorph();
        if (race.FormSpell && player->IsAlive() && player->HasSpell(race.FormSpell))
            player->CastSpell(player, race.FormSpell, true);
    }

    void WrenSays(Player* player, Race const& race, uint8 line)
    {
        if (Creature* wren = ObjectAccessor::GetCreature(*player, race.Wren))
            if (wren->AI())
                wren->AI()->Talk(line, player);
    }

    void HagathaSays(Player* player, Race const& race, uint8 line)
    {
        if (Creature* hagatha = ObjectAccessor::GetCreature(*player, race.Hagatha))
            if (hagatha->AI())
                hagatha->AI()->Talk(line, player);
    }

    // Clears everything a race put into the world. quiet = logout: nobody to talk to.
    void EndRace(Player* player, bool quiet = false)
    {
        Race* race = RaceOf(player);
        if (!race)
            return;
        TakeOffBeast(player, *race);
        if (Creature* hagatha = ObjectAccessor::GetCreature(*player, race->Hagatha))
            hagatha->DespawnOrUnsummon(quiet ? 0ms : 4s);
        for (ObjectGuid const& guid : race->Fires)
            if (GameObject* fire = ObjectAccessor::GetGameObject(*player, guid))
                fire->DespawnOrUnsummon();
        races.erase(player->GetGUID().GetCounter());
    }

    void Lose(Player* player, uint8 wrenLine, bool hagathaWon = false)
    {
        Race* race = RaceOf(player);
        if (!race)
            return;
        WrenSays(player, *race, wrenLine);
        if (hagathaWon)
            HagathaSays(player, *race, HagathaWins);
        EndRace(player);
    }

    void Win(Player* player)
    {
        Race* race = RaceOf(player);
        if (!race)
            return;
        player->AreaExploredOrEventHappens(race->Quest);
        switch (race->Quest)
        {
            case QuestDerby: WrenSays(player, *race, WrenWonDerby); break;
            case QuestRematch: WrenSays(player, *race, WrenWonRematch); break;
            default: WrenSays(player, *race, WrenWonLastLap); break;
        }
        HagathaSays(player, *race, race->Quest == QuestLastLap ? HagathaGivesKakapo : HagathaLoses);
        RiderSays(player, *race, "We won! Can we do it again? Can we do it again?");
        EndRace(player);
    }
}

// --- Hagatha on her Kakapo -------------------------------------------------------------------------------------------

struct npc_devourer_derby_hagatha : public CreatureAI
{
    explicit npc_devourer_derby_hagatha(Creature* creature) : CreatureAI(creature) { }

    std::vector<Position> Path;
    uint32 Index = 0;
    bool Running = false;
    bool Finished = false;

    void UpdateAI(uint32 /*diff*/) override { }

    void Run(std::vector<Position> const& path, float pace)
    {
        Path = path;
        Index = 0;
        Running = !Path.empty();
        me->SetWalk(false);
        me->SetSpeedRate(MOVE_RUN, pace / baseMoveSpeed[MOVE_RUN]);
        if (Running)
            me->GetMotionMaster()->MovePoint(Index, Path[Index]);
    }

    void MovementInform(uint32 type, uint32 id) override
    {
        if (type != POINT_MOTION_TYPE || !Running || id != Index)
            return;
        if (++Index >= Path.size())
        {
            Running = false;
            Finished = true;
            return;
        }
        me->GetMotionMaster()->MovePoint(Index, Path[Index]);
    }
};

// --- Wren at the starting line --------------------------------------------------------------------------------------

struct npc_devourer_derby_wren : public CreatureAI
{
    explicit npc_devourer_derby_wren(Creature* creature) : CreatureAI(creature) { }

    void UpdateAI(uint32 /*diff*/) override { }

    void sGossipSelect(Player* player, uint32 menuId, uint32 optionId) override
    {
        if (menuId != MenuWren || optionId != OptionRace)
            return;
        CloseGossipMenuFor(player);
        Start(player);
    }

    void sQuestReward(Player* player, Quest const* quest, uint32 /*opt*/) override
    {
        if (quest->GetQuestId() != QuestDerby)
            return;
        // Race 1 opens riding: Apprentice Riding.
        if (!player->HasSpell(SpellApprenticeRiding))
            player->learnSpell(SpellApprenticeRiding);
    }

    void Start(Player* player)
    {
        Race tryRace;
        tryRace.Wren = me->GetGUID();
        tryRace.Quest = SignedUpFor(player);
        if (!tryRace.Quest)
        {
            Talk(WrenNoRace, player);
            return;
        }
        if (RaceOf(player) || player->IsInCombat() || !player->IsAlive() || player->GetVehicle() ||
            player->GetVehicleKit() || player->GetExactDist2d(StartX, StartY) > LineRange)
        {
            Talk(WrenBusy, player);
            return;
        }
        Player* rider = FindRider(player);
        if (!rider)
        {
            Talk(WrenNoRider, player);
            return;
        }

        Race& race = races[player->GetGUID().GetCounter()] = tryRace;
        race.Rider = rider->GetGUID();
        LayCourse(player, race);

        // Hagatha swoops in beside the Devourer, on the Kakapo; only this Devourer sees her.
        Position at = player->GetPosition();
        player->MovePositionToFirstCollision(at, 4.0f, float(M_PI) / 2.0f);
        if (TempSummon* hagatha = player->SummonCreature(NpcHagatha, at.GetPositionX(), at.GetPositionY(),
            at.GetPositionZ(), player->GetOrientation(), TEMPSUMMON_MANUAL_DESPAWN, 0, nullptr, true))
        {
            hagatha->Mount(DisplayKakapo);
            race.Hagatha = hagatha->GetGUID();
        }

        Talk(WrenChallenger, player);
        HagathaSays(player, race, HagathaArrives);
        me->HandleEmoteCommand(EMOTE_ONESHOT_SPELL_CAST_OMNI);
        player->CastSpell(player, VisualTransform, true);
        PutOnBeast(player, race);
        // The body Wren gives it is its own from now on, won or lost: the Primal Tallstrider form (owner, 2026-10-03:
        // "it does not matter if winning or loosing there, it gets unlocked, with the transformation").
        if (ShapePrimalTallstrider)
            sDevourer.Unlock(player, ShapePrimalTallstrider, 0, false);
        rider->EnterVehicle(player, 0);
        Talk(WrenTransform, player);
        if (IsCompanion(rider))
            rider->Say("I'm the navigator! Left! No, the other left!", LANG_UNIVERSAL);

        player->SetControlled(true, UNIT_STATE_ROOT);  // until the countdown is over
        race.Now = Race::Countdown;
        race.Beat = 0;
        race.Timer = BeatEvery;
    }
};

// --- the race, looked at from the Devourer's side ----------------------------------------------------------------

namespace
{
    void Countdown(Player* player, Race& race)
    {
        switch (race.Beat++)
        {
            case 0: WrenSays(player, race, WrenMarks); return;
            case 1: player->GetSession()->SendAreaTriggerMessage("3"); return;
            case 2: player->GetSession()->SendAreaTriggerMessage("2"); return;
            case 3: player->GetSession()->SendAreaTriggerMessage("1"); return;
            default: break;
        }

        player->GetSession()->SendAreaTriggerMessage("GO!");
        player->SetControlled(false, UNIT_STATE_ROOT);
        for (Position const& p : race.Points)
            if (GameObject* fire = player->SummonGameObject(GoWitchfire, p.GetPositionX(), p.GetPositionY(),
                p.GetPositionZ(), 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 600))
                race.Fires.push_back(fire->GetGUID());
        if (Creature* hagatha = ObjectAccessor::GetCreature(*player, race.Hagatha))
            if (auto* ai = dynamic_cast<npc_devourer_derby_hagatha*>(hagatha->AI()))
            {
                ai->Talk(HagathaGo, player);
                ai->Run(race.Points, race.Pace);
            }
        race.Now = Race::Running;
        race.Next = 0;
        PointTo(player, race);
    }

    void Running(Player* player, Race& race)
    {
        // The rider must still be on its back.
        Vehicle* saddle = player->GetVehicleKit();
        Unit* rider = saddle ? saddle->GetPassenger(0) : nullptr;
        if (!rider || rider->GetGUID() != race.Rider)
        {
            Lose(player, WrenDropped);
            return;
        }

        Creature* hagatha = ObjectAccessor::GetCreature(*player, race.Hagatha);
        auto* ai = hagatha ? dynamic_cast<npc_devourer_derby_hagatha*>(hagatha->AI()) : nullptr;
        if (!ai || ai->Finished)
        {
            Lose(player, WrenLost, ai != nullptr);
            return;
        }

        Position const& next = race.Points[race.Next];
        float const dist = player->GetExactDist2d(next.GetPositionX(), next.GetPositionY());
        if (dist > LostDistance)
        {
            Lose(player, WrenOffCourse);
            return;
        }
        if (dist > CheckpointRadius || std::fabs(player->GetPositionZ() - next.GetPositionZ()) > 15.0f)
            return;

        if (++race.Next >= race.Points.size())
        {
            Win(player);
            return;
        }
        player->GetSession()->SendAreaTriggerMessage("Checkpoint {} of {}", uint32(race.Next),
            uint32(race.Points.size() - 1));
        if (race.Next == race.Points.size() / 2)
            RiderSays(player, race, "Halfway! I think. Yes! Probably!");
        PointTo(player, race);
    }

    void Update(Player* player, Race& race, uint32 diff)
    {
        if (!player->IsAlive() || player->GetMapId() != 1 || player->IsBeingTeleported())
        {
            Lose(player, WrenLost);
            return;
        }
        if (race.Timer > diff)
        {
            race.Timer -= diff;
            return;
        }
        if (race.Now == Race::Countdown)
        {
            race.Timer = BeatEvery;
            Countdown(player, race);
        }
        else
        {
            race.Timer = UpdateEvery;
            Running(player, race);
        }
    }
}

class devourer_derby_player : public PlayerScript
{
public:
    devourer_derby_player() : PlayerScript("devourer_derby_player") { }

    void OnPlayerUpdate(Player* player, uint32 diff) override
    {
        if (Race* race = RaceOf(player))
            Update(player, *race, diff);
    }

    void OnPlayerLogout(Player* player) override
    {
        EndRace(player, true);
    }
};

class devourer_derby_world : public WorldScript
{
public:
    devourer_derby_world() : WorldScript("devourer_derby_world") { }

    void OnAfterConfigLoad(bool /*reload*/) override
    {
        companion = sConfigMgr->GetOption<std::string>("Devourer.WitchCompanion", "Bramble");
    }
};

void AddSC_devourer_derby()
{
    RegisterCreatureAI(npc_devourer_derby_hagatha);
    RegisterCreatureAI(npc_devourer_derby_wren);
    new devourer_derby_player();
    new devourer_derby_world();
}
