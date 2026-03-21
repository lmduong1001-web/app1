@echo off
cd /d %~dp0

git add .
git commit -m "app1"
git push origin master

echo DONE!
pause