# PowerShell script để chạy tool trên VS Code
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  TOOL TỰ ĐỘNG TRA CỨU SỐ ĐIỆN THOẠI TỪ MÃ HỢP ĐỒNG" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/2] Đang kiểm tra thư viện Python..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
Write-Host "[OK] Thư viện đã sẵn sàng." -ForegroundColor Green
Write-Host ""

Write-Host "[2/2] Bắt đầu chạy tool..." -ForegroundColor Yellow
Write-Host "Lưu ý: Đảm bảo LDPlayer đang mở đến màn hình Tạo SR!" -ForegroundColor Magenta
Write-Host ""
python auto_lookup_sop.py

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  ĐÃ HOÀN THÀNH!" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
