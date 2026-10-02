/*
 * mod-devourer: the Hollowmoor witch sisters (task 010).
 * Released under GNU AGPL v3, like AzerothCore.
 *
 * At level 5 a ritual pulls the Devourer into the In-Between (map 35, see tools/witch_sisters.py). It wakes in a
 * cage, the sisters talk, Wren turns it into a Baby Berserker (shape 4) and hands out three chores. When the last
 * one is handed in, the cage opens and both sisters are its trainers. "Send me back" returns it to where the ritual
 * took it; `.inbetween` (a stopgap until a proper spell, see the task 010 PR) brings a freed Devourer back.
 * Wren's fourth chore (owner, 2026-10-02): "Pests in the Cells" turns the Devourer into a Biletoad (shape 14) and
 * puts anima pests around her cages, for each Devourer its own; some hover out of reach (DevourerFrogs.cpp).
 *
 * Data: all ids, places and lines come from tools/witch_sisters.py (DevourerSistersIds.h and the world SQL).
 * Characters: character_devourer_inbetween keeps where the Devourer was taken from and when it may come back.
 */

#include "Devourer.h"
#include "DevourerSistersIds.h"

#include "Chat.h"
#include "CommandScript.h"
#include "Config.h"
#include "CreatureAI.h"
#include "CreatureScript.h"
#include "CreatureTextMgr.h"
#include "DatabaseEnv.h"
#include "GameObject.h"
#include "GameTime.h"
#include "GossipDef.h"
#include "Map.h"
#include "ObjectAccessor.h"
#include "ObjectMgr.h"
#include "Player.h"
#include "PlayerScript.h"
#include "ScriptedGossip.h"
#include "Random.h"
#include "TemporarySummon.h"
#include "WorldPacket.h"
#include "WorldScript.h"
#include "WorldSession.h"
#include <algorithm>
#include <cmath>
#include <iterator>
#include <set>
#include <unordered_map>
#include <vector>

using namespace Devourer;
using namespace Devourer::Sisters;
using namespace Acore::ChatCommands;

namespace
{
    // Owner, 2026-10-01: a new form, the Warp Stalker (shape 13), instead of the Baby Berserker (its ported model
    // crashes the client), and no cage: the Devourer stands in the summoning circle.
    constexpr uint32 ShapeIntro = 13;
    constexpr uint32 CheckInterval = 1000;       // ms between looks at the cage, the snacks and the ritual
    constexpr uint32 SnackDelay = 8000;          // ms before Wren tosses in more snacks once they are all gone
    constexpr uint32 SnackLifetime = 120000;     // ms a snack lives, dead or alive (its corpse waits to be eaten)
    constexpr uint32 SnacksPerToss = 3;
    constexpr uint32 TaleSpacing = 7000;         // ms between the lines of Hagatha's tale
    constexpr uint32 StrayLineEvery = 20000;     // ms between two "stay in the cage" lines
    constexpr uint32 CageLingers = 10000;        // ms the opened cage stays before it vanishes
    constexpr uint32 ReviveAfter = 2000;         // ms a Devourer that died in the cage lies there
    constexpr uint32 PestLifetime = 600000;      // ms a pest lives, dead or alive (its corpse waits to be eaten)

    struct Config
    {
        bool Enabled = true;
        uint8 Level = 5;
        uint32 ReturnCooldown = 1800;            // seconds between two .inbetween
    } config;

    // One stay in the In-Between, runtime only: what is saved is the quest log and character_devourer_inbetween.
    struct Visit
    {
        enum Step : uint8
        {
            None,          // nothing going on (outside, or freed and walking around)
            Pulling,       // the ritual has taken hold; the teleport follows
            Travelling,    // on the way to the In-Between
            Intro,         // asleep, waking, transformed: the beats below
            Caged,         // the chores
        };

        Step Now = None;
        uint32 Timer = 0;                         // ms to the next pull/intro beat
        uint8 Beat = 0;
        uint32 Check = 5000;                      // the first look waits a little after login
        uint32 Snacks = 0;                        // ms until more snacks may be tossed
        std::vector<ObjectGuid> Tossed;
        uint8 Tale = 0;                           // the line of the tale Hagatha says next (0 = not telling)
        uint32 TaleTimer = 0;
        uint32 StrayLine = 0;
        uint32 Revive = 0;
        uint32 CageGone = 0;
        ObjectGuid Cage;
        bool Returning = false;                   // came back with .inbetween: Wren greets it
        std::vector<ObjectGuid> Pests;            // the fourth chore: this Devourer's pests
        std::set<ObjectGuid> PestsEaten;          // the ones already counted
    };

    std::unordered_map<ObjectGuid::LowType, Visit> visits;

    Visit& VisitOf(Player* player) { return visits[player->GetGUID().GetCounter()]; }

    bool Freed(Player const* player) { return player->GetQuestRewardStatus(QuestTale); }
    bool InBetween(Player const* player) { return player->GetMapId() == InBetweenMap; }

    // Somewhere a ritual (or .inbetween) may take it from: never out of a fight, a flight, a dungeon or a battle.
    bool CanTravel(Player* player)
    {
        return player->IsInWorld() && player->IsAlive() && !player->IsInCombat() && !player->IsInFlight() &&
            !player->IsBeingTeleported() && !player->GetVehicle() && !player->GetTransport() &&
            !player->GetMap()->Instanceable();
    }

    Creature* Sister(Player* player, uint32 entry) { return player->FindNearestCreature(entry, 60.0f); }

    void Say(Player* player, uint32 entry, uint8 line, Milliseconds delay = 0ms)
    {
        if (Creature* sister = Sister(player, entry))
            if (sister->AI())
                sister->AI()->Talk(line, player, delay);
    }

    // Wren's voice from nowhere: her creature_text line, sent as her whisper (she is not on this map).
    void Whisper(Player* player, uint32 entry, uint8 line)
    {
        CreatureTemplate const* sister = sObjectMgr->GetCreatureTemplate(entry);
        std::string const text = sCreatureTextMgr->GetLocalizedChatString(entry, 0, line, 0,
            player->GetSession()->GetSessionDbLocaleIndex());
        if (!sister || text.empty())
            return;
        WorldPacket data;
        ChatHandler::BuildChatPacket(data, CHAT_MSG_MONSTER_WHISPER, LANG_UNIVERSAL, ObjectGuid::Empty, player->GetGUID(),
            text, 0, sister->Name);
        player->SendDirectMessage(&data);
    }

    // --- where it came from (character_devourer_inbetween) -----------------------------------------------------

    struct Origin
    {
        bool Known = false;
        uint32 MapId = 0;
        float X = 0, Y = 0, Z = 0, O = 0;
        uint32 NextVisit = 0;
    };

    Origin LoadOrigin(Player* player)
    {
        Origin origin;
        if (QueryResult result = CharacterDatabase.Query(
                "SELECT map, x, y, z, o, next_visit FROM character_devourer_inbetween WHERE guid = {}",
                player->GetGUID().GetCounter()))
        {
            Field* f = result->Fetch();
            origin.Known = true;
            origin.MapId = f[0].Get<uint32>();
            origin.X = f[1].Get<float>();
            origin.Y = f[2].Get<float>();
            origin.Z = f[3].Get<float>();
            origin.O = f[4].Get<float>();
            origin.NextVisit = f[5].Get<uint32>();
        }
        return origin;
    }

    void SaveOrigin(Player* player, uint32 nextVisit = 0)
    {
        CharacterDatabase.Execute(
            "INSERT INTO character_devourer_inbetween (guid, map, x, y, z, o, next_visit) VALUES ({}, {}, {}, {}, {}, {}, {}) "
            "ON DUPLICATE KEY UPDATE map = VALUES(map), x = VALUES(x), y = VALUES(y), z = VALUES(z), o = VALUES(o)"
            "{}",
            player->GetGUID().GetCounter(), player->GetMapId(), player->GetPositionX(), player->GetPositionY(),
            player->GetPositionZ(), player->GetOrientation(), nextVisit,
            nextVisit ? ", next_visit = VALUES(next_visit)" : "");
    }

    // --- the cage --------------------------------------------------------------------------------------------

    GameObject* Cage(Player* player, Visit& visit)
    {
        // Owner, 2026-10-01: no cage any more; the summoning circle (a fixed object on that spot) holds the Devourer
        // until the chores are done. Nothing is summoned; the "cage" names below stand for the circle.
        visit.Cage = ObjectGuid::Empty;
        return nullptr;
    }

    // Task 014: both sisters channel at the Devourer while the ritual holds it (stock visual beam).
    void Channel(Player* player, bool on)
    {
        for (uint32 entry : { NpcHagatha, NpcWren })
        {
            Creature* sister = Sister(player, entry);
            if (!sister)
                continue;
            if (on)
            {
                sister->SetFacingToObject(player);
                sister->CastSpell(player, SpellChannel, false);
            }
            else
                sister->InterruptNonMeleeSpells(false, SpellChannel);
        }
    }

    void PutBackInCage(Player* player)
    {
        player->NearTeleportTo(CageX, CageY, CageZ + 0.3f, player->GetOrientation());
    }

    void OpenCage(Player* player)
    {
        Visit& visit = VisitOf(player);
        visit.Now = Visit::None;
        if (GameObject* cage = ObjectAccessor::GetGameObject(*player, visit.Cage))
            cage->SetGoState(GO_STATE_ACTIVE);
        visit.CageGone = CageLingers;
        Channel(player, false);
        Say(player, NpcWren, WrenCageOpen);
        Say(player, NpcHagatha, HagathaCageOpen, 6s);
    }

    // --- the ritual and the intro ------------------------------------------------------------------------------

    void StartPull(Player* player, Visit& visit)
    {
        player->Dismount();
        player->RemoveAurasByType(SPELL_AURA_MOUNTED);
        player->SetControlled(true, UNIT_STATE_ROOT);
        player->CastSpell(player, VisualPull, true);
        Whisper(player, NpcWren, WrenFoundYou);
        visit.Now = Visit::Pulling;
        visit.Timer = 3000;
    }

    void Travel(Player* player, Visit& visit)
    {
        player->SetControlled(false, UNIT_STATE_ROOT);
        if (!CanTravel(player))
        {
            visit.Now = Visit::None;              // a fight broke out: the ritual tries again in a moment
            return;
        }
        SaveOrigin(player);
        visit.Now = player->TeleportTo(InBetweenMap, CageX, CageY, CageZ + 0.3f, CageO) ? Visit::Travelling : Visit::None;
    }

    void BeginStay(Player* player, Visit& visit)
    {
        Cage(player, visit);
        if (player->GetExactDist2d(CageX, CageY) > CageRadius)
            PutBackInCage(player);
        if (!Freed(player))
            Channel(player, true);
        // Never offered the first chore: the whole intro (also after a logout in the middle of it).
        if (player->GetQuestStatus(QuestFeeding) == QUEST_STATUS_NONE && !player->GetQuestRewardStatus(QuestFeeding))
        {
            visit.Now = Visit::Intro;
            visit.Beat = 0;
            visit.Timer = 0;
            return;
        }
        visit.Now = Visit::Caged;
        visit.Snacks = 0;
    }

    void OfferFirstChore(Player* player)
    {
        Quest const* quest = sObjectMgr->GetQuestTemplate(QuestFeeding);
        Creature* wren = Sister(player, NpcWren);
        if (quest && wren && player->CanTakeQuest(quest, false))
            player->PlayerTalkClass->SendQuestGiverQuestDetails(quest, wren->GetGUID(), true);
    }

    // One beat of the intro; returns the ms to the next one (0 = the intro is over).
    uint32 IntroBeat(Player* player, Visit& visit)
    {
        switch (visit.Beat++)
        {
            case 0:                                       // asleep in the cage
                player->CastSpell(player, VisualArrive, true);
                player->SetControlled(true, UNIT_STATE_ROOT);
                player->AddAura(VisualSleep, player);
                player->SetStandState(UNIT_STAND_STATE_SLEEP);
                return 3000;
            case 1:
                Say(player, NpcHagatha, HagathaHush);
                return 5000;
            case 2:                                       // it wakes
                player->RemoveAurasDueToSpell(VisualSleep);
                player->SetStandState(UNIT_STAND_STATE_STAND);
                Say(player, NpcWren, WrenAwake);
                return 6000;
            case 3:
                Say(player, NpcHagatha, HagathaAnother);
                return 7000;
            case 4:
                Say(player, NpcWren, WrenBeforeSpell);
                return 5000;
            case 5:                                       // Wren's spell: the Baby Berserker, worn at once
                if (Creature* wren = Sister(player, NpcWren))
                    wren->HandleEmoteCommand(EMOTE_ONESHOT_SPELL_CAST_OMNI);
                player->CastSpell(player, VisualTransform, true);
                sDevourer.Unlock(player, ShapeIntro, 0, true);
                return 2500;
            case 6:
                Say(player, NpcWren, WrenBaby);
                return 6000;
            case 7:
                Say(player, NpcHagatha, HagathaBerserker);
                return 8000;
            default:                                      // the chores begin
                Say(player, NpcWren, WrenChores);
                player->SetControlled(false, UNIT_STATE_ROOT);
                OfferFirstChore(player);
                return 0;
        }
    }

    // --- the chores --------------------------------------------------------------------------------------------

    void TossSnacks(Player* player, Visit& visit)
    {
        uint32 const killed = player->GetReqKillOrCastCurrentCount(QuestFeeding, NpcSnack);
        uint32 const count = std::max<uint32>(1, SnacksPerToss > killed ? SnacksPerToss - killed : 1);
        visit.Tossed.clear();
        for (uint32 i = 0; i < count; ++i)
        {
            float const angle = float(i) * 2.0f * float(M_PI) / float(count);
            // Only this Devourer sees its snacks (a second Devourer in the next cage gets its own).
            if (TempSummon* snack = player->SummonCreature(NpcSnack, CageX + 0.9f * std::cos(angle),
                    CageY + 0.9f * std::sin(angle), CageZ + 0.2f, angle + float(M_PI), TEMPSUMMON_TIMED_DESPAWN,
                    SnackLifetime, nullptr, true))
            {
                visit.Tossed.push_back(snack->GetGUID());
                if (snack->AI())
                    snack->AI()->AttackStart(player);
            }
        }
        Say(player, NpcWren, WrenSnacks);
    }

    void Chores(Player* player, Visit& visit)
    {
        if (player->GetQuestStatus(QuestFeeding) != QUEST_STATUS_INCOMPLETE)
            return;

        // "Devour one of them": the module remembers every corpse a Devourer has eaten.
        if (player->GetReqKillOrCastCurrentCount(QuestFeeding, CreditDevoured) < 1)
            for (ObjectGuid const& eaten : sDevourer.Get(player).Eaten)
                if (eaten.GetEntry() == NpcSnack)
                {
                    player->KilledMonsterCredit(CreditDevoured);
                    break;
                }

        bool anyLeft = false;                     // alive, or a corpse not yet eaten
        for (ObjectGuid const& guid : visit.Tossed)
            if (ObjectAccessor::GetCreature(*player, guid))
                anyLeft = true;
        if (anyLeft)
        {
            visit.Snacks = SnackDelay;
            return;
        }
        if (visit.Snacks > CheckInterval)
        {
            visit.Snacks -= CheckInterval;
            return;
        }
        if (player->GetQuestStatus(QuestFeeding) == QUEST_STATUS_INCOMPLETE)
            TossSnacks(player, visit);
    }

    // The fourth chore: every pest devoured counts. While none is left about (alive, or a corpse not yet eaten) and the
    // chore is not done, Wren's cages fill again with as many as are still missing, the hovering ones first.
    void PestChore(Player* player, Visit& visit)
    {
        if (player->GetQuestStatus(QuestPests) != QUEST_STATUS_INCOMPLETE || !player->IsAlive())
            return;
        Quest const* quest = sObjectMgr->GetQuestTemplate(QuestPests);
        if (!quest)
            return;
        uint32 const needed = quest->RequiredNpcOrGoCount[0];
        uint32 done = player->GetReqKillOrCastCurrentCount(QuestPests, CreditPest);
        for (ObjectGuid const& eaten : sDevourer.Get(player).Eaten)
            if ((eaten.GetEntry() == NpcPest || eaten.GetEntry() == NpcPestPerched) && done < needed &&
                visit.PestsEaten.insert(eaten).second)
            {
                player->KilledMonsterCredit(CreditPest);
                if (++done >= needed)
                    Say(player, NpcWren, WrenPestsGone);
            }
        if (done >= needed)
            return;

        for (ObjectGuid const& guid : visit.Pests)
            if (Creature* pest = ObjectAccessor::GetCreature(*player, guid))
                if (pest->IsAlive() || !visit.PestsEaten.count(guid))
                    return;
        visit.Pests.clear();
        uint32 left = needed - done;
        for (bool perched : { true, false })
            for (PestSpot const& spot : PestSpots)
                if (left && spot.Perched == perched)
                    if (TempSummon* pest = player->SummonCreature(perched ? NpcPestPerched : NpcPest, spot.X, spot.Y,
                            spot.Z, frand(0.0f, 2.0f * float(M_PI)), TEMPSUMMON_TIMED_DESPAWN, PestLifetime, nullptr,
                            true))
                    {
                        visit.Pests.push_back(pest->GetGUID());
                        --left;
                    }
    }

    void TellTale(Player* player, Visit& visit, uint32 diff)
    {
        if (!visit.Tale)
            return;
        if (visit.TaleTimer > diff)
        {
            visit.TaleTimer -= diff;
            return;
        }
        static uint8 const lines[] = { HagathaTale1, HagathaTale2, HagathaTale3, HagathaTale4 };
        if (visit.Tale <= std::size(lines))
        {
            Say(player, NpcHagatha, lines[visit.Tale - 1]);
            ++visit.Tale;
            visit.TaleTimer = TaleSpacing;
            return;
        }
        visit.Tale = 0;                           // heard to its end
        if (player->GetQuestStatus(QuestTale) == QUEST_STATUS_INCOMPLETE)
            player->KilledMonsterCredit(CreditTale);
    }

    void SendBack(Player* player)
    {
        Origin const origin = LoadOrigin(player);
        player->CastSpell(player, VisualPull, true);
        if (origin.Known && origin.MapId != InBetweenMap)
            player->TeleportTo(origin.MapId, origin.X, origin.Y, origin.Z, origin.O);
        else
            player->TeleportTo(player->m_homebindMapId, player->m_homebindX, player->m_homebindY,
                player->m_homebindZ, player->GetOrientation());
    }

    // --- the per-player clock ----------------------------------------------------------------------------------

    void Update(Player* player, uint32 diff)
    {
        Visit& visit = VisitOf(player);

        if (visit.CageGone)
        {
            if (visit.CageGone > diff)
                visit.CageGone -= diff;
            else
            {
                visit.CageGone = 0;
                if (GameObject* cage = ObjectAccessor::GetGameObject(*player, visit.Cage))
                    player->RemoveGameObject(cage, true);
                visit.Cage = ObjectGuid::Empty;
            }
        }

        if (visit.Revive)
        {
            if (visit.Revive > diff)
                visit.Revive -= diff;
            else
            {
                visit.Revive = 0;
                if (!player->IsAlive() && InBetween(player))
                {
                    player->ResurrectPlayer(1.0f);
                    player->SpawnCorpseBones();
                    PutBackInCage(player);
                    Say(player, NpcWren, WrenNoDying);
                }
            }
        }

        TellTale(player, visit, diff);

        switch (visit.Now)
        {
            case Visit::Pulling:
                if (visit.Timer > diff)
                    visit.Timer -= diff;
                else
                    Travel(player, visit);
                return;
            case Visit::Travelling:
                if (!InBetween(player) || !player->IsInWorld() || player->IsBeingTeleported())
                    return;
                if (Freed(player))
                {
                    visit.Now = Visit::None;      // came back with .inbetween
                    if (visit.Returning)
                        Say(player, NpcWren, WrenWelcomeBack, 2s);
                    visit.Returning = false;
                    return;
                }
                BeginStay(player, visit);
                return;
            case Visit::Intro:
                if (visit.Timer > diff)
                {
                    visit.Timer -= diff;
                    return;
                }
                visit.Timer = IntroBeat(player, visit);
                if (!visit.Timer)
                    visit.Now = Visit::Caged;
                return;
            default:
                break;
        }

        if (visit.StrayLine > diff)
            visit.StrayLine -= diff;
        else
            visit.StrayLine = 0;

        if (visit.Check > diff)
        {
            visit.Check -= diff;
            return;
        }
        visit.Check = CheckInterval;

        if (Freed(player))
        {
            visit.Now = Visit::None;
            if (InBetween(player))
                PestChore(player, visit);
            return;
        }

        if (!InBetween(player))
        {
            visit.Now = Visit::None;
            if (player->GetLevel() >= config.Level && CanTravel(player))
                StartPull(player, visit);         // level 5, or logged in at 5+ without having been there
            return;
        }

        if (!player->IsAlive() || !player->IsInWorld() || player->IsBeingTeleported())
            return;
        if (visit.Now == Visit::None)
        {
            BeginStay(player, visit);             // logged in inside the In-Between
            return;
        }

        // Caged: it stays in, it does its chores.
        Cage(player, visit);
        if (player->GetExactDist2d(CageX, CageY) > CageRadius)
        {
            PutBackInCage(player);
            if (!visit.StrayLine)
            {
                Say(player, NpcWren, WrenStayIn);
                visit.StrayLine = StrayLineEvery;
            }
        }
        Chores(player, visit);
    }
}

// --- the sisters ---------------------------------------------------------------------------------------------------

struct npc_devourer_witch_sister : public CreatureAI
{
    explicit npc_devourer_witch_sister(Creature* creature) : CreatureAI(creature) { }

    void UpdateAI(uint32 /*diff*/) override { }

    // Options the core does nothing with (OptionType 1, no next menu): the tale and the way back.
    void sGossipSelect(Player* player, uint32 menuId, uint32 optionId) override
    {
        if (!sDevourer.IsDevourer(player))
            return;
        if (menuId == MenuHagatha && optionId == OptionTale)
        {
            CloseGossipMenuFor(player);
            Visit& visit = VisitOf(player);
            if (!visit.Tale)
            {
                visit.Tale = 1;
                visit.TaleTimer = 0;
            }
        }
        else if ((menuId == MenuHagatha || menuId == MenuWren) && optionId == OptionBack)
        {
            CloseGossipMenuFor(player);
            if (Freed(player))
                SendBack(player);
        }
    }

    void sQuestAccept(Player* player, Quest const* quest) override
    {
        if (quest->GetQuestId() == QuestFeeding)
            VisitOf(player).Snacks = 0;           // the first snacks come at the next look
        else if (quest->GetQuestId() == QuestPests)
        {
            // "Here, I'll help you with it": Wren's spell turns it into a Biletoad; the pests come at the next look.
            Talk(WrenPestSpell, player);
            me->HandleEmoteCommand(EMOTE_ONESHOT_SPELL_CAST_OMNI);
            player->CastSpell(player, VisualTransform, true);
            sDevourer.Unlock(player, ShapeBiletoad, 0, true);
            Talk(WrenPestToad, player, 4s);
            VisitOf(player).Pests.clear();
        }
    }

    void sQuestReward(Player* player, Quest const* quest, uint32 /*opt*/) override
    {
        if (quest->GetQuestId() == QuestTale)
            OpenCage(player);
    }
};

// --- player hooks ----------------------------------------------------------------------------------------------------

class devourer_sisters_player : public PlayerScript
{
public:
    devourer_sisters_player() : PlayerScript("devourer_sisters_player") { }

    void OnPlayerLogin(Player* player) override
    {
        if (config.Enabled && sDevourer.IsDevourer(player))
            VisitOf(player) = Visit();            // the first look comes a few seconds after login
    }

    void OnPlayerLogout(Player* player) override
    {
        visits.erase(player->GetGUID().GetCounter());
    }

    void OnPlayerUpdate(Player* player, uint32 diff) override
    {
        if (config.Enabled && sDevourer.IsDevourer(player))
            Update(player, diff);
    }

    void OnPlayerJustDied(Player* player) override
    {
        if (config.Enabled && sDevourer.IsDevourer(player) && InBetween(player) && !Freed(player))
            VisitOf(player).Revive = ReviveAfter;
    }

    // The second chore: roar at Wren.
    void OnPlayerTextEmote(Player* player, uint32 textEmote, uint32 /*emoteNum*/, ObjectGuid /*guid*/) override
    {
        if (!config.Enabled || textEmote != TEXT_EMOTE_ROAR || !sDevourer.IsDevourer(player) || !InBetween(player))
            return;
        if (player->GetQuestStatus(QuestTrick) != QUEST_STATUS_INCOMPLETE)
            return;
        if (!player->FindNearestCreature(NpcWren, 15.0f))
            return;
        player->KilledMonsterCredit(CreditRoar);
        Say(player, NpcWren, WrenRoar);
    }
};

class devourer_sisters_world : public WorldScript
{
public:
    devourer_sisters_world() : WorldScript("devourer_sisters_world") { }

    void OnAfterConfigLoad(bool /*reload*/) override
    {
        config.Enabled = sConfigMgr->GetOption<bool>("Devourer.InBetween.Enable", true);
        config.Level = uint8(std::clamp<uint32>(sConfigMgr->GetOption<uint32>("Devourer.InBetween.Level", 5), 1, 80));
        config.ReturnCooldown = sConfigMgr->GetOption<uint32>("Devourer.InBetween.ReturnCooldown", 1800);
    }
};

// --- .inbetween: a freed Devourer goes back to the sisters (stopgap; the PR proposes a spell) ----------------------

class devourer_sisters_commands : public CommandScript
{
public:
    devourer_sisters_commands() : CommandScript("devourer_sisters_commands") { }

    ChatCommandTable GetCommands() const override
    {
        static ChatCommandTable commandTable = { { "inbetween", HandleInBetween, SEC_PLAYER, Console::No } };
        return commandTable;
    }

    static bool HandleInBetween(ChatHandler* handler)
    {
        Player* player = handler->GetSession()->GetPlayer();
        if (!config.Enabled || !sDevourer.IsDevourer(player))
        {
            handler->SendSysMessage("Only a Devourer knows the way into the In-Between.");
            return true;
        }
        if (!Freed(player))
        {
            handler->SendSysMessage("The sisters have not let you go yet.");
            return true;
        }
        if (InBetween(player))
        {
            handler->SendSysMessage("You are already in the In-Between.");
            return true;
        }
        if (!CanTravel(player))
        {
            handler->SendSysMessage("Not now: the way opens only out of a fight, on solid ground and outside dungeons.");
            return true;
        }
        uint32 const now = uint32(GameTime::GetGameTime().count());
        Origin const origin = LoadOrigin(player);
        if (origin.NextVisit > now)
        {
            handler->PSendSysMessage("The way into the In-Between is still closed ({} min).",
                (origin.NextVisit - now + 59) / 60);
            return true;
        }
        SaveOrigin(player, now + config.ReturnCooldown);
        Visit& visit = VisitOf(player);
        visit.Now = Visit::Travelling;
        visit.Returning = true;
        player->CastSpell(player, VisualPull, true);
        if (!player->TeleportTo(InBetweenMap, ArriveX, ArriveY, ArriveZ + 0.3f, ArriveO))
            visit = Visit();
        return true;
    }
};

void AddSC_devourer_sisters()
{
    RegisterCreatureAI(npc_devourer_witch_sister);
    new devourer_sisters_player();
    new devourer_sisters_world();
    new devourer_sisters_commands();
}
