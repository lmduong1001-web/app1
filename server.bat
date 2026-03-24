@echo off
cd /d %~dp0

echo ===== ADD & COMMIT =====
git add .
git commit -m "app1"

echo ===== PUSH =====
git push origin master

echo ===== DONE =====
pause