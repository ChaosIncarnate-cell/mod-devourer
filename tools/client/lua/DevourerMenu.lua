-- mod-devourer: the Devourer's menu (our own code; tools/client/build_client_patch.py puts it into patch-Z.MPQ
-- as Interface\FrameXML\DevourerMenu.lua and loads it last from FrameXML.toc).
--
-- A draggable button (next to the minimap at first) or /devour opens a window with two tabs:
--   Shapes   every shape there is: the ones the Devourer has eaten can be clicked to take them (with a button
--            for the colouring); the others are greyed out. GMs and admins get "Unlock all".
--   Gallery  every shape: how to get it (which creature, where it lives, what it grows out of), its favourite
--            food, all its abilities (the game's own tooltips), its Bio Points and what the next growth needs, every
--            colouring it has (worn ones usable, the others greyed with how to get them) and, once the shape is
--            unlocked, a 3D preview of it and of each colouring (locked shapes show a question mark).
-- The server sends everything as addon messages (prefix DVR, see Mgr::SendMenu in src/DevourerMgr.cpp); the menu
-- asks for it with ".devour menu" at login. Anima is the rage bar: for a Devourer it is drawn purple.
--
-- /devour           opens or closes the menu
-- /devour <words>   the same as the chat command ".devour <words>"

local PREFIX = "DVR";
local MAX_SHAPES = 16;
local ROW_HEIGHT = 26;
local ANIMA_COLOR = { r = 0.58, g = 0.29, b = 0.95 };

local catalog, pendingCatalog = {}, nil;   -- every shape: { id, spell, food, kit = {}, passive, hints = {}, display,
                                           --   colours = { {display, name} }, evos = { {to, bp, level, any, tasks} } }
local owned, pendingOwned = {}, nil;       -- shape id -> { worn, wearing, skins = {}, bp, progress = { ["to:task"] = n } }
local previewColour = nil;                 -- the gallery's colouring (display id), nil = the base one
local isGM = false;
local animaCost = 0;
local dirty = false;
local selected = nil;                      -- the gallery's shape

local function IsDevourer(unit)
	local _, token = UnitClass(unit);
	return token == "DEVOURER";
end

local function Server(words)
	SendChatMessage(".devour" .. (words ~= "" and (" " .. words) or ""), "SAY");
end

local function ShapeName(spell)
	local name = GetSpellInfo(spell or 0);
	return name and (string.gsub(name, " Form$", "")) or "?";
end

-- Anima: the rage bar in purple, on every frame that shows a Devourer.
hooksecurefunc("UnitFrameManaBar_UpdateType", function(manaBar)
	if ( manaBar and manaBar.unit and UnitExists(manaBar.unit) and IsDevourer(manaBar.unit)
			and UnitPowerType(manaBar.unit) == 1 ) then
		manaBar:SetStatusBarColor(ANIMA_COLOR.r, ANIMA_COLOR.g, ANIMA_COLOR.b);
	end
end);

local function SpellTooltip(self)
	if ( self.spellId ) then
		GameTooltip:SetOwner(self, "ANCHOR_RIGHT");
		GameTooltip:SetHyperlink("spell:" .. self.spellId);
		if ( self.extra ) then
			GameTooltip:AddLine(self.extra, 0.7, 0.7, 0.7, true);
		end
		GameTooltip:Show();
	end
end

-- --- the window -------------------------------------------------------------------------------------------
local menu = CreateFrame("Frame", "DevourerMenuFrame", UIParent);
menu:SetWidth(340);
menu:SetHeight(200);
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

local shapesPanel = CreateFrame("Frame", "DevourerMenuShapes", menu);
shapesPanel:SetPoint("TOPLEFT", 0, -60);
shapesPanel:SetPoint("BOTTOMRIGHT", 0, 0);

local galleryPanel = CreateFrame("Frame", "DevourerMenuGallery", menu);
galleryPanel:SetPoint("TOPLEFT", 0, -60);
galleryPanel:SetPoint("BOTTOMRIGHT", 0, 0);
galleryPanel:Hide();

-- Tabs (they switch only out of combat: the Shapes tab holds the buttons that take a shape).
local tabs = {};
local function ShowTab(which)
	if ( InCombatLockdown() ) then
		return;
	end
	if ( which == "gallery" ) then
		menu:SetWidth(580);
		menu:SetHeight(460);
		shapesPanel:Hide();
		galleryPanel:Show();
	else
		menu:SetWidth(340);
		galleryPanel:Hide();
		shapesPanel:Show();
		menu:SetHeight(menu.shapesHeight or 330);
	end
	for name, tab in pairs(tabs) do
		if ( name == which ) then
			tab:Disable();
		else
			tab:Enable();
		end
	end
end
for i, name in ipairs({ "shapes", "gallery" }) do
	local tab = CreateFrame("Button", nil, menu, "UIPanelButtonTemplate");
	tab:SetWidth(90);
	tab:SetHeight(22);
	tab:SetPoint("TOPLEFT", 18 + (i - 1) * 94, -32);
	tab:SetText(name == "shapes" and "Shapes" or "Gallery");
	tab:SetScript("OnClick", function() ShowTab(name); end);
	tabs[name] = tab;
end

-- --- Shapes tab -------------------------------------------------------------------------------------------
local costText = shapesPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall");
costText:SetPoint("TOPLEFT", 20, 0);

local rows = {};
for i = 1, MAX_SHAPES do
	local r = CreateFrame("Button", "DevourerMenuShape" .. i, shapesPanel, "SecureActionButtonTemplate");
	r:SetWidth(200);
	r:SetHeight(ROW_HEIGHT - 2);
	r:SetPoint("TOPLEFT", 16, -16 - (i - 1) * ROW_HEIGHT);
	r:SetAttribute("type", "spell");
	r.icon = r:CreateTexture(nil, "ARTWORK");
	r.icon:SetWidth(ROW_HEIGHT - 4);
	r.icon:SetHeight(ROW_HEIGHT - 4);
	r.icon:SetPoint("LEFT", 2, 0);
	r.name = r:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall");
	r.name:SetPoint("LEFT", r.icon, "RIGHT", 6, 0);
	r.name:SetJustifyH("LEFT");
	r.bp = r:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall");
	r.bp:SetPoint("RIGHT", -4, 0);
	r.worn = r:CreateTexture(nil, "BACKGROUND");
	r.worn:SetAllPoints();
	r.worn:SetTexture(ANIMA_COLOR.r, ANIMA_COLOR.g, ANIMA_COLOR.b, 0.25);
	r:SetHighlightTexture("Interface\\QuestFrame\\UI-QuestTitleHighlight", "ADD");
	r:SetScript("OnEnter", SpellTooltip);
	r:SetScript("OnLeave", GameTooltip_Hide);

	-- Colouring: left click the next one, right click the one before (".devour skin <name>").
	local c = CreateFrame("Button", nil, shapesPanel, "UIPanelButtonTemplate");
	c:SetWidth(90);
	c:SetHeight(20);
	c:SetPoint("LEFT", r, "RIGHT", 4, 0);
	c:RegisterForClicks("LeftButtonUp", "RightButtonUp");
	c:SetScript("OnClick", function(self, button)
		local mine = self.owned;
		if ( not mine or #mine.skins < 2 ) then
			return;
		end
		local at = 1;
		for n, skin in ipairs(mine.skins) do
			if ( skin == mine.wearing ) then
				at = n;
			end
		end
		at = (button == "RightButton") and (at - 2) % #mine.skins + 1 or at % #mine.skins + 1;
		Server("skin " .. mine.skins[at]);
	end);
	c:SetScript("OnEnter", function(self)
		if ( self.owned ) then
			GameTooltip:SetOwner(self, "ANCHOR_RIGHT");
			GameTooltip:AddLine("Colouring: " .. self.owned.wearing);
			GameTooltip:AddLine(table.concat(self.owned.skins, ", "), 1, 1, 1, true);
			if ( #self.owned.skins > 1 ) then
				GameTooltip:AddLine("Left click: next. Right click: back.", 0.7, 0.7, 0.7);
			end
			GameTooltip:Show();
		end
	end);
	c:SetScript("OnLeave", GameTooltip_Hide);
	r.colour = c;
	rows[i] = r;
end

local unlockAll = CreateFrame("Button", nil, shapesPanel, "UIPanelButtonTemplate");
unlockAll:SetWidth(150);
unlockAll:SetHeight(22);
unlockAll:SetText("Unlock all (GM)");
unlockAll:SetScript("OnClick", function() Server("unlockall"); end);
unlockAll:SetScript("OnEnter", function(self)
	GameTooltip:SetOwner(self, "ANCHOR_RIGHT");
	GameTooltip:AddLine("Every shape and every colouring, for your target (a Devourer) or yourself.", 1, 1, 1, true);
	GameTooltip:Show();
end);
unlockAll:SetScript("OnLeave", GameTooltip_Hide);
unlockAll:Hide();

-- --- Gallery tab ------------------------------------------------------------------------------------------
local list = {};
for i = 1, MAX_SHAPES do
	local b = CreateFrame("Button", nil, galleryPanel);
	b:SetWidth(110);
	b:SetHeight(18);
	b:SetPoint("TOPLEFT", 16, -4 - (i - 1) * 19);
	b.text = b:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall");
	b.text:SetPoint("LEFT", 4, 0);
	b.text:SetJustifyH("LEFT");
	b:SetHighlightTexture("Interface\\QuestFrame\\UI-QuestTitleHighlight", "ADD");
	b.mark = b:CreateTexture(nil, "BACKGROUND");
	b.mark:SetAllPoints();
	b.mark:SetTexture(ANIMA_COLOR.r, ANIMA_COLOR.g, ANIMA_COLOR.b, 0.3);
	b.mark:Hide();
	list[i] = b;
end

local detail = CreateFrame("Frame", nil, galleryPanel);
detail:SetPoint("TOPLEFT", 132, -4);
detail:SetPoint("BOTTOMRIGHT", -16, 16);

local dIcon = detail:CreateTexture(nil, "ARTWORK");
dIcon:SetWidth(36);
dIcon:SetHeight(36);
dIcon:SetPoint("TOPLEFT", 0, 0);

local dName = detail:CreateFontString(nil, "OVERLAY", "GameFontNormal");
dName:SetPoint("TOPLEFT", dIcon, "TOPRIGHT", 6, -2);
dName:SetJustifyH("LEFT");

local dState = detail:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall");
dState:SetPoint("TOPLEFT", dName, "BOTTOMLEFT", 0, -3);

local function Section(anchor, text)
	local head = detail:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall");
	head:SetPoint("TOPLEFT", anchor, "BOTTOMLEFT", 0, -10);
	head:SetText(text);
	return head;
end

local howHead = Section(dIcon, "How to get it");
local dHow = detail:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall");
dHow:SetPoint("TOPLEFT", howHead, "BOTTOMLEFT", 0, -3);
dHow:SetWidth(180);
dHow:SetJustifyH("LEFT");

local foodHead = Section(dHow, "Favourite food");
local dFood = detail:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall");
dFood:SetPoint("TOPLEFT", foodHead, "BOTTOMLEFT", 0, -3);

local abilityHead = Section(dFood, "Abilities");
local abilities = {};
for i = 1, 5 do
	local a = CreateFrame("Button", nil, detail);
	a:SetWidth(30);
	a:SetHeight(30);
	a:SetPoint("TOPLEFT", abilityHead, "BOTTOMLEFT", (i - 1) * 34, -4);
	a.icon = a:CreateTexture(nil, "ARTWORK");
	a.icon:SetAllPoints();
	a:SetScript("OnEnter", SpellTooltip);
	a:SetScript("OnLeave", GameTooltip_Hide);
	abilities[i] = a;
end

-- Bio Points and the next growth (every growth a shape has, with the task progress of an owned shape).
local growthHead = Section(abilities[1], "Bio Points and growth");
local dGrowth = detail:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall");
dGrowth:SetPoint("TOPLEFT", growthHead, "BOTTOMLEFT", 0, -3);
dGrowth:SetWidth(200);
dGrowth:SetJustifyH("LEFT");
growthHead:ClearAllPoints();
growthHead:SetPoint("TOPLEFT", abilities[1], "BOTTOMLEFT", 0, -10);

-- The 3D preview (a silhouette while the shape is locked) and the shape's colourings below it.
local COLOUR_ROWS = 6;
local model = CreateFrame("PlayerModel", "DevourerMenuModel", detail);
model:SetWidth(170);
model:SetHeight(170);
model:SetPoint("TOPRIGHT", 0, 0);
local modelBack = model:CreateTexture(nil, "BACKGROUND");
modelBack:SetAllPoints();
modelBack:SetTexture(0, 0, 0, 0.45);
local unknown = detail:CreateFontString(nil, "OVERLAY", "GameFontNormalHuge");
unknown:SetPoint("CENTER", model, "CENTER", 0, 0);
unknown:SetText("?");
unknown:SetTextColor(0.35, 0.35, 0.35);
local unknownIcon = detail:CreateTexture(nil, "ARTWORK");
unknownIcon:SetWidth(96);
unknownIcon:SetHeight(96);
unknownIcon:SetPoint("CENTER", model, "CENTER", 0, 0);
unknownIcon:SetVertexColor(0, 0, 0);

local colourHead = detail:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall");
colourHead:SetPoint("TOPLEFT", model, "BOTTOMLEFT", 0, -6);
colourHead:SetText("Colourings");
local colourRows = {};
local colourScroll = CreateFrame("ScrollFrame", "DevourerMenuColourScroll", detail, "FauxScrollFrameTemplate");
colourScroll:SetPoint("TOPLEFT", colourHead, "BOTTOMLEFT", 0, -2);
colourScroll:SetWidth(150);
colourScroll:SetHeight(COLOUR_ROWS * 16);
local wearButton = CreateFrame("Button", nil, detail, "UIPanelButtonTemplate");
wearButton:SetWidth(100);
wearButton:SetHeight(20);
wearButton:SetPoint("TOPLEFT", colourScroll, "BOTTOMLEFT", 0, -6);
wearButton:SetText("Wear colouring");
wearButton:SetScript("OnClick", function(self)
	if ( self.skin ) then
		Server("skin " .. self.skin);
	end
end);
local colourInfo = detail:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall");
colourInfo:SetPoint("TOPLEFT", wearButton, "BOTTOMLEFT", 0, -4);
colourInfo:SetWidth(170);
colourInfo:SetJustifyH("LEFT");

local ShowDetail;

-- How to get a colouring: the server's hint line "Colouring <name>: Devour ..." for it.
local function ColourHow(shape, name)
	for _, hint in ipairs(shape.hints) do
		local text = string.match(hint, "^Colouring " .. string.gsub(name, "%p", "%%%0") .. ": (.*)$");
		if ( text ) then
			return text;
		end
	end
	return "Devour a creature of this kind that wears it.";
end

local function ColourOwned(id, name)
	local mine = owned[id];
	if ( not mine ) then
		return false;
	end
	for _, skin in ipairs(mine.skins) do
		if ( skin == name ) then
			return true;
		end
	end
	return false;
end

local function UpdateColours()
	local shape = selected and catalog[selected];
	local colours = shape and shape.colours or {};
	FauxScrollFrame_Update(colourScroll, #colours, COLOUR_ROWS, 16);
	local offset = FauxScrollFrame_GetOffset(colourScroll);
	for i, row in ipairs(colourRows) do
		local c = colours[i + offset];
		if ( c ) then
			row.colour = c;
			row.text:SetText(c.name);
			local have = ColourOwned(shape.id, c.name);
			if ( have ) then
				row.text:SetTextColor(1, 1, 1);
			else
				row.text:SetTextColor(0.5, 0.5, 0.5);
			end
			if ( previewColour == c.display or (not previewColour and c.display == shape.display) ) then
				row.mark:Show();
			else
				row.mark:Hide();
			end
			row:Show();
		else
			row.colour = nil;
			row:Hide();
		end
	end
end

for i = 1, COLOUR_ROWS do
	local row = CreateFrame("Button", nil, detail);
	row:SetWidth(140);
	row:SetHeight(16);
	row:SetPoint("TOPLEFT", colourScroll, "TOPLEFT", 0, -(i - 1) * 16);
	row.text = row:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall");
	row.text:SetPoint("LEFT", 2, 0);
	row.text:SetJustifyH("LEFT");
	row.mark = row:CreateTexture(nil, "BACKGROUND");
	row.mark:SetAllPoints();
	row.mark:SetTexture(ANIMA_COLOR.r, ANIMA_COLOR.g, ANIMA_COLOR.b, 0.3);
	row.mark:Hide();
	row:SetHighlightTexture("Interface\\QuestFrame\\UI-QuestTitleHighlight", "ADD");
	row:SetScript("OnClick", function(self)
		if ( self.colour ) then
			previewColour = self.colour.display;
			ShowDetail();
		end
	end);
	colourRows[i] = row;
end
colourScroll:SetScript("OnVerticalScroll", function(self, offset)
	FauxScrollFrame_OnVerticalScroll(self, offset, 16, UpdateColours);
end);

-- The preview: SetDisplayInfo where the client has it, SetCreature as the way back. A failure leaves the question mark.
local function ShowModel(display)
	local ok = false;
	if ( display and display > 0 ) then
		model:ClearModel();
		if ( model.SetDisplayInfo ) then
			ok = pcall(model.SetDisplayInfo, model, display);
		end
		if ( model.SetModelScale ) then
			model:SetModelScale(1);
		end
	end
	if ( ok ) then
		model:Show();
	else
		model:Hide();
	end
	return ok;
end

local function GrowthLines(shape)
	local mine = owned[shape.id];
	local lines = {};
	if ( mine ) then
		table.insert(lines, "Bio Points now: " .. (mine.bp or 0));
	else
		table.insert(lines, "Not eaten yet: it earns Bio Points while worn.");
	end
	if ( #shape.evos == 0 ) then
		table.insert(lines, "It does not grow into another shape.");
	end
	for _, evo in ipairs(shape.evos) do
		local to = catalog[evo.to];
		local name = to and ShapeName(to.spell) or "?";
		if ( owned[evo.to] ) then
			table.insert(lines, "Grew into " .. name .. ".");
		else
			local bp = mine and (mine.bp or 0) or 0;
			local text = "Grows into " .. name .. ": " .. bp .. "/" .. evo.bp .. " BP";
			if ( UnitLevel("player") < evo.level ) then
				text = text .. ", level " .. evo.level;
			elseif ( evo.level > 1 ) then
				text = text .. ", level " .. evo.level .. " ok";
			end
			table.insert(lines, text);
			if ( #evo.tasks > 0 ) then
				table.insert(lines, evo.any and #evo.tasks > 1 and "Any one task:" or "Tasks:");
			end
			for _, task in ipairs(evo.tasks) do
				local done = mine and mine.progress[evo.to .. ":" .. task.id] or 0;
				table.insert(lines, "  " .. task.text .. " " .. math.min(done, task.count) .. "/" .. task.count);
			end
		end
	end
	return table.concat(lines, "\n");
end

function ShowDetail()
	local shape = selected and catalog[selected];
	for _, b in ipairs(list) do
		if ( b.shape and b.shape == selected ) then
			b.mark:Show();
		else
			b.mark:Hide();
		end
	end
	if ( not shape ) then
		detail:Hide();
		return;
	end
	detail:Show();
	local _, _, icon = GetSpellInfo(shape.spell);
	dIcon:SetTexture(icon);
	dIcon:SetDesaturated(not owned[shape.id]);
	dName:SetText(ShapeName(shape.spell));
	if ( owned[shape.id] ) then
		dState:SetText("|cff96e05aYours|r");
	else
		dState:SetText("|cff999999Not eaten yet|r");
	end
	dHow:SetText(#shape.hints > 0 and table.concat(shape.hints, "\n") or "-");
	dFood:SetText(shape.food ~= "" and shape.food or "-");
	local spells = {};
	for _, id in ipairs(shape.kit) do
		table.insert(spells, id);
	end
	if ( shape.passive and shape.passive > 0 ) then
		table.insert(spells, shape.passive);
	end
	for i, a in ipairs(abilities) do
		local id = spells[i];
		if ( id ) then
			local _, _, spellIcon = GetSpellInfo(id);
			a.spellId = id;
			a.extra = (id == shape.passive) and "Passive" or nil;
			a.icon:SetTexture(spellIcon);
			a:Show();
		else
			a:Hide();
		end
	end
	dGrowth:SetText(GrowthLines(shape));

	-- Preview: only for a shape the Devourer has eaten.
	local have = owned[shape.id];
	local display = shape.display;
	local picked = false;
	for _, c in ipairs(shape.colours) do
		if ( c.display == previewColour ) then
			picked = c;
		end
	end
	if ( picked ) then
		display = picked.display;
	else
		previewColour = nil;
	end
	if ( have and ShowModel(display) ) then
		unknown:Hide();
		unknownIcon:Hide();
	else
		model:Hide();
		unknownIcon:SetTexture(icon);
		unknownIcon:Show();
		unknown:SetText(have and "" or "?");
		unknown:Show();
	end
	UpdateColours();
	local c = picked or shape.colours[1];
	wearButton.skin = nil;
	if ( c and have ) then
		if ( ColourOwned(shape.id, c.name) ) then
			colourInfo:SetText(c.name .. (have.wearing == c.name and " (worn)" or ""));
			wearButton.skin = c.name;
			if ( have.wearing == c.name ) then
				wearButton:Disable();
			else
				wearButton:Enable();
			end
		else
			colourInfo:SetText("|cff999999" .. c.name .. ": " .. ColourHow(shape, c.name) .. "|r");
			wearButton:Disable();
		end
	elseif ( c ) then
		colourInfo:SetText("|cff999999" .. c.name .. ": unlock the shape first.|r");
		wearButton:Disable();
	else
		colourInfo:SetText("");
		wearButton:Disable();
	end
end

for _, b in ipairs(list) do
	b:SetScript("OnClick", function(self)
		selected = self.shape;
		previewColour = nil;
		ShowDetail();
	end);
end

-- --- filling it -------------------------------------------------------------------------------------------
local function Ordered()
	local out = {};
	for id in pairs(catalog) do
		table.insert(out, id);
	end
	table.sort(out);
	return out;
end

-- Secure buttons can only change out of combat; a change during a fight waits for its end.
local function Refresh()
	if ( InCombatLockdown() ) then
		dirty = true;
		return;
	end
	dirty = false;

	costText:SetText(animaCost > 0 and ("A shift costs " .. animaCost .. " Anima") or "");
	local ids = Ordered();

	for i, r in ipairs(rows) do
		local id = ids[i];
		local shape = id and catalog[id];
		if ( shape ) then
			local mine = owned[id];
			local name, _, icon = GetSpellInfo(shape.spell);
			r.spellId = shape.spell;
			r.icon:SetTexture(icon);
			r.name:SetText(ShapeName(shape.spell));
			r.bp:SetText(mine and ((mine.bp or 0) .. " BP") or "");
			if ( mine ) then
				r:SetAttribute("spell", name);
				r.extra = (animaCost > 0 and ("Costs " .. animaCost .. " Anima.\n") or "") .. GrowthLines(shape);
				r.icon:SetDesaturated(false);
				r.name:SetTextColor(1, 1, 1);
				if ( mine.worn ) then
					r.worn:Show();
				else
					r.worn:Hide();
				end
				r.colour.owned = mine;
				r.colour:SetText(mine.wearing);
				if ( #mine.skins > 1 ) then
					r.colour:Enable();
				else
					r.colour:Disable();
				end
				r.colour:Show();
			else
				r:SetAttribute("spell", nil);
				r.extra = "Not eaten yet. See the Gallery for how to get it.";
				r.icon:SetDesaturated(true);
				r.name:SetTextColor(0.5, 0.5, 0.5);
				r.worn:Hide();
				r.colour.owned = nil;
				r.colour:Hide();
			end
			r:Show();
		else
			r:Hide();
			r.colour:Hide();
		end
	end

	local count = math.min(#ids, MAX_SHAPES);
	unlockAll:ClearAllPoints();
	unlockAll:SetPoint("TOPLEFT", 16, -22 - count * ROW_HEIGHT);
	if ( isGM ) then
		unlockAll:Show();
	else
		unlockAll:Hide();
	end

	for i, b in ipairs(list) do
		local id = ids[i];
		if ( id ) then
			b.shape = id;
			b.text:SetText(ShapeName(catalog[id].spell));
			if ( owned[id] ) then
				b.text:SetTextColor(1, 1, 1);
			else
				b.text:SetTextColor(0.5, 0.5, 0.5);
			end
			b:Show();
		else
			b.shape = nil;
			b:Hide();
		end
	end
	if ( not selected or not catalog[selected] ) then
		selected = ids[1];
	end
	ShowDetail();

	menu.shapesHeight = math.max(120 + count * ROW_HEIGHT + (isGM and 28 or 0), 330);
	if ( shapesPanel:IsShown() ) then
		menu:SetHeight(menu.shapesHeight);
	end
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
		UIErrorsFrame:AddMessage("The Devourer menu opens and closes only out of combat.", 1, 0.3, 0.3);
		return;
	end
	if ( menu:IsShown() ) then
		menu:Hide();
	else
		Refresh();
		menu:Show();
		Server("menu");   -- fresh Bio Points
	end
end

toggle:SetScript("OnClick", ToggleMenu);
toggle:SetScript("OnEnter", function(self)
	GameTooltip:SetOwner(self, "ANCHOR_LEFT");
	GameTooltip:AddLine("Devourer");
	GameTooltip:AddLine("Shapes and gallery. Drag to move.", 1, 1, 1);
	GameTooltip:Show();
end);
toggle:SetScript("OnLeave", GameTooltip_Hide);

-- --- the data ---------------------------------------------------------------------------------------------
local function Split(text, sep)
	local out = {};
	for part in string.gmatch(text or "", "([^" .. sep .. "]+)") do
		table.insert(out, part);
	end
	return out;
end

local function OnMessage(message)
	local kind = string.sub(message, 1, 1);
	if ( kind == "C" ) then
		pendingCatalog = {};
	elseif ( kind == "A" ) then
		isGM = string.sub(message, 3) == "1";
	elseif ( kind == "G" and pendingCatalog ) then
		-- G:<shape>:<form spell>:<favourite food>:<ability>,<ability>,...:<passive>
		local f = Split(message, ":");
		local id = tonumber(f[2]);
		if ( id ) then
			local kit = {};
			for _, s in ipairs(Split(f[5], ",")) do
				table.insert(kit, tonumber(s));
			end
			pendingCatalog[id] = { id = id, spell = tonumber(f[3]), food = f[4] or "", kit = kit,
				passive = tonumber(f[6]) or 0, hints = {}, display = 0, colours = {}, evos = {} };
		end
	elseif ( kind == "H" and pendingCatalog ) then
		-- H:<shape>:<text> (the text may hold colons)
		local id, text = string.match(message, "^H:(%d+):(.*)$");
		local shape = id and pendingCatalog[tonumber(id)];
		if ( shape ) then
			table.insert(shape.hints, text);
		end
	elseif ( kind == "D" and pendingCatalog ) then
		-- D:<shape>:<base display>
		local id, display = string.match(message, "^D:(%d+):(%d+)$");
		local shape = id and pendingCatalog[tonumber(id)];
		if ( shape ) then
			shape.display = tonumber(display);
		end
	elseif ( kind == "Q" and pendingCatalog ) then
		-- Q:<shape>:<display>|<name>,<display>|<name>,...
		local id, rest = string.match(message, "^Q:(%d+):(.*)$");
		local shape = id and pendingCatalog[tonumber(id)];
		if ( shape ) then
			for _, entry in ipairs(Split(rest, ",")) do
				local display, name = string.match(entry, "^(%d+)|(.*)$");
				if ( display ) then
					table.insert(shape.colours, { display = tonumber(display), name = name });
				end
			end
		end
	elseif ( kind == "V" and pendingCatalog ) then
		-- V:<from>:<to>:<BP>:<level>:<any task>
		local from, to, bp, level, any = string.match(message, "^V:(%d+):(%d+):(%d+):(%d+):(%d)$");
		local shape = from and pendingCatalog[tonumber(from)];
		if ( shape ) then
			table.insert(shape.evos, { to = tonumber(to), bp = tonumber(bp), level = tonumber(level), any = any == "1",
				tasks = {} });
		end
	elseif ( kind == "T" and pendingCatalog ) then
		-- T:<from>:<to>:<task id>:<count>:<text>
		local from, to, task, count, text = string.match(message, "^T:(%d+):(%d+):(%d+):(%d+):(.*)$");
		local shape = from and pendingCatalog[tonumber(from)];
		if ( shape ) then
			for _, evo in ipairs(shape.evos) do
				if ( evo.to == tonumber(to) ) then
					table.insert(evo.tasks, { id = tonumber(task), count = tonumber(count), text = text });
				end
			end
		end
	elseif ( kind == "P" and pendingOwned ) then
		-- P:<shape>:<Bio Points>
		local id, bp = string.match(message, "^P:(%d+):(%d+)$");
		local mine = id and pendingOwned[tonumber(id)];
		if ( mine ) then
			mine.bp = tonumber(bp);
		end
	elseif ( kind == "U" and pendingOwned ) then
		-- U:<from>:<to>:<task id>:<progress>
		local from, to, task, done = string.match(message, "^U:(%d+):(%d+):(%d+):(%d+)$");
		local mine = from and pendingOwned[tonumber(from)];
		if ( mine ) then
			mine.progress[to .. ":" .. task] = tonumber(done);
		end
	elseif ( kind == "B" ) then
		pendingOwned = {};
	elseif ( kind == "S" and pendingOwned ) then
		-- S:<shape>:<form spell>:<worn>:<colouring worn>:<colouring>,<colouring>,...
		local f = Split(message, ":");
		local id = tonumber(f[2]);
		if ( id ) then
			pendingOwned[id] = { worn = f[4] == "1", wearing = f[5] or "", skins = Split(f[6], ","),
				bp = 0, progress = {} };
		end
	elseif ( kind == "K" and pendingOwned ) then
		-- K:<shape>:<colouring>,<colouring>,... (more colourings of an owned shape; a kind can have dozens)
		local id, list = string.match(message, "^K:(%d+):(.*)$");
		local mine = id and pendingOwned[tonumber(id)];
		if ( mine ) then
			for _, skin in ipairs(Split(list, ",")) do
				table.insert(mine.skins, skin);
			end
		end
	elseif ( kind == "E" ) then
		if ( pendingCatalog ) then
			catalog, pendingCatalog = pendingCatalog, nil;
		end
		if ( pendingOwned ) then
			owned, pendingOwned = pendingOwned, nil;
		end
		animaCost = tonumber(string.sub(message, 3)) or 0;
		Refresh();
	end
end

local events = CreateFrame("Frame");
events:RegisterEvent("PLAYER_ENTERING_WORLD");
events:RegisterEvent("CHAT_MSG_ADDON");
events:RegisterEvent("PLAYER_REGEN_ENABLED");
events:SetScript("OnEvent", function(self, event, prefix, message, channel, sender)
	if ( event == "PLAYER_ENTERING_WORLD" ) then
		if ( IsDevourer("player") ) then
			-- Anima is the rage bar: the client builds cost lines and the bar text from these strings, so a
			-- Devourer's own client reads "Anima" (only this player's class decides it).
			RAGE = "Anima";
			RAGE_COST = "%d Anima";
			RAGE_COST_PER_TIME = "%d Anima, plus %d per sec";
			toggle:Show();
			Server("menu");
		else
			toggle:Hide();
			menu:Hide();
		end
	elseif ( event == "CHAT_MSG_ADDON" ) then
		if ( prefix == PREFIX and sender == UnitName("player") ) then
			OnMessage(message);
		end
	elseif ( event == "PLAYER_REGEN_ENABLED" ) then
		if ( dirty ) then
			Refresh();
		end
	end
end);

ShowTab("shapes");

SLASH_DEVOURERMENU1 = "/devour";
SlashCmdList["DEVOURERMENU"] = function(msg)
	msg = msg and strtrim(msg) or "";
	if ( msg == "" ) then
		ToggleMenu();
	else
		Server(msg);
	end
end;
