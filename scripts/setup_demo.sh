#!/usr/bin/env bash
# ============================================================
# SETUP DEMO 1-LỆNH cho dự án Quản lý Tài sản + Phòng họp (Đề 6)
# Chạy trong Git Bash (Windows) hoặc terminal Linux/Mac, tại thư mục gốc repo:
#     bash scripts/setup_demo.sh
# Yêu cầu: đã cài Docker Desktop và đang chạy.
# Kết quả: Odoo đầy đủ dữ liệu demo ở http://localhost:8069 (DB ttdn_test, admin/admin)
# ============================================================
set -e
CF="docker compose -f docker-compose.run.yml"
DB="ttdn_test"
DBARGS="--db_host=db --db_user=odoo --db_password=odoo"

echo ">>> [1/5] Khởi động PostgreSQL..."
$CF up -d db
sleep 3

echo ">>> [2/5] Cài 3 module (nhan_su, tai_san, phong_hop) vào DB '$DB'..."
$CF run --rm odoo odoo -i nhan_su,tai_san,phong_hop -d "$DB" $DBARGS --stop-after-init --without-demo=all

echo ">>> [3/5] Khởi động Odoo web..."
$CF up -d odoo
echo "    (chờ Odoo sẵn sàng)"; sleep 10

echo ">>> [4/5] Đặt múi giờ Việt Nam cho admin..."
$CF exec -T odoo bash -c "echo \"env['res.users'].browse(2).tz='Asia/Ho_Chi_Minh'; env.cr.commit()\" | odoo shell -d $DB $DBARGS --no-http" >/dev/null 2>&1 || true

echo ">>> [5/5] Seed dữ liệu demo đầy đủ..."
$CF exec -T odoo bash -c "odoo shell -d $DB $DBARGS --no-http < /mnt/scripts/seed_demo.py" 2>&1 | grep -E "SEED_DONE" || echo "    (xem log nếu seed không in SEED_DONE)"

echo ""
echo "============================================================"
echo " XONG! Mở:  http://localhost:8069"
echo " Database:  $DB   |   Đăng nhập:  admin / admin"
echo "------------------------------------------------------------"
echo " (Tùy chọn) Bật AI Groq + Telegram - chạy lệnh, thay <KEY>:"
echo " $CF exec -T odoo bash -c \"echo \\\"\\"
echo "   env['ir.config_parameter'].sudo().set_param('phong_hop.groq_api_key','<GROQ_KEY>');"
echo "   env['ir.config_parameter'].sudo().set_param('phong_hop.telegram_bot_token','<BOT_TOKEN>');"
echo "   env['ir.config_parameter'].sudo().set_param('phong_hop.telegram_chat_id','<CHAT_ID>');"
echo "   env.cr.commit()\\\" | odoo shell -d $DB $DBARGS --no-http\""
echo "============================================================"
