@echo off
REM Automated script to fix dataset folder structure
echo ================================================
echo PS-03 Dataset Structure Fix
echo ================================================
echo.

cd /d "%~dp0"

echo Step 1: Rename mock_set to testing_set
echo ----------------------------------------
if exist "data\mock_set" (
    if exist "data\testing_set" (
        echo WARNING: testing_set already exists!
        echo Skipping rename...
    ) else (
        echo Renaming mock_set to testing_set...
        move "data\mock_set" "data\testing_set"
        echo OK: Renamed to testing_set
    )
) else (
    echo OK: mock_set not found (already renamed or doesn't exist)
)
echo.

echo Step 2: Flatten sample-set nested structure
echo ----------------------------------------
if exist "data\sample-set\sample-set" (
    echo Found nested sample-set folder
    
    REM Create temp folder
    if not exist "data\sample_set_temp" mkdir "data\sample_set_temp"
    
    REM Move all class folders to temp
    echo Moving class folders...
    xcopy "data\sample-set\sample-set\*" "data\sample_set_temp\" /E /I /Y
    
    REM Remove old nested structure
    echo Removing old structure...
    rmdir "data\sample-set" /S /Q
    
    REM Rename temp to sample_set
    echo Renaming to sample_set...
    move "data\sample_set_temp" "data\sample_set"
    
    echo OK: Flattened sample-set structure
) else if exist "data\sample-set" (
    echo Renaming sample-set to sample_set...
    if exist "data\sample_set" (
        echo WARNING: sample_set already exists!
    ) else (
        move "data\sample-set" "data\sample_set"
        echo OK: Renamed to sample_set
    )
) else (
    echo OK: sample-set already processed or doesn't exist
)
echo.

echo Step 3: Verify structure
echo ----------------------------------------
echo Current data folder contents:
dir data /B
echo.

echo ================================================
echo Structure Fix Complete!
echo ================================================
echo.
echo Next steps:
echo 1. Extract chips: python scripts\batch_extract_chips.py --sample-dir data\sample_set --out-dir chips
echo 2. Build index:   python scripts\build_index.py --targets data\testing_set --out cache\indexes
echo 3. Run search:    python scripts\run_search.py --chips "chips\Solar Panel\chip_01.tif" --index cache\indexes --name "Solar Panel" --out outputs\results.txt
echo.
pause
