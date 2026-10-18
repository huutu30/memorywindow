@echo off
chcp 65001 > nul
title TOOL TRA CỨU MÃ HỢP ĐỒNG SOP

echo ========================================================
echo   TOOL TỰ ĐỘNG TRA CỨU SỐ ĐIỆN THOẠI TỪ MÃ HỢP ĐỒNG
echo ========================================================
echo.

echo [1/2] Đang kiểm tra thư viện Python cần thiết...
pip install -r requirements.txt --quiet
echo [OK] Thư viện đã sẵn sàng.
echo.

echo [2/2] Bắt đầu chạy tool...
echo Lưu ý: Hãy đảm bảo LDPlayer đang mở đến màn hình Tạo SR!
echo.
python auto_lookup_sop.py

echo.
echo ========================================================
echo   ĐÃ CHẠY XONG! Bấm phím bất kỳ để đóng cửa sổ này.
echo ========================================================
pause > nul
