# -*- coding: utf-8 -*-
# Seed dữ liệu demo cho hệ thống Quản lý Tài sản + Phòng họp (Đề 6).
# Chạy: cat scripts/seed_demo.py | docker compose -f docker-compose.run.yml exec -T odoo \
#         odoo shell -d ttdn_test --db_host=db --db_user=odoo --db_password=odoo --no-http
# Idempotent: chạy lại sẽ bỏ qua bản ghi đã tồn tại (theo mã/khoá).
import base64
import logging
from datetime import datetime, timedelta
_log = logging.getLogger("seed_demo")

def goc(model, key, val, vals):
    rec = env[model].search([(key, "=", val)], limit=1)
    if rec:
        return rec
    vals[key] = val
    return env[model].create(vals)

def tai_anh(idx):
    try:
        import requests
        r = requests.get("https://i.pravatar.cc/300?img=%d" % idx, timeout=15)
        if r.status_code == 200 and r.content:
            return base64.b64encode(r.content)
    except Exception as e:
        _log.warning("Khong tai duoc anh %s: %s", idx, e)
    return False

# ============ PHÒNG BAN ============
pb_giamdoc = goc("phong_ban", "ma_phong", "PB-GD", {"ten_phong": "Ban Giám đốc"})
pb_hanhchinh = goc("phong_ban", "ma_phong", "PB-HC", {"ten_phong": "Phòng Hành chính - Nhân sự"})
pb_kythuat = goc("phong_ban", "ma_phong", "PB-KT", {"ten_phong": "Phòng Kỹ thuật"})
pb_kinhdoanh = goc("phong_ban", "ma_phong", "PB-KD", {"ten_phong": "Phòng Kinh doanh"})

# ============ CHỨC VỤ ============
cv_giamdoc = goc("chuc_vu", "ma", "CV-GD", {"ten": "Giám đốc", "phong_ban_id": pb_giamdoc.id, "luong_cung": 40000000, "tro_cap": 5000000})
cv_truongphong = goc("chuc_vu", "ma", "CV-TP", {"ten": "Trưởng phòng", "phong_ban_id": pb_kythuat.id, "luong_cung": 25000000, "tro_cap": 3000000})
cv_nhanvien = goc("chuc_vu", "ma", "CV-NV", {"ten": "Nhân viên", "phong_ban_id": pb_kythuat.id, "luong_cung": 15000000, "tro_cap": 1000000})
cv_hr = goc("chuc_vu", "ma", "CV-HR", {"ten": "Chuyên viên Nhân sự", "phong_ban_id": pb_hanhchinh.id, "luong_cung": 16000000, "tro_cap": 1500000})

# ============ NHÂN VIÊN (có ảnh) ============
nv_data = [
    ("NV001", "Nguyễn Văn An", "1985-03-12", "Hà Nội", pb_giamdoc, cv_giamdoc, None),
    ("NV002", "Trần Thị Bình", "1990-07-22", "Hải Phòng", pb_hanhchinh, cv_hr, "NV001"),
    ("NV003", "Lê Hoàng Cường", "1988-11-05", "Đà Nẵng", pb_kythuat, cv_truongphong, "NV001"),
    ("NV004", "Phạm Thị Dung", "1995-02-18", "Nam Định", pb_kythuat, cv_nhanvien, "NV003"),
    ("NV005", "Hoàng Văn Em", "1993-09-30", "Thái Bình", pb_kythuat, cv_nhanvien, "NV003"),
    ("NV006", "Vũ Thị Hoa", "1996-06-14", "Bắc Ninh", pb_kinhdoanh, cv_nhanvien, "NV001"),
    ("NV007", "Đỗ Minh Khôi", "1992-12-01", "Hưng Yên", pb_kythuat, cv_nhanvien, "NV003"),
    ("NV008", "Bùi Thị Lan", "1994-04-27", "Hà Nam", pb_kinhdoanh, cv_nhanvien, "NV001"),
]
nv_map = {}
for i, (ma, ten, ns, qq, pb, cv, sep) in enumerate(nv_data, start=1):
    vals = {
        "ho_ten": ten, "ngay_sinh": ns, "que_quan": qq,
        "dia_chi": qq, "email": ma.lower() + "@dnu.edu.vn",
        "so_dien_thoai": "09%08d" % (10000000 + i),
        "so_bhxh": "BH%07d" % (1000000 + i),
        "trang_thai": "dang_lam",
        "phong_ban_id": pb.id, "chuc_vu_id": cv.id,
    }
    anh = tai_anh(i)
    if anh:
        vals["hinh_anh"] = anh
    rec = goc("nhan_vien", "ma_dinh_danh", ma, vals)
    nv_map[ma] = rec
# Gán quản lý trực tiếp
for (ma, ten, ns, qq, pb, cv, sep) in nv_data:
    if sep and nv_map.get(ma) and nv_map.get(sep):
        nv_map[ma].quan_ly_id = nv_map[sep].id

# ============ DANH MỤC TÀI SẢN ============
lt_laptop = goc("loai_tai_san", "ma_loai_tai_san", "LT-LAP", {"ten_loai_tai_san": "Laptop"})
lt_mh = goc("loai_tai_san", "ma_loai_tai_san", "LT-MH", {"ten_loai_tai_san": "Màn hình"})
lt_phong = goc("loai_tai_san", "ma_loai_tai_san", "LT-PH", {"ten_loai_tai_san": "Phòng họp"})
vt_kho = goc("vi_tri", "ma_vi_tri", "VT-KHO", {"ten_vi_tri": "Kho tầng 1"})
vt_t3 = goc("vi_tri", "ma_vi_tri", "VT-T3", {"ten_vi_tri": "Tầng 3 - Khu kỹ thuật"})
ncc = goc("nha_cung_cap", "ma_nha_cung_cap", "NCC-01", {
    "ten_nha_cung_cap": "Công ty TNHH Thế Giới Số", "ten_nguoi_dai_dien": "Nguyễn Văn Sỹ",
    "so_dien_thoai": "02438001122", "email": "sales@tgs.vn"})

# ============ TÀI SẢN ============
# Laptop cấp cho nhân viên (trang_thai = Muon, có người dùng)
ts_laptop = [
    ("Laptop Dell Latitude 5420", "NV003", 22000000),
    ("Laptop ThinkPad X1", "NV004", 28000000),
    ("Laptop HP EliteBook", "NV005", 21000000),
]
for ten, ma_nv, gia in ts_laptop:
    goc("tai_san", "ten_tai_san", ten, {
        "loai_tai_san_id": lt_laptop.id, "nha_cung_cap_id": ncc.id,
        "vi_tri_hien_tai_id": vt_t3.id, "gia_tien_mua": gia, "ngay_mua": "2024-01-15",
        "trang_thai": "Muon", "nguoi_su_dung_id": nv_map[ma_nv].id})
# Tài sản lưu kho
for ten, gia in [("Màn hình Dell 24inch", 3500000), ("Màn hình LG 27inch", 4200000)]:
    goc("tai_san", "ten_tai_san", ten, {
        "loai_tai_san_id": lt_mh.id, "nha_cung_cap_id": ncc.id,
        "vi_tri_hien_tai_id": vt_kho.id, "gia_tien_mua": gia, "ngay_mua": "2024-03-10",
        "trang_thai": "CatGiu"})

# ============ TÀI SẢN = PHÒNG HỌP (is_phong_hop) + HỒ SƠ PHÒNG ============
phong_def = [
    ("Phòng họp A1", 20, "phong_hop", 35000000),
    ("Phòng họp B2", 10, "phong_hop", 20000000),
    ("Hội trường lớn", 100, "hoi_truong", 120000000),
]
phong_map = {}
for ten, sc, loai, gia in phong_def:
    ts = goc("tai_san", "ten_tai_san", ten, {
        "loai_tai_san_id": lt_phong.id, "nha_cung_cap_id": ncc.id,
        "vi_tri_hien_tai_id": vt_kho.id, "gia_tien_mua": gia, "ngay_mua": "2023-06-01",
        "trang_thai": "CatGiu", "is_phong_hop": True, "suc_chua": sc})
    ph = goc("quan_ly_phong_hop", "name", ten, {"loai_phong": loai, "suc_chua": sc, "tai_san_id": ts.id})
    phong_map[ten] = ph

# ============ THIẾT BỊ (trong kho, sẵn sàng) ============
for ten, loai in [("Máy chiếu Epson EB-X06", "may_chieu"), ("Máy chiếu BenQ", "may_chieu"),
                  ("Micro không dây Shure", "micro"), ("Micro Sennheiser", "micro"),
                  ("Loa JBL", "loa"), ("Điều hòa Daikin", "dieu_hoa")]:
    goc("thiet_bi", "name", ten, {"loai_thiet_bi": loai, "vi_tri_hien_tai": "kho", "trang_thai": "san_sang"})

# ============ ĐƠN ĐẶT PHÒNG (nhiều trạng thái) ============
if env["dat_phong"].search_count([]) == 0:
    base = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    d1 = base + timedelta(days=1)
    d2 = base + timedelta(days=2)
    env["dat_phong"].create({
        "phong_id": phong_map["Phòng họp A1"].id, "nguoi_muon_id": nv_map["NV003"].id,
        "so_nguoi_du_hop": 15, "trang_thai": "đã_duyệt",
        "thoi_gian_muon_du_kien": d1 + timedelta(hours=9),
        "thoi_gian_tra_du_kien": d1 + timedelta(hours=11)})
    env["dat_phong"].create({
        "phong_id": phong_map["Phòng họp B2"].id, "nguoi_muon_id": nv_map["NV006"].id,
        "so_nguoi_du_hop": 8, "trang_thai": "chờ_duyệt",
        "thoi_gian_muon_du_kien": d1 + timedelta(hours=14),
        "thoi_gian_tra_du_kien": d1 + timedelta(hours=16)})
    env["dat_phong"].create({
        "phong_id": phong_map["Hội trường lớn"].id, "nguoi_muon_id": nv_map["NV001"].id,
        "so_nguoi_du_hop": 80, "trang_thai": "đã_trả",
        "thoi_gian_muon_du_kien": d2 + timedelta(hours=8),
        "thoi_gian_tra_du_kien": d2 + timedelta(hours=10)})

env.cr.commit()
print("SEED_DONE | nhan_vien=%d phong_ban=%d tai_san=%d phong_hop=%d thiet_bi=%d dat_phong=%d" % (
    env["nhan_vien"].search_count([]), env["phong_ban"].search_count([]),
    env["tai_san"].search_count([]), env["quan_ly_phong_hop"].search_count([]),
    env["thiet_bi"].search_count([]), env["dat_phong"].search_count([])))
