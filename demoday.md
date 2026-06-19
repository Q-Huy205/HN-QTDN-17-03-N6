# DEMO DAY — Báo cáo Cải tiến Dự án

**Đề tài:** Đề 6 — Quản lý Tài sản + Phòng họp (tích hợp HRM) · Odoo 15
**Kế thừa từ:** nhóm CNTT16-05 N10 — https://github.com/tranchienthinh-0000/TTDN-16-05-N10
**Repo nhóm:** https://github.com/Q-Huy205/HN-QTDN-17-03-N6

> Tài liệu này liệt kê **cái gì MỚI thêm**, **cái gì SỬA/làm mới** so với bản kế thừa,
> kèm **tham chiếu file + số dòng** và **commit** để thầy đối chiếu nhanh.

---

## A. TÓM TẮT NHANH

| # | Hạng mục | Loại | Mức điểm | Vị trí chính |
|---|----------|------|----------|--------------|
| 1 | Kiểm tra sức chứa phòng khi đặt | 🆕 Mới | Mức 2 | [dat_phong.py:125](addons/phong_hop/models/dat_phong.py#L125) |
| 2 | Gắn phòng họp vào Tài sản (`is_phong_hop`) | 🆕 Mới | Đúng tinh thần Đề 6 | [tai_san.py:81](addons/tai_san/models/tai_san.py#L81) |
| 3 | Trợ lý AI đặt phòng dùng **LLM thật (Groq)** | 🆕 Mới | Mức 3 (AI) | [phong_hop_ai_wizard.py:405](addons/phong_hop/wizards/phong_hop_ai_wizard.py#L405) |
| 4 | Thông báo **Telegram** khi duyệt | 🆕 Mới | Mức 3 (External API) | [dat_phong.py:251](addons/phong_hop/models/dat_phong.py#L251) |
| 5 | Ảnh đại diện nhân viên | 🆕 Mới | HRM | [nhan_vien.py:17](addons/nhan_su/models/nhan_vien.py#L17) |
| 6 | Sửa lỗi thứ tự load menu (crash cài đặt) | 🔧 Sửa | — | [phong_hop/\_\_manifest\_\_.py:22](addons/phong_hop/__manifest__.py#L22) |
| 7 | Sửa bug `fields.Date.max` (crash tạo hợp đồng) | 🔧 Sửa | — | [hop_dong.py:84](addons/nhan_su/models/hop_dong.py#L84) |
| 8 | Bổ sung 6 sequence còn thiếu (trùng mã 'New') | 🔧 Sửa | — | [sequence.xml:27](addons/tai_san/data/sequence.xml#L27) |
| 9 | Sửa lệch múi giờ +7 (wizard + Telegram) | 🔧 Sửa | — | [phong_hop_ai_wizard.py:508](addons/phong_hop/wizards/phong_hop_ai_wizard.py#L508) |
| 10 | Sửa Groq bị Cloudflare chặn (User-Agent) | 🔧 Sửa | — | [phong_hop_ai_wizard.py:442](addons/phong_hop/wizards/phong_hop_ai_wizard.py#L442) |
| 11 | Hạ tầng Docker + seed + tài liệu demo | 🆕 Mới | — | [DEMO_SETUP.md](DEMO_SETUP.md) |

Tổng cộng **16 commit** có lịch sử rõ ràng (xem mục E).

---

## B. TÍNH NĂNG MỚI (chi tiết)

### 1. Kiểm tra sức chứa phòng họp khi đặt 🆕 (Mức 2)
- **Bản gốc:** model phòng có field `suc_chua` nhưng **không dùng để kiểm tra** → có thể đặt 100 người vào phòng 10 chỗ.
- **Cải tiến:** thêm `so_nguoi_du_hop` + ràng buộc chặn vượt sức chứa.
- **Code:**
  - Field: [dat_phong.py:23-30](addons/phong_hop/models/dat_phong.py#L23-L30) (`so_nguoi_du_hop`, `suc_chua_phong` related)
  - Ràng buộc: [dat_phong.py:125-138](addons/phong_hop/models/dat_phong.py#L125-L138) (`_constrains_suc_chua`)
  - Giao diện: [dat_phong.xml:46-47](addons/phong_hop/views/dat_phong.xml#L46-L47), [dat_phong.xml:108](addons/phong_hop/views/dat_phong.xml#L108)
- **Commit:** `329439ec`

### 2. Gắn phòng họp vào Tài sản dùng chung (`is_phong_hop`) 🆕
- **Bản gốc:** phòng họp (`quan_ly_phong_hop`) tách rời, không liên quan tới `tai_san` → sai tinh thần Đề 6 "phòng họp là tài sản dùng chung".
- **Cải tiến:** đánh dấu tài sản là phòng họp + liên kết 2 chiều, tự đồng bộ.
- **Code:**
  - `tai_san`: [tai_san.py:81-82](addons/tai_san/models/tai_san.py#L81-L82) (`is_phong_hop`, `suc_chua`)
  - Link + đồng bộ: [quan_ly_phong_hop.py:19-26](addons/phong_hop/models/quan_ly_phong_hop.py#L19) (`tai_san_id`, domain `is_phong_hop=True`), [quan_ly_phong_hop.py:71-94](addons/phong_hop/models/quan_ly_phong_hop.py#L71) (`_onchange_tai_san_id`, `_sync_tai_san_flag`, `create`/`write`)
  - Tránh **phụ thuộc vòng**: KHÔNG đặt Many2one chiều `tai_san → quan_ly_phong_hop` (giải thích tại [tai_san.py:78-80](addons/tai_san/models/tai_san.py#L78-L80))
- **Commit:** `ca55811f`

### 3. Trợ lý AI đặt phòng dùng LLM thật — Groq 🆕 (Mức 3)
- **Bản gốc:** "AI" chỉ là **regex/rule-based** (bóc tách bằng biểu thức chính quy).
- **Cải tiến:** gọi **mô hình ngôn ngữ lớn Groq** (API tương thích OpenAI) để hiểu câu đặt phòng tiếng Việt tự nhiên; **tự fallback về regex** nếu thiếu key/lỗi mạng → không bao giờ vỡ.
- **Code:**
  - Cấu hình + endpoint: [phong_hop_ai_wizard.py:18-24](addons/phong_hop/wizards/phong_hop_ai_wizard.py#L18)
  - Đọc key: [phong_hop_ai_wizard.py:399](addons/phong_hop/wizards/phong_hop_ai_wizard.py#L399) (`_groq_config`)
  - Gọi LLM: [phong_hop_ai_wizard.py:405](addons/phong_hop/wizards/phong_hop_ai_wizard.py#L405) (`_llm_extract`)
  - Áp kết quả: [phong_hop_ai_wizard.py:454](addons/phong_hop/wizards/phong_hop_ai_wizard.py#L454) (`_apply_llm_result`)
  - Điểm ưu tiên LLM rồi fallback: [phong_hop_ai_wizard.py:524-532](addons/phong_hop/wizards/phong_hop_ai_wizard.py#L524)
- **Cấu hình:** System Parameter `phong_hop.groq_api_key`, `phong_hop.groq_model`
- **Commit:** `24624a69` (+ fix Cloudflare `20738b03`)

### 4. Thông báo Telegram khi đặt phòng được duyệt 🆕 (Mức 3 — External API)
- **Cải tiến:** khi bấm **Duyệt**, hệ thống gọi **Telegram Bot API** gửi thông báo; thiếu cấu hình thì bỏ qua, không chặn nghiệp vụ.
- **Code:**
  - Hàm gửi: [dat_phong.py:251](addons/phong_hop/models/dat_phong.py#L251) (`_send_telegram`)
  - Soạn nội dung: [dat_phong.py:282](addons/phong_hop/models/dat_phong.py#L282) (`_telegram_message_duyet`)
  - Kích hoạt khi duyệt: [dat_phong.py:311](addons/phong_hop/models/dat_phong.py#L311)
- **Cấu hình:** `phong_hop.telegram_bot_token`, `phong_hop.telegram_chat_id`
- **Commit:** `aea46b31` (+ fix giờ `be8f2cbd`)

### 5. Ảnh đại diện nhân viên 🆕
- **Bản gốc:** model `nhan_vien` **không có** trường ảnh.
- **Cải tiến:** thêm `hinh_anh` (kiểu Image) + hiển thị avatar trên form.
- **Code:** [nhan_vien.py:17](addons/nhan_su/models/nhan_vien.py#L17), giao diện [nhan_vien.xml:11](addons/nhan_su/views/nhan_vien.xml#L11)
- **Commit:** `b40b85c6`

---

## C. SỬA LỖI / LÀM MỚI CODE GỐC K16

> Đây là phần "đọc hiểu mã nguồn cũ → vá lỗi" mà đề bài yêu cầu (Audit Code).
> Các lỗi này khiến bản gốc **không cài/chạy được** hoặc **hiển thị sai**.

### 6. Lỗi thứ tự load khiến cài đặt CRASH 🔧
- **Lỗi:** `menu.xml` load trước, tham chiếu action định nghĩa ở file load sau → `ParseError: External ID not found: action_quan_ly_phong_hop`.
- **Sửa:** đưa `menu.xml` load **cuối cùng**, gom toàn bộ menuitem về 1 file.
- **Code:** [phong_hop/\_\_manifest\_\_.py:11-22](addons/phong_hop/__manifest__.py#L11-L22)
- **Commit:** `392ac469`

### 7. Bug `fields.Date.max` 🔧
- **Lỗi:** `hop_dong` dùng `fields.Date.max` (không tồn tại) → `AttributeError` khi tạo hợp đồng không có ngày kết thúc.
- **Sửa:** [hop_dong.py:83-84](addons/nhan_su/models/hop_dong.py#L83-L84) dùng `fields.Date.to_date("9999-12-31")`
- **Commit:** `f25914d9`

### 8. Thiếu 6 sequence → trùng mã "New" 🔧
- **Lỗi:** code gọi `next_by_code(...)` cho khấu hao/bảo trì/điều chuyển/thanh lý/vị trí... nhưng sequence chưa định nghĩa → mọi bản ghi mang mã `New` → vi phạm ràng buộc duy nhất.
- **Sửa:** bổ sung 6 sequence tại [sequence.xml:27-68](addons/tai_san/data/sequence.xml#L27-L68)
- **Commit:** `f25914d9`

### 9. Lệch múi giờ +7 (lưu local thành UTC) 🔧
- **Lỗi:** nhập 09:00 nhưng hiển thị 16:00 (Odoo lưu Datetime theo UTC, code gốc lưu thẳng giờ local).
- **Sửa:** quy đổi local↔UTC ở ranh giới.
  - Helper: [phong_hop_ai_wizard.py:505-521](addons/phong_hop/wizards/phong_hop_ai_wizard.py#L505) (`_tzname`, `_local_to_utc`, `_utc_to_local_str`)
  - Lưu đúng: [phong_hop_ai_wizard.py:499](addons/phong_hop/wizards/phong_hop_ai_wizard.py#L499), [:558](addons/phong_hop/wizards/phong_hop_ai_wizard.py#L558), [:685](addons/phong_hop/wizards/phong_hop_ai_wizard.py#L685)
  - Telegram hiển thị giờ local: [dat_phong.py:273](addons/phong_hop/models/dat_phong.py#L273) (`_fmt_local`), dùng tại [dat_phong.py:289](addons/phong_hop/models/dat_phong.py#L289)
- **Commit:** `da3a8330`, `be8f2cbd`

### 10. Groq bị Cloudflare chặn (403/1010) 🔧
- **Lỗi:** request không có `User-Agent` bị Cloudflare chặn.
- **Sửa:** thêm header User-Agent tại [phong_hop_ai_wizard.py:442](addons/phong_hop/wizards/phong_hop_ai_wizard.py#L442)
- **Commit:** `20738b03`

---

## D. HẠ TẦNG & DỮ LIỆU DEMO 🆕

- **Docker chạy local:** [docker-compose.run.yml](docker-compose.run.yml) — `odoo:15` + `postgres:13`, chỉ mount module custom (tránh xung đột core). Commit `3f39f4a7`.
- **Seed dữ liệu đầy đủ cả 3 module:** [scripts/seed_demo.py](scripts/seed_demo.py) — 8 nhân viên (ảnh + quản lý trực tiếp), hợp đồng+phụ cấp, lịch sử công tác, chứng chỉ, chấm công, nghỉ phép, tăng ca, phiếu lương; tài sản + khấu hao/mượn/bảo trì/điều chuyển/thanh lý; phòng họp + thiết bị + đặt phòng. Idempotent, tự set múi giờ VN. Commit `841fb322`, `dad8ac1b`.
- **Cài 1 lệnh:** [scripts/setup_demo.ps1](scripts/setup_demo.ps1) (PowerShell) / [scripts/setup_demo.sh](scripts/setup_demo.sh) (Git Bash). Commit `d51dc45a`, `dad8ac1b`.
- **Hướng dẫn bàn giao:** [DEMO_SETUP.md](DEMO_SETUP.md).

---

## E. LỊCH SỬ COMMIT (minh bạch tiến độ)

```
336b8104  feat: kế thừa module Tài sản + Phòng họp (Đề 6) từ K16   (mốc gốc)
329439ec  feat: validate số người dự họp không vượt sức chứa
ca55811f  feat: gắn phòng họp vào tài sản dùng chung (is_phong_hop)
24624a69  feat: AI wizard đặt phòng dùng LLM thật (Groq)
aea46b31  feat: thông báo Telegram khi đặt phòng được duyệt
392ac469  fix:  sửa thứ tự load menu (crash cài đặt)
3f39f4a7  chore: docker-compose.run.yml chạy thử local
20738b03  fix:  thêm User-Agent tránh Cloudflare chặn Groq
b40b85c6  feat: ảnh đại diện nhân viên + seed cơ bản
da3a8330  fix:  xử lý timezone trong AI wizard
f25914d9  fix:  vá bug gốc K16 (hop_dong Date.max + thiếu sequence)
841fb322  feat: seed dữ liệu demo đầy đủ 3 module
be8f2cbd  fix:  tin Telegram hiển thị giờ local
d51dc45a  docs: setup_demo.sh + DEMO_SETUP.md
cbee6f6e  chore: .gitattributes ép LF cho .sh
dad8ac1b  feat: setup_demo.ps1 + seed tự set múi giờ VN
```

---

## F. ĐỐI CHIẾU THANG ĐIỂM

- **Mức 1 (Tích hợp hệ thống):** HRM (`nhan_vien`) là dữ liệu gốc, mọi liên kết tài sản/phòng họp trỏ về `nhan_vien`; chung 1 CSDL.
- **Mức 2 (Tự động hóa quy trình):** chống trùng phòng/thiết bị, kiểm tra sức chứa, workflow duyệt + audit log, đồng bộ tài sản↔phòng họp tự động.
- **Mức 3 (AI & External API):** AI Groq bóc tách yêu cầu đặt phòng (input→xử lý→output), Telegram Bot API gửi thông báo theo sự kiện duyệt.
