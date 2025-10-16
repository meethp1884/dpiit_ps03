@echo off
REM ========================================================================
REM FIX GITHUB PUSH - Remove large data files
REM ========================================================================

echo ========================================================================
echo FIXING GITHUB PUSH - Removing Large Data Files
echo ========================================================================
echo.

cd /d "%~dp0"

echo [1/5] Removing data files from git tracking...
git rm -r --cached data/ 2>nul
git rm -r --cached chips/ 2>nul
git rm -r --cached cache/ 2>nul
git rm -r --cached outputs/ 2>nul

echo.
echo [2/5] Adding updated .gitignore...
git add .gitignore

echo.
echo [3/5] Committing changes...
git commit -m "Remove large data files - code only"

echo.
echo [4/5] Pushing to GitHub...
git push origin main

echo.
echo [5/5] Verifying...
git status

echo.
echo ========================================================================
echo DONE! Code pushed to GitHub (without data files)
echo ========================================================================
echo.
echo NEXT: Upload datasets separately to Kaggle
echo   1. Go to https://www.kaggle.com/datasets
echo   2. Create 3 datasets:
echo      - ps03-sample-set (from data/sample_set/)
echo      - ps03-training-set (from data/training_set/)  
echo      - ps03-testing-set (from data/testing_set/)
echo.

pause
