@echo off
:start
echo Starting Pokemon Bot...
python pokemon.py
echo Bot crashed or stopped, restarting in 5 seconds...
timeout /t 5
goto start
