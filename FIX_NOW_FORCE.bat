@echo off
REM ========================================================================
REM NUCLEAR OPTION - Remove data files from git history completely
REM ========================================================================

echo ========================================================================
echo REMOVING DATA FILES FROM GIT HISTORY
echo This will take a few minutes...
echo ========================================================================
echo.

cd /d "%~dp0"

echo [STEP 1] Removing data files from ALL commits...
git filter-branch --force --index-filter "git rm -r --cached --ignore-unmatch data/ chips/ cache/ outputs/" --prune-empty --tag-name-filter cat -- --all

echo.
echo [STEP 2] Cleaning up...
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo.
echo [STEP 3] Force pushing to GitHub...
git push origin main --force

echo.
echo ========================================================================
echo DONE! GitHub push should work now.
echo ========================================================================
pause
