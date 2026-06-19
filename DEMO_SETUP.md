# Hướng dẫn chạy demo (Đề 6 – Quản lý Tài sản + Phòng họp)

> Dành cho người **clone repo về máy trống** và muốn có Odoo đầy đủ dữ liệu để demo.
> Dữ liệu nằm trong database (không có trong git) → phải cài module + seed một lần.

## 0. Yêu cầu
- Cài **Docker Desktop** và đang chạy.
- Có **Git Bash** (Windows) hoặc terminal Linux/Mac.

## 1. Clone repo
```bash
git clone https://github.com/Q-Huy205/HN-QTDN-17-03-N6.git
cd HN-QTDN-17-03-N6
```

## 2. Chạy 1 lệnh duy nhất (khuyến nghị)

**Trên Windows dùng PowerShell** (đơn giản nhất):
```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup_demo.ps1
```

**Hoặc dùng Git Bash / Linux / Mac:**
```bash
bash scripts/setup_demo.sh
```

> ⚠️ **Đừng gõ `bash ...` trong cửa sổ PowerShell!** Khi đó `bash` sẽ gọi WSL và báo
> *"The command 'docker' could not be found in this WSL 2 distro"*. Hãy dùng file `.ps1`
> ở trên, **hoặc** mở app **"Git Bash"** riêng rồi mới chạy file `.sh`.

Lần đầu sẽ tải image `odoo:15` + `postgres:13` (~1.5GB, hơi lâu). Script tự động:
cài 3 module → khởi động web → seed dữ liệu demo (kèm set múi giờ VN).

Khi thấy `XONG!` → mở **http://localhost:8069**
- Database: `ttdn_test` · Đăng nhập: **admin / admin**

## 3. (Tùy chọn) Bật AI Groq + thông báo Telegram
Không bật vẫn chạy bình thường (AI tự dùng regex, Telegram bỏ qua). Muốn bật, thay `<...>` bằng key của bạn:
```bash
docker compose -f docker-compose.run.yml exec -T odoo bash -c "echo \"
env['ir.config_parameter'].sudo().set_param('phong_hop.groq_api_key','<GROQ_KEY>');
env['ir.config_parameter'].sudo().set_param('phong_hop.telegram_bot_token','<BOT_TOKEN>');
env['ir.config_parameter'].sudo().set_param('phong_hop.telegram_chat_id','<CHAT_ID>');
env.cr.commit()\" | odoo shell -d ttdn_test --db_host=db --db_user=odoo --db_password=odoo --no-http"
```
- Groq key: lấy free tại https://console.groq.com
- Telegram: tạo bot qua @BotFather, lấy `chat_id` qua `https://api.telegram.org/bot<TOKEN>/getUpdates`

## 4. Lệnh quản lý thường dùng
```bash
CF="docker compose -f docker-compose.run.yml"
$CF up -d        # bật lại (sau khi tắt máy)
$CF down         # tắt container (giữ dữ liệu)
$CF logs -f odoo # xem log
$CF down -v      # XOÁ SẠCH cả dữ liệu (muốn cài lại từ đầu thì chạy lại bước 2)
```

## 5. Nếu muốn cài thủ công (không dùng script)
```bash
CF="docker compose -f docker-compose.run.yml"; DBARGS="--db_host=db --db_user=odoo --db_password=odoo"
$CF up -d db
$CF run --rm odoo odoo -i nhan_su,tai_san,phong_hop -d ttdn_test $DBARGS --stop-after-init --without-demo=all
$CF up -d odoo
$CF exec -T odoo bash -c "odoo shell -d ttdn_test $DBARGS --no-http < /mnt/scripts/seed_demo.py"
```

## Dữ liệu demo có sẵn
- **HRM:** 8 nhân viên (ảnh + quản lý trực tiếp), hợp đồng, phụ cấp, lịch sử công tác, chứng chỉ, chấm công, nghỉ phép, tăng ca, phiếu lương.
- **Tài sản:** laptop/màn hình/phòng họp, khấu hao, phiếu mượn, bảo trì, điều chuyển, thanh lý.
- **Phòng họp:** 3 phòng, 6 thiết bị, đơn đặt phòng đủ trạng thái, Trợ lý AI đặt phòng.
