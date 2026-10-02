@echo off
rem The model tool: opens in your browser. Keep this window open while you use it; close it to stop.
rem Lives in the mod-devourer repo (git pull brings cloud changes).
cd /d "%~dp0source\azerothcore-wotlk\modules\mod-devourer\tools\modeltool"
start "" http://localhost:8765
python server.py
