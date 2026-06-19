# ============================================================
# SETUP DEMO 1-LỆNH (bản PowerShell) - Quản lý Tài sản + Phòng họp (Đề 6)
# Dùng khi máy chỉ có PowerShell (không có Git Bash / WSL chưa bật docker).
# Chạy tại thư mục gốc repo:
#     powershell -ExecutionPolicy Bypass -File scripts\setup_demo.ps1
# Yêu cầu: Docker Desktop đang chạy.
# Kết quả: http://localhost:8069  (DB ttdn_test, admin/admin)
# ============================================================
$ErrorActionPreference = "Stop"
$DB = "ttdn_test"

Write-Host ">>> [1/4] Khoi dong PostgreSQL..." -ForegroundColor Cyan
docker compose -f docker-compose.run.yml up -d db
Start-Sleep -Seconds 3

Write-Host ">>> [2/4] Cai 3 module (nhan_su, tai_san, phong_hop)..." -ForegroundColor Cyan
docker compose -f docker-compose.run.yml run --rm odoo odoo -i nhan_su,tai_san,phong_hop -d $DB --db_host=db --db_user=odoo --db_password=odoo --stop-after-init --without-demo=all

Write-Host ">>> [3/4] Khoi dong Odoo web..." -ForegroundColor Cyan
docker compose -f docker-compose.run.yml up -d odoo
Start-Sleep -Seconds 10

Write-Host ">>> [4/4] Seed du lieu demo (kem set mui gio VN)..." -ForegroundColor Cyan
docker compose -f docker-compose.run.yml exec -T odoo bash -c "odoo shell -d $DB --db_host=db --db_user=odoo --db_password=odoo --no-http < /mnt/scripts/seed_demo.py"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host " XONG! Mo:  http://localhost:8069" -ForegroundColor Green
Write-Host " Database:  $DB   |   Dang nhap:  admin / admin" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
