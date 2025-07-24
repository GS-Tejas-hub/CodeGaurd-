@echo off
cd "%~dp0"
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/GS-Tejas-hub/CodeGaurd-.git
git push -u origin master
