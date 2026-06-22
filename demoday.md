# DEMO DAY — Thuyết minh Nghiệp vụ & Cải tiến

**Đề tài:** Đề 6 — Quản lý Tài sản + Phòng họp, tích hợp Quản lý Nhân sự (HRM) · Nền tảng **Odoo 15**
**Kế thừa từ:** nhóm CNTT16-05 N10 — https://github.com/tranchienthinh-0000/TTDN-16-05-N10
**Repo nhóm:** https://github.com/Q-Huy205/HN-QTDN-17-03-N6

> **Cách dùng tài liệu này khi demo:** Phần **I** là bài nói theo 3 mức chấm điểm (đọc trôi cho thầy nghe).
> Phần **II–IV** là tra cứu nhanh khi thầy hỏi "cái này nằm ở đâu trong code".

---

## Bối cảnh doanh nghiệp giả định
Một **công ty dịch vụ/agency** có nhiều phòng ban. Công ty cần quản lý **tài sản** (laptop, màn hình, phòng họp...) và **điều phối phòng họp dùng chung** — tránh cảnh 2 nhóm cùng giành 1 phòng một khung giờ. Tất cả phải gắn với **một danh sách nhân viên duy nhất** (HRM) để biết "ai đang giữ tài sản gì", "ai đặt phòng nào".

---

# I. NGHIỆP VỤ THEO 3 MỨC (phần chấm điểm)

## ✅ MỨC 1 — TÍCH HỢP HỆ THỐNG (dữ liệu nhất quán)

**Nghiệp vụ:** Trong một doanh nghiệp, chỉ được có **MỘT** danh sách nhân viên làm gốc. Các bộ phận khác (tài sản, phòng họp) **không tự tạo lại** danh sách nhân viên mà phải **trỏ về** hồ sơ nhân sự gốc. Nhờ vậy dữ liệu không trùng lặp, không "ông nói gà bà nói vịt".

**Hệ thống của nhóm làm gì:**
- Module **HRM (`nhan_su`)** giữ hồ sơ nhân viên gốc: thông tin cá nhân, **ảnh đại diện**, phòng ban, chức vụ, **quản lý trực tiếp**, hợp đồng, chấm công, chứng chỉ...
- Module **Tài sản**: trường *"Người đang sử dụng"* của mỗi tài sản **trỏ thẳng** về nhân viên trong HRM — không gõ lại tên.
- Module **Phòng họp**: trường *"Người mượn"* của mỗi đơn đặt phòng cũng **trỏ về** nhân viên HRM.
- **Điểm tích hợp đặc biệt của Đề 6:** phòng họp vừa là **một tài sản dùng chung** (đánh dấu *"Là phòng họp"*), vừa có hồ sơ điều phối lịch riêng → 3 module **dùng chung một cơ sở dữ liệu**.

> **Kịch bản kể cho thầy:** "Khi công ty cấp chiếc laptop cho anh Cường, em chỉ cần chọn anh Cường từ danh sách nhân viên có sẵn — hệ thống tự biết anh ấy thuộc Phòng Kỹ thuật. Đến khi anh Cường đặt phòng họp, vẫn là **chính nhân viên đó** trong cùng một danh sách, không hề nhập trùng. Đó là tính nhất quán dữ liệu mà Mức 1 yêu cầu."

*Code: `nguoi_su_dung_id` → `nhan_vien` ([tai_san.py:76](addons/tai_san/models/tai_san.py#L76)); `nguoi_muon_id` → `nhan_vien` ([dat_phong.py:20](addons/phong_hop/models/dat_phong.py#L20)); liên kết phòng↔tài sản ([quan_ly_phong_hop.py:19](addons/phong_hop/models/quan_ly_phong_hop.py#L19)).*

---

## ✅ MỨC 2 — TỰ ĐỘNG HÓA QUY TRÌNH (event-driven)

**Nghiệp vụ:** Hệ thống phải **tự làm tiếp** các bước dựa trên sự kiện, giảm thao tác tay và sai sót. Trọng tâm Đề 6 là **giải quyết tranh chấp tài nguyên dùng chung** và **quy trình duyệt** chặt chẽ.

Hệ thống tự động hóa **5 việc**:

**1) Chống trùng lịch phòng họp (lõi của Đề 6).**
Khi có người đặt/duyệt phòng, hệ thống **tự dò** xem phòng đó đã có đơn *đã duyệt / đang dùng* nào đè lên khung giờ chưa. Nếu trùng → **chặn ngay** kèm thông báo.
> *"Phòng đã có lịch ĐÃ DUYỆT/ĐANG SỬ DỤNG trùng khung giờ."*

**2) Chống trùng thiết bị.** Một chiếc máy chiếu không thể cùng lúc phục vụ 2 cuộc họp — hệ thống dò trùng cả thiết bị theo khung giờ.

**3) Kiểm tra sức chứa.** Không cho đăng ký 15 người vào phòng chỉ chứa 10 — báo lỗi *"Phòng chỉ chứa tối đa X người"*.

**4) Tự hủy đơn trùng + ghi nhật ký khi duyệt.** Khi trưởng phòng **Duyệt** một đơn, hệ thống **tự động hủy** mọi đơn *chờ duyệt* khác bị trùng giờ (cùng phòng, hoặc cùng người mượn), và **ghi audit log** (ai thao tác, lúc nào, trạng thái trước→sau).

**5) Quy trình trạng thái tự cập nhật tài nguyên.**
`Chờ duyệt → Đã duyệt → Đang sử dụng → Đã trả`. Khi **Bắt đầu sử dụng**, thiết bị tự chuyển *Kho → Phòng*; khi **Trả phòng**, thiết bị tự về *Kho* và hệ thống cập nhật **lịch sử mượn/trả**. Bên Tài sản cũng có vòng đời tương tự: phiếu mượn, bảo trì, điều chuyển, **khấu hao** (tự trừ giá trị tài sản), **thanh lý**.

> **Kịch bản kể cho thầy:** "Sáng thứ Hai, anh Cường và chị Hoa cùng xin phòng họp A1 lúc 9–11h. Trưởng phòng duyệt cho anh Cường → hệ thống **tự động hủy** đơn của chị Hoa, ghi rõ lý do 'trùng lịch', và lưu nhật ký. Không ai phải vào hủy thủ công, và luôn truy được trách nhiệm."

*Code: chống trùng phòng ([dat_phong.py:111](addons/phong_hop/models/dat_phong.py#L111)); chống trùng thiết bị ([dat_phong.py:167](addons/phong_hop/models/dat_phong.py#L167)); sức chứa ([dat_phong.py:125](addons/phong_hop/models/dat_phong.py#L125)); tự hủy đơn trùng + audit khi duyệt ([dat_phong.py:295](addons/phong_hop/models/dat_phong.py#L295)); bắt đầu sử dụng + chuyển thiết bị ([dat_phong.py:361](addons/phong_hop/models/dat_phong.py#L361)).*

---

## ✅ MỨC 3 — AI & KẾT NỐI BÊN NGOÀI

**Nghiệp vụ:** Ứng dụng công nghệ mới để hệ thống "thông minh" hơn và **liên thông với nền tảng ngoài**.

**1) Trợ lý AI đặt phòng (AI/LLM — Groq).**
Thay vì điền từng ô (ngày, giờ, số người, thiết bị), nhân viên chỉ cần **gõ một câu tiếng Việt tự nhiên**:
> *"đặt phòng mai 9–11h cho 15 người có máy chiếu và 2 mic"*

Hệ thống gửi câu này tới **mô hình ngôn ngữ lớn Groq**, AI **bóc tách** ra dữ liệu có cấu trúc (ngày = mai, giờ = 09:00–11:00, số người = 15, thiết bị = máy chiếu×1, mic×2), rồi **tự tìm phòng trống phù hợp** và gợi ý thiết bị cần mượn từ kho.
*(Có cơ chế dự phòng: nếu mất mạng/thiếu khóa API, hệ thống tự chuyển sang bóc tách bằng quy tắc, không bao giờ hỏng.)*

**2) Thông báo qua Telegram (External API).**
Ngay khi một đơn được **Duyệt**, hệ thống **tự gọi Telegram Bot API** gửi tin báo cho người phụ trách: phòng nào, ai mượn, mấy người, khung giờ. Đây là kết nối **theo sự kiện** tới nền tảng ngoài.

> **Kịch bản kể cho thầy:** "Nhân viên không cần biết form ở đâu — chỉ gõ một câu như nhắn tin, **AI hiểu và tự điền**. Khi sếp duyệt, **Telegram báo ngay** về điện thoại. Đây là phần Mức 3: tích hợp AI và kết nối dịch vụ ngoài."

*Code: gọi AI Groq ([phong_hop_ai_wizard.py:405](addons/phong_hop/wizards/phong_hop_ai_wizard.py#L405)); gửi Telegram ([dat_phong.py:251](addons/phong_hop/models/dat_phong.py#L251)).*

📌 **Sơ đồ luồng nghiệp vụ end-to-end:** xem [docs/businessflow/](docs/businessflow/) — thể hiện rõ cả 3 mức trên một hình.

---

# II. CẢI TIẾN SO VỚI BẢN KẾ THỪA (mới / sửa)

| # | Hạng mục | Loại | Mức | Vị trí |
|---|----------|------|-----|--------|
| 1 | Kiểm tra sức chứa phòng khi đặt | 🆕 Mới | 2 | [dat_phong.py:125](addons/phong_hop/models/dat_phong.py#L125) |
| 2 | Gắn phòng họp vào Tài sản (`is_phong_hop`) | 🆕 Mới | 1 | [tai_san.py:81](addons/tai_san/models/tai_san.py#L81) |
| 3 | Trợ lý AI dùng **LLM thật (Groq)** | 🆕 Mới | 3 | [phong_hop_ai_wizard.py:405](addons/phong_hop/wizards/phong_hop_ai_wizard.py#L405) |
| 4 | Thông báo **Telegram** khi duyệt | 🆕 Mới | 3 | [dat_phong.py:251](addons/phong_hop/models/dat_phong.py#L251) |
| 5 | Ảnh đại diện nhân viên | 🆕 Mới | 1 | [nhan_vien.py:17](addons/nhan_su/models/nhan_vien.py#L17) |

> **Lưu ý quan trọng khi thầy hỏi "AI cũ làm gì rồi?":** bản kế thừa K16 mới chỉ bóc tách bằng **biểu thức chính quy (regex)**, chưa phải AI thật. Nhóm đã **nâng lên gọi mô hình ngôn ngữ lớn Groq**, đồng thời thêm **kiểm tra sức chứa** (bản cũ có trường `suc_chua` nhưng bỏ trống không dùng) và **gắn phòng họp thành tài sản dùng chung** đúng tinh thần Đề 6.

---

# III. ĐỌC HIỂU & VÁ LỖI MÃ NGUỒN CŨ (Audit Code)

> Đề bài yêu cầu "đọc hiểu mã nguồn cũ, tái cấu trúc". Nhóm đã phát hiện và sửa **5 lỗi** khiến bản gốc **không cài/chạy được hoặc hiển thị sai**:

1. **Crash khi cài đặt:** `menu.xml` nạp trước các action nó tham chiếu → lỗi `ParseError`. Đã sắp lại thứ tự nạp ([phong_hop/\_\_manifest\_\_.py:22](addons/phong_hop/__manifest__.py#L22)).
2. **Crash khi tạo hợp đồng:** code dùng `fields.Date.max` (không tồn tại). Đã sửa ([hop_dong.py:84](addons/nhan_su/models/hop_dong.py#L84)).
3. **Trùng mã chứng từ:** thiếu 6 bộ sinh mã (sequence) cho khấu hao/bảo trì/điều chuyển/thanh lý... → mọi bản ghi mang mã "New". Đã bổ sung ([sequence.xml:27](addons/tai_san/data/sequence.xml#L27)).
4. **Lệch múi giờ +7:** nhập 09:00 hiển thị 16:00 (Odoo lưu giờ UTC). Đã quy đổi local↔UTC ở AI wizard và thông báo Telegram.
5. **AI bị Cloudflare chặn (403):** thiếu header `User-Agent` khi gọi Groq. Đã sửa.

---

# IV. HẠ TẦNG & DỮ LIỆU DEMO

- **Chạy demo 1 lệnh** (máy trống): xem [DEMO_SETUP.md](DEMO_SETUP.md) — Docker dựng `odoo:15` + `postgres:13`, cài 3 module, seed dữ liệu.
- **Dữ liệu mẫu đầy đủ** cả 3 module: 8 nhân viên (ảnh + cây quản lý), hợp đồng, chấm công, chứng chỉ, phiếu lương; tài sản + khấu hao/mượn/bảo trì/điều chuyển/thanh lý; phòng họp + thiết bị + đặt phòng ([scripts/seed_demo.py](scripts/seed_demo.py)).
- **Lịch sử 17 commit** rõ ràng theo từng tính năng (không commit dồn cuối kỳ).

---

> **Tóm tắt 1 câu để chốt với thầy:** Nhóm đã biến 3 module rời rạc thành **một hệ thống ERP thống nhất** — HRM là dữ liệu gốc (Mức 1), tự động chống trùng & duyệt theo quy trình (Mức 2), và thông minh hóa bằng AI Groq + thông báo Telegram (Mức 3); đồng thời vá nhiều lỗi của bản gốc để hệ thống chạy được thật.
