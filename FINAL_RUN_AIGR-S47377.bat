@echo off
REM ========================================================================
REM PS-03 FINAL SUBMISSION WORKFLOW - Team AIGR-S47377
REM ========================================================================
REM This script will:
REM 1. Extract query chips from all 8 classes
REM 2. Build FAISS index from testing set
REM 3. Run visual search for all classes
REM 4. Combine results into ONE submission file
REM 5. Generate submission in PS-03 format
REM ========================================================================

echo ========================================================================
echo PS-03 Visual Search - Team AIGR-S47377
echo ========================================================================
echo.
echo This will generate your complete submission file for all 8 classes.
echo Estimated time: 25-35 minutes
echo.

cd /d "%~dp0"

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo.
    echo Please run first:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo ========================================================================
echo [STEP 1/6] Activating virtual environment...
echo ========================================================================
call venv\Scripts\activate.bat
echo [OK] Environment activated
echo.

REM Extract chips from all classes
echo ========================================================================
echo [STEP 2/6] Extracting query chips from all 8 classes...
echo ========================================================================
echo.

python scripts\batch_extract_chips.py ^
    --sample-dir data\sample_set ^
    --out-dir chips ^
    --max-chips 5 ^
    --padding 20

if errorlevel 1 (
    echo [ERROR] Chip extraction failed!
    pause
    exit /b 1
)

echo.
echo [OK] All query chips extracted
echo.

REM Build FAISS index
echo ========================================================================
echo [STEP 3/6] Building FAISS index from 40 testing images...
echo ========================================================================
echo This may take 5-10 minutes on CPU, 2 minutes on GPU...
echo.

REM Check for CUDA
python -c "import torch; exit(0 if torch.cuda.is_available() else 1)" 2>nul
if errorlevel 1 (
    echo [INFO] Using CPU (no GPU detected)
    set DEVICE=cpu
) else (
    echo [INFO] Using GPU (CUDA detected) - This will be faster!
    set DEVICE=cuda
)
echo.

REM Check for trained checkpoint
set CHECKPOINT=
if exist "models\checkpoints\best.pth" (
    echo [INFO] Found trained checkpoint: models\checkpoints\best.pth
    echo [INFO] Using trained embedder for better accuracy!
    set CHECKPOINT=--checkpoint models\checkpoints\best.pth
    echo.
) else (
    echo [INFO] No trained checkpoint found, using baseline embedder
    echo [INFO] To improve accuracy, train first:
    echo [INFO]   python scripts\train_embedder.py --data data\training_set --epochs 50
    echo.
)

python scripts\build_index.py ^
    --targets data\testing_set ^
    --out cache\indexes ^
    --config configs\default.yaml ^
    --device %DEVICE% ^
    %CHECKPOINT%

if errorlevel 1 (
    echo [ERROR] Index building failed!
    pause
    exit /b 1
)

echo.
echo [OK] FAISS index built successfully
echo.

REM Create outputs directory
if not exist "outputs" mkdir "outputs"

REM Run search for all 8 classes
echo ========================================================================
echo [STEP 4/6] Running visual search for all 8 classes...
echo ========================================================================
echo.

REM Class 1: Solar Panel
echo [4.1/8] Searching for: Solar Panel...
python scripts\run_search.py ^
    --chips "chips\Solar Panel\chip_01.tif" "chips\Solar Panel\chip_02.tif" "chips\Solar Panel\chip_03.tif" "chips\Solar Panel\chip_04.tif" "chips\Solar Panel\chip_05.tif" ^
    --index cache\indexes ^
    --name "Solar Panel" ^
    --out "outputs\temp_solar_panel.txt" ^
    --team "AIGR-S47377" ^
    --config configs\default.yaml ^
    --device %DEVICE% ^
    %CHECKPOINT%
echo       [OK] Solar Panel complete
echo.

REM Class 2: Brick Kiln
echo [4.2/8] Searching for: Brick Kiln...
python scripts\run_search.py ^
    --chips "chips\Brick Kiln\chip_01.tif" "chips\Brick Kiln\chip_02.tif" "chips\Brick Kiln\chip_03.tif" ^
    --index cache\indexes ^
    --name "Brick Kiln" ^
    --out "outputs\temp_brick_kiln.txt" ^
    --team "AIGR-S47377" ^
    --config configs\default.yaml ^
    --device %DEVICE% ^
    %CHECKPOINT%
echo       [OK] Brick Kiln complete
echo.

REM Class 3: Pond-1 & Pond-2
echo [4.3/8] Searching for: Pond-1 ^& Pond-2...
python scripts\run_search.py ^
    --chips "chips\Pond-1 & Pond-2\chip_01.tif" ^
    --index cache\indexes ^
    --name "Pond-1 & Pond-2" ^
    --out "outputs\temp_pond_1_2.txt" ^
    --team "AIGR-S47377" ^
    --config configs\default.yaml ^
    --device %DEVICE% ^
    %CHECKPOINT%
echo       [OK] Pond-1 ^& Pond-2 complete
echo.

REM Class 4: Pond-1,Pond-2 & Playground
echo [4.4/8] Searching for: Pond-1,Pond-2 ^& Playground...
python scripts\run_search.py ^
    --chips "chips\Pond-1,Pond-2 & Playground\chip_01.tif" ^
    --index cache\indexes ^
    --name "Pond-1,Pond-2 & Playground" ^
    --out "outputs\temp_pond_playground.txt" ^
    --team "AIGR-S47377" ^
    --config configs\default.yaml ^
    --device %DEVICE% ^
    %CHECKPOINT%
echo       [OK] Pond-1,Pond-2 ^& Playground complete
echo.

REM Class 5: Pond-2,STP & Sheds
echo [4.5/8] Searching for: Pond-2,STP ^& Sheds...
python scripts\run_search.py ^
    --chips "chips\Pond-2,STP & Sheds\chip_01.tif" ^
    --index cache\indexes ^
    --name "Pond-2,STP & Sheds" ^
    --out "outputs\temp_pond_stp_sheds.txt" ^
    --team "AIGR-S47377" ^
    --config configs\default.yaml ^
    --device %DEVICE% ^
    %CHECKPOINT%
echo       [OK] Pond-2,STP ^& Sheds complete
echo.

REM Class 6: MetroShed,STP & Sheds
echo [4.6/8] Searching for: MetroShed,STP ^& Sheds...
python scripts\run_search.py ^
    --chips "chips\MetroShed,STP & Sheds\chip_01.tif" ^
    --index cache\indexes ^
    --name "MetroShed,STP & Sheds" ^
    --out "outputs\temp_metro_stp_sheds.txt" ^
    --team "AIGR-S47377" ^
    --config configs\default.yaml ^
    --device %DEVICE% ^
    %CHECKPOINT%
echo       [OK] MetroShed,STP ^& Sheds complete
echo.

REM Class 7: Playground
echo [4.7/8] Searching for: Playground...
python scripts\run_search.py ^
    --chips "chips\Playground\chip_01.tif" ^
    --index cache\indexes ^
    --name "Playground" ^
    --out "outputs\temp_playground.txt" ^
    --team "AIGR-S47377" ^
    --config configs\default.yaml ^
    --device %DEVICE% ^
    %CHECKPOINT%
echo       [OK] Playground complete
echo.

REM Class 8: Sheds
echo [4.8/8] Searching for: Sheds...
python scripts\run_search.py ^
    --chips "chips\Sheds\chip_01.tif" "chips\Sheds\chip_02.tif" "chips\Sheds\chip_03.tif" ^
    --index cache\indexes ^
    --name "Sheds" ^
    --out "outputs\temp_sheds.txt" ^
    --team "AIGR-S47377" ^
    --config configs\default.yaml ^
    --device %DEVICE% ^
    %CHECKPOINT%
echo       [OK] Sheds complete
echo.

echo [OK] All 8 classes searched successfully
echo.

REM Combine all results into ONE submission file
echo ========================================================================
echo [STEP 5/6] Combining all class results into ONE submission file...
echo ========================================================================
echo.

REM Generate submission filename with date (DD-MMM-YYYY format)
for /f "tokens=1-3 delims=/ " %%a in ('echo %date%') do (
    set DD=%%a
    set MM=%%b
    set YYYY=%%c
)

REM Convert month number to abbreviation
if "%MM%"=="01" set MMM=Jan
if "%MM%"=="02" set MMM=Feb
if "%MM%"=="03" set MMM=Mar
if "%MM%"=="04" set MMM=Apr
if "%MM%"=="05" set MMM=May
if "%MM%"=="06" set MMM=Jun
if "%MM%"=="07" set MMM=Jul
if "%MM%"=="08" set MMM=Aug
if "%MM%"=="09" set MMM=Sep
if "%MM%"=="10" set MMM=Oct
if "%MM%"=="11" set MMM=Nov
if "%MM%"=="12" set MMM=Dec

set SUBMISSION_FILE=outputs\GC_PS03_%DD%-%MMM%-%YYYY%_AIGR-S47377.txt

echo Creating: %SUBMISSION_FILE%
echo.

REM Combine all temp files
copy /B ^
    "outputs\temp_solar_panel.txt" + ^
    "outputs\temp_brick_kiln.txt" + ^
    "outputs\temp_pond_1_2.txt" + ^
    "outputs\temp_pond_playground.txt" + ^
    "outputs\temp_pond_stp_sheds.txt" + ^
    "outputs\temp_metro_stp_sheds.txt" + ^
    "outputs\temp_playground.txt" + ^
    "outputs\temp_sheds.txt" ^
    "%SUBMISSION_FILE%" >nul

if errorlevel 1 (
    echo [ERROR] Failed to combine results!
    pause
    exit /b 1
)

REM Clean up temp files
del /Q outputs\temp_*.txt 2>nul

echo [OK] All results combined into ONE file
echo.

REM Show summary
echo ========================================================================
echo [STEP 6/6] SUBMISSION SUMMARY
echo ========================================================================
echo.

echo Final Submission File:
echo   %SUBMISSION_FILE%
echo.

REM Count total detections
for /f %%A in ('type "%SUBMISSION_FILE%" ^| find /C /V ""') do set TOTAL_DETECTIONS=%%A
echo Total Detections: %TOTAL_DETECTIONS%
echo.

echo Detections by Class:
echo.
for /f %%A in ('findstr /C:"Solar Panel" "%SUBMISSION_FILE%" ^| find /C /V ""') do echo   Solar Panel:                    %%A
for /f %%A in ('findstr /C:"Brick Kiln" "%SUBMISSION_FILE%" ^| find /C /V ""') do echo   Brick Kiln:                     %%A
for /f %%A in ('findstr /C:"Pond-1 & Pond-2" "%SUBMISSION_FILE%" ^| find /C /V ""') do echo   Pond-1 ^& Pond-2:                %%A
for /f %%A in ('findstr /C:"Pond-1,Pond-2 & Playground" "%SUBMISSION_FILE%" ^| find /C /V ""') do echo   Pond-1,Pond-2 ^& Playground:    %%A
for /f %%A in ('findstr /C:"Pond-2,STP & Sheds" "%SUBMISSION_FILE%" ^| find /C /V ""') do echo   Pond-2,STP ^& Sheds:             %%A
for /f %%A in ('findstr /C:"MetroShed,STP & Sheds" "%SUBMISSION_FILE%" ^| find /C /V ""') do echo   MetroShed,STP ^& Sheds:          %%A
for /f %%A in ('findstr /C:"Playground" "%SUBMISSION_FILE%" ^| find /C /V ""') do echo   Playground:                     %%A  
for /f %%A in ('findstr /C:"Sheds" "%SUBMISSION_FILE%" ^| find /C /V ""') do echo   Sheds:                          %%A
echo.

echo File Format: PS-03 Standard (space-delimited)
echo   x_min y_min x_max y_max class_name target_filename score
echo.

echo ========================================================================
echo SUCCESS! Your submission file is ready for Team AIGR-S47377
echo ========================================================================
echo.
echo File Location:
echo   %SUBMISSION_FILE%
echo.
echo Next Steps:
echo   1. Review the file: notepad "%SUBMISSION_FILE%"
echo   2. Verify format matches PS-03 requirements
echo   3. Submit to hackathon portal
echo.
echo ========================================================================

pause
notepad "%SUBMISSION_FILE%"
