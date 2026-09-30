-- mod-devourer: the Devourer's shape menu (our own code; tools/client/build_client_patch.py puts it into
-- patch-Z.MPQ as Interface\FrameXML\DevourerMenu.lua and loads it last from FrameXML.toc).
--
-- A small draggable button (next to the minimap at first) opens a window with the base kit (Rush, Concentrate,
-- Devour), "True form" and every shape the Devourer has eaten; a click on a shape shifts into it, the button
-- on its right switches the colouring. The server sends the list as addon messages (prefix DVR, see
-- Mgr::SendMenu in src/DevourerMgr.cpp); the menu asks for it with ".devour menu" at login.
-- Anima is the rage bar: for a Devourer it is coloured like the void.
--
-- /devour           opens or closes the menu
-- /devour <words>   the same as the chat command ".devour <words>"

local PREFIX = "DVR";
local MAX_SHAPES = 16;
local ROW_HEIGHT = 30;
local ANIMA_COLOR = { r = 0.58, g = 0.29, b = 0.95 };
local BASE_SPELLS = { 9100990, 9100992, 9100001 };      -- Rush, Concentrate, Devour (Quick Devour when talented)
local QUICK_DEVOUR = 9100032;

local shapes, pending = {}, nil;
local animaCost = 0;
local dirty = false;

local function IsDevourer(unit)
	local _, token = UnitClass(unit);
	return token == "DEVOURER";
end

local function Server(words)
	SendChatMessage(".devour" .. (words ~= "" and (" " .. words) or ""), "SAY");
end

-- Anima: the rage bar in the void's colour, on every frame that shows a Devourer.
hooksecurefunc("UnitFrameManaBar_UpdateType", function(manaBar)
	if ( manaBar and manaBar.unit and UnitExists(manaBar.unit) and IsDevourer(manaBar.unit)
			and UnitPowerType(manaBar.unit) == 1 ) then
		manaBar:SetStatusBarColor(ANIMA_COLOR.r, ANIMA_COLOR.g, ANIMA_COLOR.b);
	end
end);

-- --- the window -------------------------------------------------------------------------------------------
local menu = CreateFrame("Frame", "DevourerMenuFrame", UIParent);
menu:SetWidth(230);
menu:SetHeight(120);
menu:SetPoint("TOPRIGHT", Minimap, "BOTTOMLEFT", -10, -10);
menu:SetBackdrop({
	bgFile = "Interface\\DialogFrame\\UI-DialogBox-Background",
	edgeFile = "Interface\\DialogFrame\\UI-DialogBox-Border",
	tile = true, tileSize = 32, edgeSize = 24,
	insets = { left = 6, right = 6, top = 6, bottom = 6 },
});
menu:SetMovable(true);
menu:EnableMouse(true);
menu:SetClampedToScreen(true);
menu:RegisterForDrag("LeftButton");
menu:SetScript("OnDragStart", function(self) if ( not InCombatLockdown() ) then self:StartMoving(); end end);
menu:SetScript("OnDragStop", function(self) self:StopMovingOrSizing(); end);
menu:Hide();

local title = menu:CreateFontString(nil, "OVERLAY", "GameFontNormal");
title:SetPoint("TOP", 0, -14);
title:SetText("Devourer");

local close = CreateFrame("Button", nil, menu, "UIPanelCloseButton");
close:SetPoint("TOPRIGHT", -2, -2);

local costText = menu:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall");
costText:SetPoint("TOP", title, "BOTTOM", 0, -4);

local function SpellTooltip(self)
	if ( self.spellId ) then
		GameTooltip:SetOwner(self, "ANCHOR_RIGHT");
		GameTooltip:SetHyperlink("spell:" .. self.spellId);
		if ( self.extra ) then
			GameTooltip:AddLine(self.extra, 0.58, 0.29, 0.95, true);
		end
		GameTooltip:Show();
	end
end

-- The base kit: three spell buttons.
local base = {};
for i = 1, #BASE_SPELLS do
	local b = CreateFrame("Button", "DevourerMenuBase" .. i, menu, "SecureActionButtonTemplate");
	b:SetWidth(34);
	b:SetHeight(34);
	b:SetPoint("TOPLEFT", 20 + (i - 1) * 42, -48);
	b:SetAttribute("type", "spell");
	b.icon = b:CreateTexture(nil, "ARTWORK");
	b.icon:SetAllPoints();
	b:SetHighlightTexture("Interface\\Buttons\\ButtonHilight-Square", "ADD");
	b:SetScript("OnEnter", SpellTooltip);
	b:SetScript("OnLeave", GameTooltip_Hide);
	base[i] = b;
end

-- True form: leaves whatever shape is worn.
local trueForm = CreateFrame("Button", "DevourerMenuTrueForm", menu, "SecureActionButtonTemplate,UIPanelButtonTemplate");
trueForm:SetWidth(64);
trueForm:SetHeight(24);
trueForm:SetPoint("TOPRIGHT", -18, -53);
trueForm:SetText("True form");
trueForm:SetAttribute("type", "macro");

-- One row per shape: the shape (a secure spell button) and its colouring.
local rows = {};
for i = 1, MAX_SHAPES do
	local r = CreateFrame("Button", "DevourerMenuShape" .. i, menu, "SecureActionButtonTemplate");
	r:SetWidth(126);
	r:SetHeight(ROW_HEIGHT - 2);
	r:SetPoint("TOPLEFT", 16, -90 - (i - 1) * ROW_HEIGHT);
	r:SetAttribute("type", "spell");
	r.icon = r:CreateTexture(nil, "ARTWORK");
	r.icon:SetWidth(ROW_HEIGHT - 4);
	r.icon:SetHeight(ROW_HEIGHT - 4);
	r.icon:SetPoint("LEFT", 2, 0);
	r.name = r:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall");
	r.name:SetPoint("LEFT", r.icon, "RIGHT", 6, 0);
	r.name:SetJustifyH("LEFT");
	r.worn = r:CreateTexture(nil, "BACKGROUND");
	r.worn:SetAllPoints();
	r.worn:SetTexture(ANIMA_COLOR.r, ANIMA_COLOR.g, ANIMA_COLOR.b, 0.25);
	r:SetHighlightTexture("Interface\\QuestFrame\\UI-QuestTitleHighlight", "ADD");
	r:SetScript("OnEnter", SpellTooltip);
	r:SetScript("OnLeave", GameTooltip_Hide);

	-- Colouring: left click the next one, right click the one before (".devour skin <name>").
	local c = CreateFrame("Button", nil, menu, "UIPanelButtonTemplate");
	c:SetWidth(66);
	c:SetHeight(20);
	c:SetPoint("LEFT", r, "RIGHT", 4, 0);
	c:RegisterForClicks("LeftButtonUp", "RightButtonUp");
	c:SetScript("OnClick", function(self, button)
		local shape = self.shape;
		if ( not shape or #shape.skins < 2 ) then
			return;
		end
		local at = 1;
		for n, skin in ipairs(shape.skins) do
			if ( skin == shape.wearing ) then
				at = n;
			end
		end
		at = (button == "RightButton") and (at - 2) % #shape.skins + 1 or at % #shape.skins + 1;
		Server("skin " .. shape.skins[at]);
	end);
	c:SetScript("OnEnter", function(self)
		if ( self.shape ) then
			GameTooltip:SetOwner(self, "ANCHOR_RIGHT");
			GameTooltip:AddLine("Colouring: " .. self.shape.wearing);
			GameTooltip:AddLine(table.concat(self.shape.skins, ", "), 1, 1, 1, true);
			if ( #self.shape.skins > 1 ) then
				GameTooltip:AddLine("Left click: next. Right click: back.", 0.7, 0.7, 0.7);
			end
			GameTooltip:Show();
		end
	end);
	c:SetScript("OnLeave", GameTooltip_Hide);
	r.colour = c;
	rows[i] = r;
end

local empty = menu:CreateFontString(nil, "OVERLAY", "GameFontDisableSmall");
empty:SetPoint("TOPLEFT", 20, -96);
empty:SetWidth(190);
empty:SetJustifyH("LEFT");
empty:SetText("No shape yet. Devour a creature you have slain to take its shape.");

-- Buttons and their spells can only change out of combat; a change during a fight waits for its end.
local function Refresh()
	if ( InCombatLockdown() ) then
		dirty = true;
		return;
	end
	dirty = false;

	for i, id in ipairs(BASE_SPELLS) do
		local b = base[i];
		if ( id == 9100001 and not GetSpellInfo(GetSpellInfo(id) or "") and GetSpellInfo(QUICK_DEVOUR) ) then
			id = QUICK_DEVOUR;
		end
		local name, _, icon = GetSpellInfo(id);
		b.spellId = id;
		b:SetAttribute("spell", name);
		b.icon:SetTexture(icon);
	end

	costText:SetText(animaCost > 0 and ("A shift costs " .. animaCost .. " Anima") or "");

	local cancel, anyWorn = {}, false;
	for i, r in ipairs(rows) do
		local shape = shapes[i];
		if ( shape ) then
			local name, _, icon = GetSpellInfo(shape.spell);
			r.spellId = shape.spell;
			r.extra = animaCost > 0 and ("Costs " .. animaCost .. " Anima.") or nil;
			r:SetAttribute("spell", name);
			r.icon:SetTexture(icon);
			r.name:SetText((string.gsub(name or "?", " Form$", "")));
			if ( shape.worn ) then
				r.worn:Show();
				anyWorn = true;
			else
				r.worn:Hide();
			end
			r.colour.shape = shape;
			r.colour:SetText(shape.wearing);
			if ( #shape.skins > 1 ) then
				r.colour:Enable();
			else
				r.colour:Disable();
			end
			r:Show();
			r.colour:Show();
			if ( name ) then
				table.insert(cancel, "/cancelaura " .. name);
			end
		else
			r:Hide();
			r.colour:Hide();
		end
	end
	trueForm:SetAttribute("macrotext", table.concat(cancel, "\n"));
	if ( anyWorn ) then
		trueForm:Enable();
	else
		trueForm:Disable();
	end

	if ( #shapes == 0 ) then
		empty:Show();
	else
		empty:Hide();
	end
	menu:SetHeight(104 + math.max(#shapes, 1) * ROW_HEIGHT);
end

-- --- the button that opens it -----------------------------------------------------------------------------
local toggle = CreateFrame("Button", "DevourerMenuToggle", UIParent);
toggle:SetWidth(32);
toggle:SetHeight(32);
toggle:SetPoint("TOPRIGHT", Minimap, "BOTTOMLEFT", 8, 8);
toggle:SetFrameStrata("MEDIUM");
toggle:SetMovable(true);
toggle:SetClampedToScreen(true);
toggle:RegisterForDrag("LeftButton");
toggle:RegisterForClicks("LeftButtonUp");
toggle:SetNormalTexture("Interface\\Icons\\Ability_Hunter_Pet_Ravager");
toggle:SetHighlightTexture("Interface\\Minimap\\UI-Minimap-ZoomButton-Highlight", "ADD");
toggle:SetScript("OnDragStart", function(self) self:StartMoving(); end);
toggle:SetScript("OnDragStop", function(self) self:StopMovingOrSizing(); self:SetUserPlaced(true); end);
toggle:Hide();

local function ToggleMenu()
	if ( InCombatLockdown() ) then
		UIErrorsFrame:AddMessage("The shape menu opens and closes only out of combat.", 1, 0.3, 0.3);
		return;
	end
	if ( menu:IsShown() ) then
		menu:Hide();
	else
		Refresh();
		menu:Show();
	end
end

toggle:SetScript("OnClick", ToggleMenu);
toggle:SetScript("OnEnter", function(self)
	GameTooltip:SetOwner(self, "ANCHOR_LEFT");
	GameTooltip:AddLine("Devourer");
	GameTooltip:AddLine("Your shapes. Drag to move.", 1, 1, 1);
	GameTooltip:Show();
end);
toggle:SetScript("OnLeave", GameTooltip_Hide);

-- --- the data ---------------------------------------------------------------------------------------------
local function Split(text, sep)
	local out = {};
	for part in string.gmatch(text, "([^" .. sep .. "]+)") do
		table.insert(out, part);
	end
	return out;
end

local events = CreateFrame("Frame");
events:RegisterEvent("PLAYER_ENTERING_WORLD");
events:RegisterEvent("CHAT_MSG_ADDON");
events:RegisterEvent("PLAYER_REGEN_ENABLED");
events:RegisterEvent("LEARNED_SPELL_IN_TAB");
events:SetScript("OnEvent", function(self, event, prefix, message, channel, sender)
	if ( event == "PLAYER_ENTERING_WORLD" ) then
		if ( IsDevourer("player") ) then
			toggle:Show();
			Server("menu");
		else
			toggle:Hide();
			menu:Hide();
		end
	elseif ( event == "CHAT_MSG_ADDON" ) then
		if ( prefix ~= PREFIX or sender ~= UnitName("player") ) then
			return;
		end
		local kind = string.sub(message, 1, 1);
		if ( kind == "B" ) then
			pending = {};
		elseif ( kind == "S" and pending ) then
			-- S:<shape>:<form spell>:<worn>:<colouring worn>:<colouring>,<colouring>,...
			local f = Split(message, ":");
			table.insert(pending, { id = tonumber(f[2]), spell = tonumber(f[3]), worn = f[4] == "1",
				wearing = f[5] or "", skins = Split(f[6] or "", ",") });
		elseif ( kind == "E" and pending ) then
			shapes, pending = pending, nil;
			animaCost = tonumber(string.sub(message, 3)) or 0;
			while ( #shapes > MAX_SHAPES ) do
				table.remove(shapes);
			end
			Refresh();
		end
	elseif ( event == "PLAYER_REGEN_ENABLED" ) then
		if ( dirty ) then
			Refresh();
		end
	elseif ( event == "LEARNED_SPELL_IN_TAB" ) then
		Refresh();
	end
end);

SLASH_DEVOURERMENU1 = "/devour";
SlashCmdList["DEVOURERMENU"] = function(msg)
	msg = msg and strtrim(msg) or "";
	if ( msg == "" ) then
		ToggleMenu();
	else
		Server(msg);
	end
end;
