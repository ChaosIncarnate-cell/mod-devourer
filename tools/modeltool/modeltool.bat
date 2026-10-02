@echo off
rem The model tool: opens in your browser. Keep this window open while you use it; close it to stop.
cd /d "%~dp0tools\modeltool"
start "" http://localhost:8765
python server.py
