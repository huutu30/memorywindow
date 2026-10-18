@echo off
chcp 65001 > nul
title TOOL TỰ ĐỘNG TẠO CHIẾN DỊCH MEGA PUSH
cd /d "%~dp0"

echo ============================================================
echo       🚀 KHỞI ĐỘNG TOOL TỰ ĐỘNG TẠO CHIẾN DỊCH
echo ============================================================
echo.

python auto_campaign.py

pause
