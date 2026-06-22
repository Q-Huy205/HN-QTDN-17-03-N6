# -*- coding: utf-8 -*-
# Vẽ sơ đồ luồng nghiệp vụ dạng LANDSCAPE (lưới 4x3 rắn bò) cho poster.
# Chạy: python scripts/draw_flow_poster.py
from PIL import Image, ImageDraw, ImageFont

OUT = "docs/businessflow/NhomN6_BusinessFlow_Landscape.png"
FONT = "C:/Windows/Fonts/arial.ttf"
FONTB = "C:/Windows/Fonts/arialbd.ttf"

SC = 2  # scale (độ nét)
BW, BH = 300, 128          # kích thước ô
GX, GY = 70, 96            # khoảng cách ngang/dọc
MARGIN = 46
TITLE_H = 92
LEGEND_H = 96
COLS, ROWS = 4, 3

# màu: (fill, outline)
C_STEP = ("#eef0ff", "#5b6bd6")
C_AI   = ("#e7d4ff", "#7d3cff")
C_HRM  = ("#d6f5d6", "#2e9e2e")
C_AUTO = ("#fff3cd", "#d39e00")
C_API  = ("#d4f0ff", "#0094d6")
C_END  = ("#e8e8e8", "#666666")

# (text, color)  — thứ tự 1..12
STEPS = [
    ("[Nhân viên]\n1. Nhập yêu cầu tiếng Việt vào Trợ lý AI", C_STEP),
    ("[AI Groq - LLM]\n2. Bóc tách ngày / giờ / số người / thiết bị", C_AI),
    ("[Hệ thống]\n3. Lọc phòng trống, đủ sức chứa (người mượn từ HRM)", C_HRM),
    ("[Hệ thống]\n4. Gợi ý phòng phù hợp + thiết bị mượn kho", C_STEP),
    ("[Nhân viên]\n5. Chọn phòng → Tạo đăng ký", C_STEP),
    ("[Hệ thống]\n6. Kiểm tra trùng lịch / vượt sức chứa?", C_AUTO),
    ("[Trưởng phòng]\n7. Bấm Duyệt", C_STEP),
    ("[Hệ thống]\n8. Đã duyệt + tự hủy đơn trùng + ghi nhật ký", C_AUTO),
    ("[Hệ thống → Telegram]\n9. Gửi thông báo đã được duyệt", C_API),
    ("[Nhân viên]\n10. Bắt đầu sử dụng (thiết bị: kho→phòng)", C_STEP),
    ("[Nhân viên]\n11. Trả phòng (thiết bị: phòng→kho)", C_STEP),
    ("KẾT THÚC\n12. Cập nhật lịch sử mượn / trả", C_END),
]

# vị trí lưới kiểu rắn bò: hàng 0 trái→phải, hàng 1 phải→trái, hàng 2 trái→phải
def cell(i):
    row = i // COLS
    k = i % COLS
    col = k if row % 2 == 0 else (COLS - 1 - k)
    return col, row

W = MARGIN * 2 + COLS * BW + (COLS - 1) * GX
H = TITLE_H + MARGIN + ROWS * BH + (ROWS - 1) * GY + LEGEND_H
img = Image.new("RGB", (W * SC, H * SC), "white")
d = ImageDraw.Draw(img)
f_title = ImageFont.truetype(FONTB, 27 * SC)
f_box = ImageFont.truetype(FONT, 16 * SC)
f_boxb = ImageFont.truetype(FONTB, 16 * SC)
f_leg = ImageFont.truetype(FONT, 15 * SC)

def S(v):
    return v * SC

def box_xy(i):
    col, row = cell(i)
    x0 = MARGIN + col * (BW + GX)
    y0 = TITLE_H + MARGIN + row * (BH + GY)
    return x0, y0, x0 + BW, y0 + BH

def wrap(text, font, maxw):
    out = []
    for para in text.split("\n"):
        words = para.split(" ")
        line = ""
        for w in words:
            t = (line + " " + w).strip()
            if d.textlength(t, font=font) <= maxw:
                line = t
            else:
                if line:
                    out.append(line)
                line = w
        out.append(line)
    return out

def draw_box(i):
    x0, y0, x1, y1 = [S(v) for v in box_xy(i)]
    fill, outline = STEPS[i][1]
    d.rounded_rectangle([x0, y0, x1, y1], radius=S(14), fill=fill, outline=outline, width=S(2))
    lines = wrap(STEPS[i][0], f_box, S(BW - 24))
    # dòng đầu (actor) in đậm
    total_h = 0
    sizes = []
    for idx, ln in enumerate(lines):
        fnt = f_boxb if idx == 0 else f_box
        bb = d.textbbox((0, 0), ln, font=fnt)
        h = bb[3] - bb[1]
        sizes.append((ln, fnt, h))
        total_h += h + S(4)
    cy = (y0 + y1) / 2 - total_h / 2
    for ln, fnt, h in sizes:
        tw = d.textlength(ln, font=fnt)
        d.text(((x0 + x1) / 2 - tw / 2, cy), ln, font=fnt, fill="#111111")
        cy += h + S(4)

def center(i):
    x0, y0, x1, y1 = box_xy(i)
    return ((x0 + x1) / 2, (y0 + y1) / 2)

def edge_pts(i, j):
    ci, cj = cell(i), cell(j)
    x0a, y0a, x1a, y1a = box_xy(i)
    x0b, y0b, x1b, y1b = box_xy(j)
    if ci[1] == cj[1]:  # cùng hàng
        if cj[0] > ci[0]:  # sang phải
            return (x1a, (y0a + y1a) / 2), (x0b, (y0b + y1b) / 2)
        else:               # sang trái
            return (x0a, (y0a + y1a) / 2), (x1b, (y0b + y1b) / 2)
    else:  # xuống hàng dưới
        return ((x0a + x1a) / 2, y1a), ((x0b + x1b) / 2, y0b)

def arrow(p, q, color="#444444", w=3):
    import math
    p = (S(p[0]), S(p[1])); q = (S(q[0]), S(q[1]))
    d.line([p, q], fill=color, width=S(w))
    ang = math.atan2(q[1] - p[1], q[0] - p[0])
    a = S(11)
    for da in (math.radians(26), -math.radians(26)):
        d.line([q, (q[0] - a * math.cos(ang - da), q[1] - a * math.sin(ang - da))], fill=color, width=S(w))

# vẽ mũi tên nối liên tiếp
for i in range(len(STEPS) - 1):
    p, q = edge_pts(i, i + 1)
    arrow(p, q)

# tiêu đề
title = "LUỒNG NGHIỆP VỤ: ĐẶT PHÒNG HỌP BẰNG AI → DUYỆT → SỬ DỤNG → TRẢ"
tw = d.textlength(title, font=f_title)
d.text((S(W) / 2 - tw / 2, S(26)), title, font=f_title, fill="#1a1a2e")

# các ô
for i in range(len(STEPS)):
    draw_box(i)

# chú thích (legend) dưới cùng
legend = [("#e7d4ff", "#7d3cff", "AI/LLM - Groq (Mức 3)"),
          ("#d4f0ff", "#0094d6", "External API - Telegram (Mức 3)"),
          ("#fff3cd", "#d39e00", "Tự động hóa (Mức 2)"),
          ("#d6f5d6", "#2e9e2e", "Tích hợp HRM (Mức 1)")]
ly = H - LEGEND_H + 28
lx = MARGIN
for fill, outline, text in legend:
    d.rounded_rectangle([S(lx), S(ly), S(lx + 26), S(ly + 22)], radius=S(5), fill=fill, outline=outline, width=S(2))
    d.text((S(lx + 34), S(ly + 1)), text, font=f_leg, fill="#222222")
    lx += 34 + int(d.textlength(text, font=f_leg) / SC) + 40

img.save(OUT)
print("SAVED", OUT, img.size)
