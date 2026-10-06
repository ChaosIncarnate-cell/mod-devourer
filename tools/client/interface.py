"""The interface side of class 10: small changes applied at build time to the client's own GlueXML/FrameXML files
(read from the client's archives, never committed). Everything written here is ours; the patched files only
exist in the built MPQ.

GlueXML (character creation):
  CharacterCreate.xml   an 11th class button (3.3.5a has 10, one per class; with class 10 there are 11)
  CharacterCreate.lua   MAX_CLASSES_PER_RACE 11, the Devourer's icon (its own texture, not a cell of
                        Blizzard's icon sheet), appended at the end of the file
  GlueStrings.lua       the class description, role lines and the "not for this race" tooltip
FrameXML (in game):
  Constants.lua         class colour and icon coordinates, so class-keyed lookups (who list, chat, LFG,
                        arena frames ...) find the Devourer
  WorldStateFrame.lua   the battleground score board's class icon table
  FrameXML.toc          loads DevourerMenu.lua (ours, tools/client/lua/) last: the shape menu and the Anima colour
AddOns:
  Blizzard_RaidUI       a Devourer in a raid no longer breaks the raid frame (no class button of its own)
  Blizzard_Calendar     the same for an event's invite list
"""
from __future__ import annotations

import re
from pathlib import Path

TOKEN = "DEVOURER"
COLOR = (0.72, 0.47, 0.18)                 # the bronze of the CoA emblem
ICON_PATH = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-Devourer"
# The playable-races thread's four races (ChrRaces 22-26): their creation icons, one 64x64 cell each, male on top.
RACE_ICON_PATH = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-NewRaces"
RACE_ICON_SOURCE = Path(__file__).resolve().parent / "lua" / "UI-CharacterCreate-NewRaces.png"
NEW_RACE_BUTTONS = 5                       # 22 Worgen, 23 Vulpera, 24 Dracthyr, 25 Sethrak, 26 Dracthyr (Horde)
# A cell of Blizzard's 4x4 class icon sheets that no class uses: the Devourer shows an empty icon there
# (in-game frames) instead of breaking the frame. Its own icon art is only on the creation screen for now.
FREE_CELL = (0.5, 0.7421875, 0.5, 0.75)
MARK = "-- mod-devourer (tools/client/build_client_patch.py)"

DESCRIPTION = (
    "Devourers are aberrations touched by the void, shapeshifters that become what they eat. They devour the "
    "creatures they slay and gather their anima, the essence they were born from, which lets them change "
    "their very flesh.|n|nA Devourer that tastes something new can "
    "take its shape: a Sethrak of the dunes, a void-scarred Berserker and more. Every shape brings its own "
    "abilities. Gluttons grow huge and hard to kill, Skinchangers flow from shape to shape in the middle of "
    "a fight, and the Brood hatch young that fight and feed for their mother.")
INFO_LINES = [
    "- Role: Tank, Damage",
    "- Takes on the shapes of what it has eaten, each with its own abilities.",
    "- Devours slain creatures to feed its Anima.",
    "- Uses Anima as a resource: shifting into a shape costs it.",
]


class PatchError(Exception):
    pass


def _lua_str(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


# --- GlueXML ----------------------------------------------------------------------------------------------
def character_create_xml(text: str) -> tuple[str, str]:
    if re.search(r'name="CharacterCreateClassButton11"', text):
        return add_race_buttons(text), "already has an 11th class button (kept as it is), race buttons 12-16"
    m = re.search(r'<CheckButton\s[^>]*name="CharacterCreateClassButton10"[^>]*?(/>|>.*?</CheckButton>)', text, re.S)
    if not m:
        raise PatchError("CharacterCreate.xml: CharacterCreateClassButton10 not found (a replaced character "
                         "creation screen?)")
    tag = m.group(0)
    inherits = re.search(r'inherits="([^"]+)"', tag.split(">", 1)[0])
    if not inherits:
        raise PatchError("CharacterCreate.xml: CharacterCreateClassButton10 has no template")
    line_start = text.rfind("\n", 0, m.start()) + 1
    indent = re.match(r"[ \t]*", text[line_start:m.start()]).group(0)
    inner = indent + ("\t" if "\t" in indent or not indent else "    ")
    button = (f'\n{indent}<!-- mod-devourer: class 10, the Devourer -->'
              f'\n{indent}<CheckButton name="CharacterCreateClassButton11" inherits="{inherits.group(1)}" id="11">'
              f'\n{inner}<Anchors>'
              f'\n{inner}\t<Anchor point="LEFT" relativeTo="CharacterCreateClassButton10" relativePoint="RIGHT" x="6" y="0"/>'
              f'\n{inner}</Anchors>'
              f'\n{indent}</CheckButton>')
    text = text[:m.end()] + button + text[m.end():]
    return add_race_buttons(text), f"button 11 added after button 10 ({inherits.group(1)}), race buttons 12-16"


def add_race_buttons(text: str) -> str:
    """CharacterCreateRaceButton12-16 for the new races, right after button 11 (RACES_LUA places them)."""
    live = re.sub(r"<!--.*?-->", lambda c: " " * len(c.group(0)), text, flags=re.S)   # commented-out buttons don't count
    if 'name="CharacterCreateRaceButton12"' in live:
        return text
    m = re.search(r'<CheckButton\s[^>]*name="CharacterCreateRaceButton11"[^>]*?(/>|>.*?</CheckButton>)', live, re.S)
    if not m:
        if "CharacterCreateRaceButton" in live:
            raise PatchError("CharacterCreate.xml: race buttons without CharacterCreateRaceButton11 (a replaced "
                             "character creation screen?): the new races would have no buttons")
        return text                                      # no race buttons at all (a test stand-in): nothing to add
    inherits = re.search(r'inherits="([^"]+)"', m.group(0).split(">", 1)[0]).group(1)
    line_start = text.rfind("\n", 0, m.start()) + 1
    indent = re.match(r"[ \t]*", text[line_start:m.start()]).group(0)
    nl = "\r\n" if "\r\n" in text else "\n"
    buttons = "".join(f'{nl}{indent}<CheckButton name="CharacterCreateRaceButton{i}" inherits="{inherits}" id="{i}" '
                      f'hidden="true"/>' for i in range(12, 12 + NEW_RACE_BUTTONS))
    return text[:m.end()] + f"{nl}{indent}<!-- mod-devourer: the new races (ChrRaces 22-26) -->" + buttons + text[m.end():]


GLUE_LUA = MARK + r"""
-- Class 10, the Devourer: an 11th class button (CharacterCreate.xml) and its own icon texture.
if ( (MAX_CLASSES_PER_RACE or 0) < 11 ) then
	MAX_CLASSES_PER_RACE = 11;
end
if ( CLASS_ICON_TCOORDS ) then
	CLASS_ICON_TCOORDS["DEVOURER"] = {0, 1, 0, 1};
end

local DEVOURER_ICON = "@ICON@";

local function Devourer_SetIcon(texture, isDevourer, coords)
	if ( not texture ) then
		return;
	end
	if ( not texture.devourerDefault ) then
		texture.devourerDefault = texture:GetTexture() or "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-Classes";
	end
	if ( isDevourer ) then
		texture:SetTexture(DEVOURER_ICON);
		texture:SetTexCoord(0, 1, 0, 1);
	else
		texture:SetTexture(texture.devourerDefault);
		if ( coords ) then
			texture:SetTexCoord(coords[1], coords[2], coords[3], coords[4]);
		end
	end
end

-- The HD client's row (patch-k) chains ... 9 -> 10 -> 6 and anchors button 11 to button 6, but button 11 is
-- defined before button 6, so that anchor fails and the 11th class (Druid, once the Devourer is class 10) never
-- shows. Re-chain at runtime, only for that layout: ... 9 -> 6 (Death Knight) -> 11 (Druid) -> 10 (Devourer).
local devourerRowFixed;
local function Devourer_FixClassRow()
	if ( devourerRowFixed ) then
		return;
	end
	devourerRowFixed = true;
	local b6, b9, b10, b11 = CharacterCreateClassButton6, CharacterCreateClassButton9, CharacterCreateClassButton10, CharacterCreateClassButton11;
	if ( not (b6 and b9 and b10 and b11) ) then
		return;
	end
	local _, relativeTo = b6:GetPoint(1);
	if ( relativeTo ~= b10 ) then
		return;
	end
	local point, _, relativePoint, x, y = b10:GetPoint(1);
	for _, pair in ipairs({ {b6, b9}, {b11, b6}, {b10, b11} }) do
		pair[1]:ClearAllPoints();
		pair[1]:SetPoint(point, pair[2], relativePoint, x, y);
	end
end

if ( CharacterCreateEnumerateClasses ) then
	local Devourer_EnumerateClasses = CharacterCreateEnumerateClasses;
	function CharacterCreateEnumerateClasses(...)
		Devourer_FixClassRow();
		Devourer_EnumerateClasses(...);
		local count = select("#", ...) / 3;
		if ( count > MAX_CLASSES_PER_RACE ) then
			return;
		end
		for index = 1, count do
			local token = strupper(select(index * 3 - 1, ...) or "");
			local coords = CLASS_ICON_TCOORDS and CLASS_ICON_TCOORDS[token];
			Devourer_SetIcon(_G["CharacterCreateClassButton"..index.."NormalTexture"], token == "DEVOURER", coords);
			Devourer_SetIcon(_G["CharacterCreateClassButton"..index.."PushedTexture"], token == "DEVOURER", coords);
		end
	end
end

if ( SetCharacterClass ) then
	local Devourer_SetCharacterClass = SetCharacterClass;
	function SetCharacterClass(id)
		Devourer_SetCharacterClass(id);
		local _, token = GetSelectedClass();
		token = token and strupper(token);
		Devourer_SetIcon(CharacterCreateClassIcon, token == "DEVOURER", token and CLASS_ICON_TCOORDS and CLASS_ICON_TCOORDS[token]);
	end
end
"""


RACES_LUA = MARK + r"""
-- The four new races (ChrRaces 22-26, the playable-races thread): five more race buttons (CharacterCreate.xml) with
-- their own icon sheet. Buttons past the stock eleven are laid out under the last button of their faction.
if ( (MAX_RACES or 0) < 16 ) then
	MAX_RACES = 16;
end
local NEW_RACE_ICONS = "@RACEICON@";
local NEW_RACE_TCOORDS = {
	["WORGEN_MALE"]		= {0, 0.25, 0, 0.5},	["WORGEN_FEMALE"]	= {0, 0.25, 0.5, 1},
	["VULPERA_MALE"]	= {0.25, 0.5, 0, 0.5},	["VULPERA_FEMALE"]	= {0.25, 0.5, 0.5, 1},
	["DRACTHYR_MALE"]	= {0.5, 0.75, 0, 0.5},	["DRACTHYR_FEMALE"]	= {0.5, 0.75, 0.5, 1},
	["SETHRAK_MALE"]	= {0.75, 1, 0, 0.5},	["SETHRAK_FEMALE"]	= {0.75, 1, 0.5, 1},
};
if ( RACE_ICON_TCOORDS ) then
	for key, coords in pairs(NEW_RACE_TCOORDS) do
		RACE_ICON_TCOORDS[key] = coords;
	end
end

local function NewRaces_Layout(...)
	local gender = (GetSelectedSex() == SEX_MALE) and "MALE" or "FEMALE";
	-- the last stock button of each faction: whatever button ends each column in the stock layout
	local lastAlliance, lastHorde;
	for i = 1, 11 do
		local b = _G["CharacterCreateRaceButton"..i];
		if ( b and b:IsShown() ) then
			local _, side = GetFactionForRace(i);
			if ( side == "Horde" ) then lastHorde = b; else lastAlliance = b; end
		end
	end
	lastAlliance = lastAlliance or CharacterCreateRaceButton5;
	lastHorde = lastHorde or CharacterCreateRaceButton11;
	local index = 1;
	for i = 1, select("#", ...), 3 do
		local token = strupper(select(i + 1, ...) or "");
		local button = _G["CharacterCreateRaceButton"..index];
		if ( button ) then
			local normal = _G["CharacterCreateRaceButton"..index.."NormalTexture"];
			local pushed = _G["CharacterCreateRaceButton"..index.."PushedTexture"];
			local coords = NEW_RACE_TCOORDS[token.."_"..gender];
			if ( not normal.newRacesDefault ) then
				normal.newRacesDefault = normal:GetTexture();
				pushed.newRacesDefault = pushed:GetTexture();
			end
			if ( coords ) then
				normal:SetTexture(NEW_RACE_ICONS);
				pushed:SetTexture(NEW_RACE_ICONS);
			else
				normal:SetTexture(normal.newRacesDefault);
				pushed:SetTexture(pushed.newRacesDefault);
				coords = RACE_ICON_TCOORDS[token.."_"..gender];
			end
			if ( coords ) then
				normal:SetTexCoord(coords[1], coords[2], coords[3], coords[4]);
				pushed:SetTexCoord(coords[1], coords[2], coords[3], coords[4]);
			end
			if ( index > 11 ) then
				local _, side = GetFactionForRace(index);       -- the second value is not localized
				local horde = (side == "Horde");
				local above = horde and lastHorde or lastAlliance;
				button:ClearAllPoints();
				button:SetPoint("TOPLEFT", above, "BOTTOMLEFT", 0, -20);
				button:Show();
				if ( horde ) then lastHorde = button; else lastAlliance = button; end
			end
		end
		index = index + 1;
	end
end

if ( CharacterCreateEnumerateRaces ) then
	local stock = CharacterCreateEnumerateRaces;
	CharacterCreateEnumerateRaces = function(...)
		stock(...);
		NewRaces_Layout(...);
	end
end
"""


def character_create_lua(text: str) -> tuple[str, str]:
    for name in ("CharacterCreateEnumerateClasses", "SetCharacterClass", "MAX_CLASSES_PER_RACE"):
        if name not in text:
            raise PatchError(f"CharacterCreate.lua: {name} not found (a replaced character creation screen?)")
    block = GLUE_LUA.replace("@ICON@", ICON_PATH.replace("\\", "\\\\"))
    races = RACES_LUA.replace("@RACEICON@", RACE_ICON_PATH.replace("\\", "\\\\"))
    return text.rstrip() + "\n\n" + block + "\n" + races, "11 classes, the Devourer's icon, 5 new race buttons"


def glue_strings(text: str) -> tuple[str, str]:
    lines = [MARK, f"CLASS_{TOKEN} = {_lua_str(DESCRIPTION)};", f"CLASS_{TOKEN}_FEMALE = CLASS_{TOKEN};"]
    lines += [f"CLASS_INFO_{TOKEN}{i} = {_lua_str(s)};" for i, s in enumerate(INFO_LINES)]
    lines += [f"{TOKEN}_DISABLED = {_lua_str('Devourer' + chr(10) + 'You must choose a different race to be this class.')};"]
    return text.rstrip() + "\n\n" + "\n".join(lines) + "\n", "class description and tooltips"


# --- FrameXML ---------------------------------------------------------------------------------------------
def constants_lua(text: str) -> tuple[str, str]:
    if "RAID_CLASS_COLORS" not in text:
        raise PatchError("FrameXML Constants.lua: RAID_CLASS_COLORS not found")
    r, g, b = COLOR
    block = "\n".join([
        MARK,
        "-- Class 10, the Devourer. Not in CLASS_SORT_ORDER: the raid and calendar frames have one button per class",
        "-- listed there and no 11th button.",
        "if ( RAID_CLASS_COLORS ) then",
        f"\tRAID_CLASS_COLORS[\"{TOKEN}\"] = {{ r = {r}, g = {g}, b = {b} }};",
        "end",
        "if ( CLASS_ICON_TCOORDS ) then",
        f"\tCLASS_ICON_TCOORDS[\"{TOKEN}\"] = {{{', '.join(map(str, FREE_CELL))}}};",
        "end",
    ])
    return text.rstrip() + "\n\n" + block + "\n", "class colour, class icon coordinates"


def world_state_frame_lua(text: str) -> tuple[str, str]:
    if "CLASS_BUTTONS" not in text:
        return text, "no CLASS_BUTTONS table (unchanged)"
    block = "\n".join([MARK, "if ( CLASS_BUTTONS ) then",
                       f"\tCLASS_BUTTONS[\"{TOKEN}\"] = {{{', '.join(map(str, FREE_CELL))}}};", "end"])
    return text.rstrip() + "\n\n" + block + "\n", "score board class icon"


# --- load-on-demand Blizzard addons -------------------------------------------------------------------------
RAID_LUA = MARK + """
-- Class 10 has no class button in the raid frame (one per CLASS_SORT_ORDER class). Its members are shown in their
-- groups but counted under no class: the per-class lists are rebuilt for known classes only, so the Devourer's is
-- made on first use instead of failing in tinsert(nil).
if ( RAID_SUBGROUP_LISTS ) then
	setmetatable(RAID_SUBGROUP_LISTS, { __index = function(lists, key)
		if ( key == "DEVOURER" ) then
			local list = {};
			rawset(lists, key, list);
			return list;
		end
	end });
end
"""

CALENDAR_LUA = MARK + """
-- Class 10 in an event's invite list: counted like any class (no class button shows it, see CLASS_SORT_ORDER).
if ( CalendarClassData and CalendarClassData["WARRIOR"] and not CalendarClassData["DEVOURER"] ) then
	local counts = {};
	for status in pairs(CalendarClassData["WARRIOR"].counts) do
		counts[status] = 0;
	end
	CalendarClassData["DEVOURER"] = { name = nil, tcoords = CLASS_ICON_TCOORDS and CLASS_ICON_TCOORDS["DEVOURER"], counts = counts };
end
"""


def raid_ui_lua(text: str) -> tuple[str, str]:
    if "RAID_SUBGROUP_LISTS" not in text:
        return text, "no RAID_SUBGROUP_LISTS (unchanged)"
    return text.rstrip() + "\n\n" + RAID_LUA, "raid frame accepts a Devourer"


def calendar_lua(text: str) -> tuple[str, str]:
    if not re.search(r"^local CalendarClassData\b", text, re.M):
        return text, "no CalendarClassData (unchanged)"
    return text.rstrip() + "\n\n" + CALENDAR_LUA, "invite lists accept a Devourer"


MENU_LUA = Path(__file__).resolve().parent / "lua" / "DevourerMenu.lua"
MENU_PATH = "Interface\\FrameXML\\DevourerMenu.lua"


def frame_toc(text: str) -> tuple[str, str]:
    if "DevourerMenu.lua" in text:
        return text, "already loads DevourerMenu.lua (kept as it is)"
    nl = "\r\n" if "\r\n" in text else "\n"
    return text.rstrip() + nl + "DevourerMenu.lua" + nl, "loads the shape menu (DevourerMenu.lua)"


# Files that are ours from start to end: archive path -> source file.
EXTRA_FILES = {MENU_PATH: MENU_LUA}

# archive path -> (patch function, required)
PATCHES = {
    "Interface\\GlueXML\\CharacterCreate.xml": (character_create_xml, True),
    "Interface\\GlueXML\\CharacterCreate.lua": (character_create_lua, True),
    "Interface\\GlueXML\\GlueStrings.lua": (glue_strings, True),
    "Interface\\FrameXML\\Constants.lua": (constants_lua, True),
    "Interface\\FrameXML\\WorldStateFrame.lua": (world_state_frame_lua, False),
    "Interface\\FrameXML\\FrameXML.toc": (frame_toc, True),
    "Interface\\AddOns\\Blizzard_RaidUI\\Blizzard_RaidUI.lua": (raid_ui_lua, False),
    "Interface\\AddOns\\Blizzard_Calendar\\Blizzard_Calendar.lua": (calendar_lua, False),
}
