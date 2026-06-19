# Module Quản lý Phòng họp (Đề 6)

Kế thừa và cải tiến từ nhóm K16 N10
(nguồn: https://github.com/tranchienthinh-0000/TTDN-16-05-N10).

## Cải tiến so với bản gốc

1. **Validate sức chứa** — `dat_phong.so_nguoi_du_hop` không được vượt `quan_ly_phong_hop.suc_chua`.
2. **Phòng họp là tài sản dùng chung** — liên kết `quan_ly_phong_hop.tai_san_id` ↔ `tai_san.is_phong_hop`.
3. **AI wizard dùng LLM thật (Groq)** — trích xuất yêu cầu đặt phòng từ ngôn ngữ tự nhiên, fallback regex khi không có key.
4. **Thông báo Telegram (External API)** — gửi tin nhắn khi đặt phòng được duyệt.

## Cấu hình (Settings ▸ Technical ▸ Parameters ▸ System Parameters)

| Key | Ý nghĩa | Ví dụ |
|-----|---------|-------|
| `phong_hop.groq_api_key` | API key GroqCloud (https://console.groq.com) | `gsk_...` |
| `phong_hop.groq_model` | (tùy chọn) model LLM | `llama-3.3-70b-versatile` |
| `phong_hop.telegram_bot_token` | Bot token từ @BotFather | `123456:ABC...` |
| `phong_hop.telegram_chat_id` | Chat/Group ID nhận thông báo | `-1001234567890` |

> Không cấu hình các key trên thì hệ thống vẫn chạy bình thường:
> - Thiếu Groq key → AI wizard tự dùng parser regex.
> - Thiếu Telegram → bỏ qua gửi thông báo (chỉ ghi log).
