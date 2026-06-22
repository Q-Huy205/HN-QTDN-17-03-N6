# BÁO CÁO NGHIỆP VỤ & CẢI TIẾN DỰ ÁN

**Đề tài:** Đề 6 — Quản lý Tài sản + Phòng họp, tích hợp Quản lý Nhân sự (HRM)
**Nền tảng:** Odoo 15
**Kế thừa từ:** nhóm CNTT16-05 N10 — https://github.com/tranchienthinh-0000/TTDN-16-05-N10
**Mã nguồn nhóm:** https://github.com/Q-Huy205/HN-QTDN-17-03-N6

---

## Bối cảnh doanh nghiệp

Hệ thống mô phỏng một công ty dịch vụ có nhiều phòng ban, cần quản lý tài sản (laptop, màn hình, phòng họp...) và điều phối phòng họp dùng chung sao cho không xảy ra tranh chấp khi hai nhóm cùng đăng ký một phòng trong cùng khung giờ. Mọi dữ liệu đều gắn với một danh sách nhân viên duy nhất (HRM) để xác định ai đang giữ tài sản, ai đặt phòng.

Hệ thống gồm ba module tích hợp: **Quản lý nhân sự** (`nhan_su`), **Quản lý tài sản** (`tai_san`) và **Quản lý phòng họp** (`phong_hop`).

---

## I. NGHIỆP VỤ THEO BA MỨC

### Mức 1 — Tích hợp hệ thống (dữ liệu nhất quán)

**Nghiệp vụ.** Trong một doanh nghiệp chỉ tồn tại một danh sách nhân viên gốc. Các bộ phận khác không tạo lại danh sách riêng mà tham chiếu đến hồ sơ nhân sự gốc, nhờ đó dữ liệu không trùng lặp và luôn nhất quán.

**Giải pháp của hệ thống.**
- Module HRM lưu hồ sơ nhân viên gốc: thông tin cá nhân, ảnh đại diện, phòng ban, chức vụ, quản lý trực tiếp, hợp đồng, chấm công, chứng chỉ.
- Module Tài sản: trường "Người đang sử dụng" của mỗi tài sản tham chiếu trực tiếp đến nhân viên trong HRM.
- Module Phòng họp: trường "Người mượn" của mỗi đơn đặt phòng cũng tham chiếu đến nhân viên trong HRM.
- Điểm tích hợp đặc trưng của Đề 6: mỗi phòng họp đồng thời là một tài sản dùng chung (được đánh dấu "Là phòng họp"), nên ba module cùng chia sẻ một cơ sở dữ liệu.

**Ví dụ minh họa.** Khi công ty cấp một chiếc laptop cho nhân viên Lê Hoàng Cường, người dùng chỉ chọn nhân viên này từ danh sách HRM có sẵn; hệ thống tự biết nhân viên thuộc Phòng Kỹ thuật. Khi chính nhân viên đó đặt phòng họp, vẫn là cùng một bản ghi nhân viên trong cùng danh sách, không nhập trùng.

**Vị trí mã nguồn.** `nguoi_su_dung_id` → `nhan_vien` ([tai_san.py:76](addons/tai_san/models/tai_san.py#L76)); `nguoi_muon_id` → `nhan_vien` ([dat_phong.py:20](addons/phong_hop/models/dat_phong.py#L20)); liên kết phòng họp với tài sản ([quan_ly_phong_hop.py:19](addons/phong_hop/models/quan_ly_phong_hop.py#L19)).

---

### Mức 2 — Tự động hóa quy trình (event-driven)

**Nghiệp vụ.** Hệ thống tự thực thi các bước tiếp theo dựa trên sự kiện, giảm thao tác thủ công và sai sót. Trọng tâm của Đề 6 là giải quyết tranh chấp tài nguyên dùng chung và bảo đảm quy trình duyệt chặt chẽ.

**Giải pháp của hệ thống** — năm cơ chế tự động:

1. **Chống trùng lịch phòng họp.** Khi đặt hoặc duyệt phòng, hệ thống tự kiểm tra xem phòng đã có đơn "đã duyệt" hoặc "đang sử dụng" nào đè lên khung giờ chưa; nếu trùng thì chặn ngay kèm thông báo.
2. **Chống trùng thiết bị.** Một thiết bị (ví dụ máy chiếu) không thể đồng thời phục vụ hai cuộc họp trong cùng khung giờ.
3. **Kiểm tra sức chứa.** Không cho phép số người dự họp vượt quá sức chứa của phòng.
4. **Tự hủy đơn trùng và ghi nhật ký khi duyệt.** Khi người duyệt chấp thuận một đơn, hệ thống tự hủy các đơn "chờ duyệt" khác bị trùng giờ (cùng phòng hoặc cùng người mượn) và ghi nhật ký thao tác (ai thực hiện, thời điểm, trạng thái trước và sau).
5. **Quy trình trạng thái tự cập nhật tài nguyên.** Vòng đời đơn đặt phòng: chờ duyệt → đã duyệt → đang sử dụng → đã trả. Khi bắt đầu sử dụng, thiết bị tự chuyển từ kho vào phòng; khi trả phòng, thiết bị tự về kho và hệ thống cập nhật lịch sử mượn/trả. Phía Tài sản cũng có vòng đời tương tự gồm phiếu mượn, bảo trì, điều chuyển, khấu hao (tự trừ giá trị tài sản) và thanh lý.

**Ví dụ minh họa.** Nhân viên Lê Hoàng Cường và nhân viên Vũ Thị Hoa cùng đăng ký phòng họp A1 lúc 9–11h. Người duyệt chấp thuận đơn của Cường; hệ thống tự động hủy đơn của Hoa, ghi rõ lý do "trùng lịch" và lưu vào nhật ký. Không cần thao tác hủy thủ công và luôn truy được trách nhiệm.

**Vị trí mã nguồn.** Chống trùng phòng ([dat_phong.py:111](addons/phong_hop/models/dat_phong.py#L111)); chống trùng thiết bị ([dat_phong.py:167](addons/phong_hop/models/dat_phong.py#L167)); kiểm tra sức chứa ([dat_phong.py:125](addons/phong_hop/models/dat_phong.py#L125)); tự hủy đơn trùng và ghi nhật ký khi duyệt ([dat_phong.py:295](addons/phong_hop/models/dat_phong.py#L295)); bắt đầu sử dụng và chuyển thiết bị ([dat_phong.py:361](addons/phong_hop/models/dat_phong.py#L361)).

---

### Mức 3 — Ứng dụng AI và kết nối bên ngoài

**Nghiệp vụ.** Ứng dụng công nghệ mới để hệ thống thông minh hơn và liên thông với nền tảng bên ngoài.

**Giải pháp của hệ thống.**

1. **Trợ lý AI đặt phòng (mô hình ngôn ngữ lớn Groq).** Thay vì điền từng trường, nhân viên gõ một câu tiếng Việt tự nhiên, ví dụ: "đặt phòng mai 9–11h cho 15 người có máy chiếu và 2 mic". Hệ thống gửi câu này tới mô hình ngôn ngữ lớn Groq để bóc tách thành dữ liệu có cấu trúc (ngày, giờ, số người, thiết bị), sau đó tự tìm phòng trống phù hợp và gợi ý thiết bị cần mượn từ kho. Hệ thống có cơ chế dự phòng: nếu mất mạng hoặc thiếu khóa API, nó tự chuyển sang bóc tách bằng quy tắc, bảo đảm không gián đoạn.

2. **Thông báo qua Telegram (External API).** Ngay khi một đơn được duyệt, hệ thống tự gọi Telegram Bot API gửi thông báo gồm tên phòng, người mượn, số người và khung giờ. Đây là kết nối theo sự kiện tới nền tảng bên ngoài.

**Ví dụ minh họa.** Nhân viên không cần biết vị trí biểu mẫu, chỉ gõ một câu như nhắn tin và AI tự hiểu, tự điền. Khi đơn được duyệt, một tin nhắn Telegram được gửi ngay tới người phụ trách.

**Vị trí mã nguồn.** Gọi AI Groq ([phong_hop_ai_wizard.py:405](addons/phong_hop/wizards/phong_hop_ai_wizard.py#L405)); gửi Telegram ([dat_phong.py:251](addons/phong_hop/models/dat_phong.py#L251)).

**Sơ đồ luồng nghiệp vụ end-to-end** thể hiện đủ ba mức trên một hình: [docs/businessflow/](docs/businessflow/).

---

## II. CẢI TIẾN SO VỚI BẢN KẾ THỪA

| Hạng mục | Loại | Mức | Vị trí |
|----------|------|-----|--------|
| Kiểm tra sức chứa phòng khi đặt | Mới | 2 | [dat_phong.py:125](addons/phong_hop/models/dat_phong.py#L125) |
| Gắn phòng họp vào tài sản (`is_phong_hop`) | Mới | 1 | [tai_san.py:81](addons/tai_san/models/tai_san.py#L81) |
| Trợ lý AI dùng mô hình ngôn ngữ lớn thật (Groq) | Mới | 3 | [phong_hop_ai_wizard.py:405](addons/phong_hop/wizards/phong_hop_ai_wizard.py#L405) |
| Thông báo Telegram khi duyệt | Mới | 3 | [dat_phong.py:251](addons/phong_hop/models/dat_phong.py#L251) |
| Ảnh đại diện nhân viên | Mới | 1 | [nhan_vien.py:17](addons/nhan_su/models/nhan_vien.py#L17) |

Điểm cần nhấn mạnh: bản kế thừa K16 mới chỉ bóc tách yêu cầu bằng biểu thức chính quy (regex), chưa phải AI thật. Nhóm đã nâng lên gọi mô hình ngôn ngữ lớn Groq, đồng thời bổ sung kiểm tra sức chứa (bản cũ có trường sức chứa nhưng bỏ trống không dùng) và gắn phòng họp thành tài sản dùng chung đúng tinh thần Đề 6.

---

## III. ĐỌC HIỂU VÀ VÁ LỖI MÃ NGUỒN CŨ

Trong quá trình kế thừa, nhóm đã phát hiện và sửa năm lỗi khiến bản gốc không cài đặt được hoặc hiển thị sai:

1. **Lỗi cài đặt:** tệp menu được nạp trước các action mà nó tham chiếu, gây lỗi phân tích cú pháp khi cài. Đã sắp xếp lại thứ tự nạp ([phong_hop/\_\_manifest\_\_.py:22](addons/phong_hop/__manifest__.py#L22)).
2. **Lỗi tạo hợp đồng:** mã nguồn dùng `fields.Date.max` không tồn tại. Đã sửa ([hop_dong.py:84](addons/nhan_su/models/hop_dong.py#L84)).
3. **Trùng mã chứng từ:** thiếu sáu bộ sinh mã cho khấu hao, bảo trì, điều chuyển, thanh lý, vị trí; khiến mọi bản ghi mang mã "New". Đã bổ sung ([sequence.xml:27](addons/tai_san/data/sequence.xml#L27)).
4. **Lệch múi giờ:** giờ nhập 09:00 hiển thị thành 16:00 do hệ thống lưu theo UTC. Đã quy đổi múi giờ địa phương ↔ UTC ở Trợ lý AI và thông báo Telegram.
5. **AI bị chặn truy cập:** thiếu header định danh khi gọi Groq nên bị tường lửa từ chối. Đã bổ sung.

---

## IV. HẠ TẦNG VÀ DỮ LIỆU DEMO

- **Cài đặt và chạy demo** trên máy trống: hướng dẫn tại [DEMO_SETUP.md](DEMO_SETUP.md). Hệ thống dựng bằng Docker (Odoo 15 + PostgreSQL), cài ba module và nạp dữ liệu mẫu.
- **Dữ liệu mẫu đầy đủ** cho cả ba module: 8 nhân viên (kèm ảnh và cây quản lý), hợp đồng, chấm công, chứng chỉ, phiếu lương; tài sản kèm khấu hao, mượn, bảo trì, điều chuyển, thanh lý; phòng họp, thiết bị và đơn đặt phòng ([scripts/seed_demo.py](scripts/seed_demo.py)).
- **Lịch sử phát triển** gồm nhiều mốc commit rõ ràng theo từng tính năng, không cập nhật dồn một lần.

---

## Kết luận

Nhóm đã chuyển ba module rời rạc thành một hệ thống ERP thống nhất: dữ liệu nhân sự là nguồn gốc dùng chung (Mức 1), tự động chống trùng và duyệt theo quy trình (Mức 2), ứng dụng AI Groq cùng thông báo Telegram (Mức 3); đồng thời vá nhiều lỗi của bản gốc để hệ thống vận hành được trên thực tế.
