@echo off
REM ========================================================================
REM PS-03 Complete Workflow - Extract chips, build index, search all classes
REM ========================================================================

echo ========================================================================
echo PS-03 Visual Search - Complete Workflow
echo ========================================================================
echo.

cd /d "%~dp0"

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv venv
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo [1/6] Activating virtual environment...
call venv\Scripts\activate.bat
echo OK
echo.

REM Step 1: Extract chips from all classes
echo ========================================================================
echo [2/6] Extracting query chips from all classes...
echo ========================================================================
echo.

python scripts\batch_extract_chips.py ^
    --sample-dir data\sample_set ^
    --out-dir chips ^
    --max-chips 5 ^
    --padding 20

if errorlevel 1 (
    echo ERROR: Chip extraction failed!
    pause
    exit /b 1
)

echo.
echo OK: All chips extracted
echo.

REM Step 2: Build FAISS index
echo ========================================================================
echo [3/6] Building FAISS index from testing set...
echo ========================================================================
echo This may take 5-10 minutes on CPU, 2 minutes on GPU...
echo.

REM Check for CUDA
python -c "import torch; exit(0 if torch.cuda.is_available() else 1)" 2>nul
if errorlevel 1 (
    echo Using CPU (no GPU detected)
    set DEVICE=cpu
) else (
    echo Using GPU (CUDA detected)
    set DEVICE=cuda
)

python scripts\build_index.py ^
    --targets data\testing_set ^
    --out cache\indexes ^
    --device %DEVICE% ^
    --tile-size 512 ^
    --stride 256

if errorlevel 1 (
    echo ERROR: Index building failed!
    pause
    exit /b 1
)

echo.
echo OK: Index built successfully
echo.

REM Step 3: Run search for all classes
echo ========================================================================
echo [4/6] Running visual search for all classes...
echo ========================================================================
echo.

REM Create outputs directory
if not exist "outputs\runs" mkdir "outputs\runs"

REM Get team name from user or use default
set TEAM_NAME=TeamPS03
echo Enter your team name (or press Enter for default: %TEAM_NAME%):
set /p INPUT_TEAM=
if not "%INPUT_TEAM%"=="" set TEAM_NAME=%INPUT_TEAM%

echo.
echo Using team name: %TEAM_NAME%
echo.

REM Search for Solar Panel
echo [4a/8] Searching for Solar Panel...
python scripts\run_search.py ^
    --chips "chips\Solar Panel\chip_01.tif" "chips\Solar Panel\chip_02.tif" "chips\Solar Panel\chip_03.tif" "chips\Solar Panel\chip_04.tif" "chips\Solar Panel\chip_05.tif" ^
    --index cache\indexes ^
    --name "Solar Panel" ^
    --out "outputs\runs\solar_panel.txt" ^
    --team "%TEAM_NAME%" ^
    --device %DEVICE% ^
    --top-k 1000 ^
    --nms-threshold 0.3

echo.

REM Search for Brick Kiln
echo [4b/8] Searching for Brick Kiln...
python scripts\run_search.py ^
    --chips "chips\Brick Kiln\chip_01.tif" "chips\Brick Kiln\chip_02.tif" ^
    --index cache\indexes ^
    --name "Brick Kiln" ^
    --out "outputs\runs\brick_kiln.txt" ^
    --team "%TEAM_NAME%" ^
    --device %DEVICE% ^
    --top-k 1000 ^
    --nms-threshold 0.3

echo.

REM Search for Pond-1 & Pond-2
echo [4c/8] Searching for Pond-1 ^& Pond-2...
python scripts\run_search.py ^
    --chips "chips\Pond-1 & Pond-2\chip_01.tif" ^
    --index cache\indexes ^
    --name "Pond-1 & Pond-2" ^
    --out "outputs\runs\pond_1_2.txt" ^
    --team "%TEAM_NAME%" ^
    --device %DEVICE% ^
    --top-k 1000 ^
    --nms-threshold 0.3

echo.

REM Search for Pond-1,Pond-2 & Playground
echo [4d/8] Searching for Pond-1,Pond-2 ^& Playground...
python scripts\run_search.py ^
    --chips "chips\Pond-1,Pond-2 & Playground\chip_01.tif" ^
    --index cache\indexes ^
    --name "Pond-1,Pond-2 & Playground" ^
    --out "outputs\runs\pond_playground.txt" ^
    --team "%TEAM_NAME%" ^
    --device %DEVICE% ^
    --top-k 1000 ^
    --nms-threshold 0.3

echo.

REM Search for Pond-2,STP & Sheds
echo [4e/8] Searching for Pond-2,STP ^& Sheds...
python scripts\run_search.py ^
    --chips "chips\Pond-2,STP & Sheds\chip_01.tif" ^
    --index cache\indexes ^
    --name "Pond-2,STP & Sheds" ^
    --out "outputs\runs\pond_stp_sheds.txt" ^
    --team "%TEAM_NAME%" ^
    --device %DEVICE% ^
    --top-k 1000 ^
    --nms-threshold 0.3

echo.

REM Search for MetroShed,STP & Sheds
echo [4f/8] Searching for MetroShed,STP ^& Sheds...
python scripts\run_search.py ^
    --chips "chips\MetroShed,STP & Sheds\chip_01.tif" ^
    --index cache\indexes ^
    --name "MetroShed,STP & Sheds" ^
    --out "outputs\runs\metro_stp_sheds.txt" ^
    --team "%TEAM_NAME%" ^
    --device %DEVICE% ^
    --top-k 1000 ^
    --nms-threshold 0.3

echo.

REM Search for Playground
echo [4g/8] Searching for Playground...
python scripts\run_search.py ^
    --chips "chips\Playground\chip_01.tif" ^
    --index cache\indexes ^
    --name "Playground" ^
    --out "outputs\runs\playground.txt" ^
    --team "%TEAM_NAME%" ^
    --device %DEVICE% ^
    --top-k 1000 ^
    --nms-threshold 0.3

echo.

REM Search for Sheds
echo [4h/8] Searching for Sheds...
python scripts\run_search.py ^
    --chips "chips\Sheds\chip_01.tif" "chips\Sheds\chip_02.tif" ^
    --index cache\indexes ^
    --name "Sheds" ^
    --out "outputs\runs\sheds.txt" ^
    --team "%TEAM_NAME%" ^
    --device %DEVICE% ^
    --top-k 1000 ^
    --nms-threshold 0.3

echo.
echo OK: All searches complete
echo.

REM Step 4: Combine all results
echo ========================================================================
echo [5/6] Combining results from all classes...
echo ========================================================================
echo.

REM Generate submission filename with date
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)

set SUBMISSION_FILE=outputs\GC_PS03_%mydate%_%TEAM_NAME%.txt

copy /B ^
    "outputs\runs\solar_panel.txt" + ^
    "outputs\runs\brick_kiln.txt" + ^
    "outputs\runs\pond_1_2.txt" + ^
    "outputs\runs\pond_playground.txt" + ^
    "outputs\runs\pond_stp_sheds.txt" + ^
    "outputs\runs\metro_stp_sheds.txt" + ^
    "outputs\runs\playground.txt" + ^
    "outputs\runs\sheds.txt" ^
    "%SUBMISSION_FILE%"

echo.
echo OK: Combined submission file created
echo.

REM Step 5: Show summary
echo ========================================================================
echo [6/6] Summary
echo ========================================================================
echo.

REM Count detections per class
echo Detection counts by class:
echo.
findstr /C:"Solar Panel" "%SUBMISSION_FILE%" | find /C "Solar Panel" && echo   Solar Panel: && findstr /C:"Solar Panel" "%SUBMISSION_FILE%" | find /C "Solar Panel"
findstr /C:"Brick Kiln" "%SUBMISSION_FILE%" | find /C "Brick Kiln" && echo   Brick Kiln: && findstr /C:"Brick Kiln" "%SUBMISSION_FILE%" | find /C "Brick Kiln"
findstr /C:"Pond-1 & Pond-2" "%SUBMISSION_FILE%" | find /C "Pond" && echo   Pond classes: && findstr /C:"Pond" "%SUBMISSION_FILE%" | find /C "Pond"
findstr /C:"Playground" "%SUBMISSION_FILE%" | find /C "Playground" && echo   Playground: && findstr /C:"Playground" "%SUBMISSION_FILE%" | find /C "Playground"
findstr /C:"Sheds" "%SUBMISSION_FILE%" | find /C "Sheds" && echo   Sheds classes: && findstr /C:"Sheds" "%SUBMISSION_FILE%" | find /C "Sheds"

echo.
echo Total detections:
find /C "" < "%SUBMISSION_FILE%"

echo.
echo ========================================================================
echo COMPLETE! Your submission file is ready:
echo.
echo   %SUBMISSION_FILE%
echo.
echo ========================================================================
echo.
echo Next steps:
echo 1. Review results: notepad "%SUBMISSION_FILE%"
echo 2. Check individual class results in outputs\runs\
echo 3. Submit the file: %SUBMISSION_FILE%
echo.

pause
notepad "%SUBMISSION_FILE%"
