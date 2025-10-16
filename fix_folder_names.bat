@echo off
REM ========================================================================
REM FIX FOLDER NAMES - Replace & with "and" for Kaggle
REM ========================================================================

echo ========================================================================
echo FIXING FOLDER NAMES FOR KAGGLE
echo Replacing '&' with 'and' in folder names...
echo ========================================================================
echo.

cd /d "%~dp0"

REM Fix sample_set folders
cd data\sample_set
if exist "MetroShed,STP & Sheds" ren "MetroShed,STP & Sheds" "MetroShed,STP and Sheds"
if exist "Pond-1 & Pond-2" ren "Pond-1 & Pond-2" "Pond-1 and Pond-2"
if exist "Pond-1,Pond-2 & Playground" ren "Pond-1,Pond-2 & Playground" "Pond-1,Pond-2 and Playground"
if exist "Pond-2,STP & Sheds" ren "Pond-2,STP & Sheds" "Pond-2,STP and Sheds"

REM Fix training_set folders
cd ..\training_set
if exist "MetroShed,STP & Sheds" ren "MetroShed,STP & Sheds" "MetroShed,STP and Sheds"
if exist "Pond-1 & Pond-2" ren "Pond-1 & Pond-2" "Pond-1 and Pond-2"
if exist "Pond-1,Pond-2 & Playground" ren "Pond-1,Pond-2 & Playground" "Pond-1,Pond-2 and Playground"
if exist "Pond-2,STP & Sheds" ren "Pond-2,STP & Sheds" "Pond-2,STP and Sheds"

REM Fix testing_set folders
cd ..\testing_set
if exist "MetroShed,STP & Sheds" ren "MetroShed,STP & Sheds" "MetroShed,STP and Sheds"
if exist "Pond-1 & Pond-2" ren "Pond-1 & Pond-2" "Pond-1 and Pond-2"
if exist "Pond-1,Pond-2 & Playground" ren "Pond-1,Pond-2 & Playground" "Pond-1,Pond-2 and Playground"
if exist "Pond-2,STP & Sheds" ren "Pond-2,STP & Sheds" "Pond-2,STP and Sheds"

cd ..\..

echo.
echo ========================================================================
echo DONE! Folders renamed:
echo   MetroShed,STP ^& Sheds        → MetroShed,STP and Sheds
echo   Pond-1 ^& Pond-2              → Pond-1 and Pond-2
echo   Pond-1,Pond-2 ^& Playground   → Pond-1,Pond-2 and Playground
echo   Pond-2,STP ^& Sheds           → Pond-2,STP and Sheds
echo ========================================================================
echo.
echo NEXT: Zip and upload to Kaggle
echo.

pause
