# -*- coding: utf-8 -*-
# Seed dữ liệu demo ĐẦY ĐỦ cho hệ thống Quản lý Tài sản + Phòng họp (Đề 6).
# Bao trùm cả 3 module: HRM (nhan_su) + Tài sản (tai_san) + Phòng họp (phong_hop).
# Chạy: cat scripts/seed_demo.py | docker compose -f docker-compose.run.yml exec -T odoo \
#         odoo shell -d ttdn_test --db_host=db --db_user=odoo --db_password=odoo --no-http
# Idempotent: chạy lại sẽ bỏ qua bản ghi đã tồn tại (theo mã/khoá).
import base64
import logging
import pytz
from datetime import datetime, timedelta, date
_log = logging.getLogger("seed_demo")

# Giờ nhập là giờ LOCAL -> quy đổi UTC để lưu (Odoo lưu Datetime theo UTC)
_TZ = pytz.timezone(env.user.tz or "Asia/Ho_Chi_Minh")
def L2U(naive_local):
    return _TZ.localize(naive_local).astimezone(pytz.utc).replace(tzinfo=None)

def goc(model, key, val, vals):
    rec = env[model].search([(key, "=", val)], limit=1)
    if rec:
        return rec
    vals[key] = val
    return env[model].create(vals)

def goc2(model, domain, vals):
    rec = env[model].search(domain, limit=1)
    if rec:
        return rec
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

TODAY = date.today()
BASE = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

# =====================================================================
# 1. HRM: PHÒNG BAN / CHỨC VỤ
# =====================================================================
pb_giamdoc = goc("phong_ban", "ma_phong", "PB-GD", {"ten_phong": "Ban Giám đốc"})
pb_hanhchinh = goc("phong_ban", "ma_phong", "PB-HC", {"ten_phong": "Phòng Hành chính - Nhân sự"})
pb_kythuat = goc("phong_ban", "ma_phong", "PB-KT", {"ten_phong": "Phòng Kỹ thuật"})
pb_kinhdoanh = goc("phong_ban", "ma_phong", "PB-KD", {"ten_phong": "Phòng Kinh doanh"})

cv_giamdoc = goc("chuc_vu", "ma", "CV-GD", {"ten": "Giám đốc", "phong_ban_id": pb_giamdoc.id, "luong_cung": 40000000, "tro_cap": 5000000})
cv_truongphong = goc("chuc_vu", "ma", "CV-TP", {"ten": "Trưởng phòng", "phong_ban_id": pb_kythuat.id, "luong_cung": 25000000, "tro_cap": 3000000})
cv_nhanvien = goc("chuc_vu", "ma", "CV-NV", {"ten": "Nhân viên", "phong_ban_id": pb_kythuat.id, "luong_cung": 15000000, "tro_cap": 1000000})
cv_hr = goc("chuc_vu", "ma", "CV-HR", {"ten": "Chuyên viên Nhân sự", "phong_ban_id": pb_hanhchinh.id, "luong_cung": 16000000, "tro_cap": 1500000})

# =====================================================================
# 2. HRM: LOẠI PHỤ CẤP + PHỤ CẤP THEO CHỨC VỤ
# =====================================================================
pc_antrua = goc("loai_phu_cap", "ma", "PC-AT", {"ten": "Ăn trưa"})
pc_xangxe = goc("loai_phu_cap", "ma", "PC-XX", {"ten": "Xăng xe đi lại"})
pc_dienthoai = goc("loai_phu_cap", "ma", "PC-DT", {"ten": "Điện thoại"})
for cv, sotien in [(cv_giamdoc, 2000000), (cv_truongphong, 1500000), (cv_nhanvien, 800000), (cv_hr, 1000000)]:
    goc2("phu_cap_chuc_vu", [("chuc_vu_id", "=", cv.id), ("loai_phu_cap_id", "=", pc_antrua.id)],
         {"chuc_vu_id": cv.id, "loai_phu_cap_id": pc_antrua.id, "so_tien": sotien})

# =====================================================================
# 3. HRM: NHÂN VIÊN (có ảnh) + quản lý trực tiếp
# =====================================================================
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
        "ho_ten": ten, "ngay_sinh": ns, "que_quan": qq, "dia_chi": qq,
        "email": ma.lower() + "@dnu.edu.vn", "so_dien_thoai": "09%08d" % (10000000 + i),
        "so_bhxh": "BH%07d" % (1000000 + i), "trang_thai": "dang_lam",
        "phong_ban_id": pb.id, "chuc_vu_id": cv.id,
    }
    anh = tai_anh(i)
    if anh:
        vals["hinh_anh"] = anh
    nv_map[ma] = goc("nhan_vien", "ma_dinh_danh", ma, vals)
for (ma, ten, ns, qq, pb, cv, sep) in nv_data:
    if sep and nv_map.get(ma) and nv_map.get(sep):
        nv_map[ma].quan_ly_id = nv_map[sep].id

# =====================================================================
# 4. HRM: HỢP ĐỒNG (1 hiệu lực / nhân viên) + phụ cấp hợp đồng
# =====================================================================
for (ma, ten, ns, qq, pb, cv, sep) in nv_data:
    nv = nv_map[ma]
    hd = goc2("hop_dong", [("nhan_vien_id", "=", nv.id)], {
        "nhan_vien_id": nv.id, "loai_hop_dong": "chinh_thuc",
        "ngay_bat_dau": "2024-01-01", "trang_thai": "hieu_luc",
        "luong_cung_thang": cv.luong_cung or 15000000,
        "so_ngay_cong_chuan": 26, "so_gio_mot_ngay": 8.0,
        "ghi_chu": "Hợp đồng lao động không xác định thời hạn.",
    })
    if not hd.phu_cap_ids:
        env["phu_cap_hop_dong"].create({"hop_dong_id": hd.id, "loai_phu_cap_id": pc_antrua.id, "so_tien": 800000})
        env["phu_cap_hop_dong"].create({"hop_dong_id": hd.id, "loai_phu_cap_id": pc_xangxe.id, "so_tien": 500000})

# =====================================================================
# 5. HRM: LỊCH SỬ CÔNG TÁC
# =====================================================================
for ma in ["NV001", "NV003", "NV004", "NV005"]:
    nv = nv_map[ma]
    goc2("lich_su_cong_tac", [("nhan_vien_id", "=", nv.id), ("ngay_bat_dau", "=", "2022-01-01")], {
        "nhan_vien_id": nv.id, "phong_ban_id": pb_kythuat.id, "chuc_vu_id": cv_nhanvien.id,
        "ngay_bat_dau": "2022-01-01", "ngay_ket_thuc": "2023-12-31", "trang_thai": "da_ket_thuc",
        "ly_do": "Giai đoạn nhân viên thử việc/chính thức ban đầu."})
    goc2("lich_su_cong_tac", [("nhan_vien_id", "=", nv.id), ("ngay_bat_dau", "=", "2024-01-01")], {
        "nhan_vien_id": nv.id, "phong_ban_id": nv.phong_ban_id.id, "chuc_vu_id": nv.chuc_vu_id.id,
        "ngay_bat_dau": "2024-01-01", "trang_thai": "dang_lam", "ly_do": "Vị trí hiện tại."})

# =====================================================================
# 6. HRM: CHỨNG CHỈ
# =====================================================================
cc_data = [
    ("NV003", "CC-PMP", "Chứng chỉ Quản lý dự án PMP", "PMI", "2023-05-20", "2026-05-20"),
    ("NV004", "CC-AWS", "AWS Certified Developer", "Amazon", "2024-03-10", "2027-03-10"),
    ("NV005", "CC-TOEIC", "TOEIC 850", "IIG Việt Nam", "2023-11-01", "2025-11-01"),
    ("NV002", "CC-HR", "Chứng chỉ Hành chính nhân sự", "ĐH Kinh tế QD", "2022-08-15", False),
]
for ma, mcc, tcc, dvc, ngc, nhh in cc_data:
    vals = {"nhan_vien_id": nv_map[ma].id, "ten_chung_chi": tcc, "don_vi_cap": dvc, "ngay_cap": ngc}
    if nhh:
        vals["ngay_het_han"] = nhh
    goc("chung_chi", "ma_chung_chi", mcc, vals)

# =====================================================================
# 7. HRM: CHẤM CÔNG (5 ngày gần nhất, vài nhân viên)
# =====================================================================
for ma in ["NV003", "NV004", "NV005", "NV006"]:
    nv = nv_map[ma]
    for d in range(1, 6):
        ngay = TODAY - timedelta(days=d)
        if ngay.weekday() >= 5:
            continue
        muon = (ma == "NV005" and d == 2)
        gio_vao_h, gio_vao_m = (8, 45) if muon else (8, 0)
        vals = {
            "nhan_vien_id": nv.id, "ngay": ngay,
            "gio_vao": L2U(datetime.combine(ngay, datetime.min.time()).replace(hour=gio_vao_h, minute=gio_vao_m)),
            "gio_ra": L2U(datetime.combine(ngay, datetime.min.time()).replace(hour=17, minute=30)),
            "gio_nghi_trua": 1.5, "trang_thai": "di_muon" if muon else "co_mat",
        }
        goc2("cham_cong", [("nhan_vien_id", "=", nv.id), ("ngay", "=", ngay)], vals)

# =====================================================================
# 8. HRM: ĐƠN NGHỈ PHÉP + TĂNG CA
# =====================================================================
goc2("don_nghi_phep", [("nhan_vien_id", "=", nv_map["NV004"].id), ("ngay_tu", "=", TODAY + timedelta(days=3))], {
    "nhan_vien_id": nv_map["NV004"].id, "loai_nghi": "co_luong",
    "ngay_tu": TODAY + timedelta(days=3), "ngay_den": TODAY + timedelta(days=4),
    "ly_do": "Việc gia đình", "trang_thai": "da_duyet"})
goc2("don_nghi_phep", [("nhan_vien_id", "=", nv_map["NV006"].id), ("ngay_tu", "=", TODAY + timedelta(days=7))], {
    "nhan_vien_id": nv_map["NV006"].id, "loai_nghi": "khong_luong",
    "ngay_tu": TODAY + timedelta(days=7), "ngay_den": TODAY + timedelta(days=7),
    "ly_do": "Khám sức khỏe", "trang_thai": "gui_duyet"})
ot_ngay = TODAY - timedelta(days=1)
goc2("don_tang_ca", [("nhan_vien_id", "=", nv_map["NV003"].id), ("ngay", "=", ot_ngay)], {
    "nhan_vien_id": nv_map["NV003"].id, "ngay": ot_ngay,
    "gio_bat_dau": L2U(datetime.combine(ot_ngay, datetime.min.time()).replace(hour=18)),
    "gio_ket_thuc": L2U(datetime.combine(ot_ngay, datetime.min.time()).replace(hour=20, minute=30)),
    "he_so": 1.5, "ly_do": "Chạy kịp tiến độ dự án", "trang_thai": "da_duyet"})

# =====================================================================
# 9. HRM: PHIẾU LƯƠNG (kỳ tháng trước) + dòng chi tiết
# =====================================================================
ky_tu = (TODAY.replace(day=1) - timedelta(days=1)).replace(day=1)
ky_den = TODAY.replace(day=1) - timedelta(days=1)
for ma in ["NV003", "NV004"]:
    nv = nv_map[ma]
    luong = nv.chuc_vu_id.luong_cung or 15000000
    goc2("phieu_luong", [("nhan_vien_id", "=", nv.id), ("ngay_tu", "=", ky_tu)], {
        "nhan_vien_id": nv.id, "ngay_tu": ky_tu, "ngay_den": ky_den, "trang_thai": "da_tra",
        "dong_ids": [
            (0, 0, {"ma": "LUONG", "ten": "Lương cứng", "so_tien": luong}),
            (0, 0, {"ma": "PC", "ten": "Phụ cấp ăn trưa + xăng xe", "so_tien": 1300000}),
            (0, 0, {"ma": "BHXH", "ten": "Trừ BHXH (10.5%)", "so_tien": -round(luong * 0.105)}),
        ]})

# =====================================================================
# 10. TÀI SẢN: DANH MỤC + NHÀ CUNG CẤP + TÀI SẢN
# =====================================================================
lt_laptop = goc("loai_tai_san", "ma_loai_tai_san", "LT-LAP", {"ten_loai_tai_san": "Laptop"})
lt_mh = goc("loai_tai_san", "ma_loai_tai_san", "LT-MH", {"ten_loai_tai_san": "Màn hình"})
lt_phong = goc("loai_tai_san", "ma_loai_tai_san", "LT-PH", {"ten_loai_tai_san": "Phòng họp"})
vt_kho = goc("vi_tri", "ma_vi_tri", "VT-KHO", {"ten_vi_tri": "Kho tầng 1"})
vt_t3 = goc("vi_tri", "ma_vi_tri", "VT-T3", {"ten_vi_tri": "Tầng 3 - Khu kỹ thuật"})
ncc = goc("nha_cung_cap", "ma_nha_cung_cap", "NCC-01", {
    "ten_nha_cung_cap": "Công ty TNHH Thế Giới Số", "ten_nguoi_dai_dien": "Nguyễn Văn Sỹ",
    "so_dien_thoai": "02438001122", "email": "sales@tgs.vn"})

# Laptop cấp cho nhân viên (Muon)
ts_lap = {}
for ten, ma_nv, gia in [("Laptop Dell Latitude 5420", "NV003", 22000000),
                        ("Laptop ThinkPad X1", "NV004", 28000000),
                        ("Laptop HP EliteBook", "NV005", 21000000)]:
    ts_lap[ten] = goc("tai_san", "ten_tai_san", ten, {
        "loai_tai_san_id": lt_laptop.id, "nha_cung_cap_id": ncc.id, "vi_tri_hien_tai_id": vt_t3.id,
        "gia_tien_mua": gia, "ngay_mua": "2024-01-15", "trang_thai": "Muon",
        "nguoi_su_dung_id": nv_map[ma_nv].id})
# Màn hình lưu kho (CatGiu)
ts_mh = {}
for ten, gia in [("Màn hình Dell 24inch", 3500000), ("Màn hình LG 27inch", 4200000)]:
    ts_mh[ten] = goc("tai_san", "ten_tai_san", ten, {
        "loai_tai_san_id": lt_mh.id, "nha_cung_cap_id": ncc.id, "vi_tri_hien_tai_id": vt_kho.id,
        "gia_tien_mua": gia, "ngay_mua": "2024-03-10", "trang_thai": "CatGiu"})

# Tài sản = phòng họp (is_phong_hop) + hồ sơ phòng
phong_def = [("Phòng họp A1", 20, "phong_hop", 35000000),
             ("Phòng họp B2", 10, "phong_hop", 20000000),
             ("Hội trường lớn", 100, "hoi_truong", 120000000)]
phong_map = {}
for ten, sc, loai, gia in phong_def:
    ts = goc("tai_san", "ten_tai_san", ten, {
        "loai_tai_san_id": lt_phong.id, "nha_cung_cap_id": ncc.id, "vi_tri_hien_tai_id": vt_kho.id,
        "gia_tien_mua": gia, "ngay_mua": "2023-06-01", "trang_thai": "CatGiu",
        "is_phong_hop": True, "suc_chua": sc})
    phong_map[ten] = goc("quan_ly_phong_hop", "name", ten, {"loai_phong": loai, "suc_chua": sc, "tai_san_id": ts.id})

# =====================================================================
# 11. TÀI SẢN: KHẤU HAO (trên laptop)
# =====================================================================
for ten in ts_lap:
    ts = ts_lap[ten]
    if env["khau_hao"].search_count([("tai_san_id", "=", ts.id)]) == 0:
        env["khau_hao"].create({"tai_san_id": ts.id, "ngay_khau_hao": "2024-12-31",
                                "gia_tri_khau_hao": 2000000, "ghi_chu": "Khấu hao năm 2024"})

# =====================================================================
# 12. TÀI SẢN: PHIẾU MƯỢN (draft + đã trả lịch sử)
# =====================================================================
m1 = ts_mh["Màn hình Dell 24inch"]
m2 = ts_mh["Màn hình LG 27inch"]
goc("phieu_muon", "ma_phieu_muon", "PM-0001", {
    "nhan_vien_id": nv_map["NV006"].id, "tai_san_id": m1.id, "state": "draft",
    "ngay_muon_du_kien": L2U(BASE + timedelta(days=1, hours=9)),
    "ngay_tra_du_kien": L2U(BASE + timedelta(days=3, hours=17)),
    "ghi_chu": "Mượn màn hình phụ phục vụ demo"})
goc("phieu_muon", "ma_phieu_muon", "PM-0002", {
    "nhan_vien_id": nv_map["NV007"].id, "tai_san_id": m2.id, "state": "done",
    "ngay_muon_du_kien": L2U(BASE - timedelta(days=10, hours=-9)),
    "ngay_muon_thuc_te": L2U(BASE - timedelta(days=10, hours=-9)),
    "ngay_tra_du_kien": L2U(BASE - timedelta(days=5, hours=-17)),
    "ngay_tra_thuc_te": L2U(BASE - timedelta(days=5, hours=-16)),
    "ghi_chu": "Đã mượn và trả xong (lịch sử)"})

# =====================================================================
# 13. TÀI SẢN: PHIẾU BẢO TRÌ (draft + done)
# =====================================================================
lap1 = ts_lap["Laptop Dell Latitude 5420"]
lap2 = ts_lap["Laptop ThinkPad X1"]
goc("phieu_bao_tri", "ma_phieu_bao_tri", "BT-0001", {
    "tai_san_id": lap1.id, "chi_phi": 500000, "ghi_chu": "Vệ sinh, thay keo tản nhiệt",
    "ngay_bao_tri": L2U(BASE + timedelta(days=2, hours=9)),
    "ngay_tra": L2U(BASE + timedelta(days=2, hours=17)), "state": "draft"})
goc("phieu_bao_tri", "ma_phieu_bao_tri", "BT-0002", {
    "tai_san_id": lap2.id, "chi_phi": 1200000, "ghi_chu": "Thay pin (đã hoàn thành)",
    "ngay_bao_tri": L2U(BASE - timedelta(days=20, hours=-9)),
    "ngay_bao_tri_thuc_te": L2U(BASE - timedelta(days=20, hours=-9)),
    "ngay_tra": L2U(BASE - timedelta(days=18, hours=-17)),
    "ngay_tra_thuc_te": L2U(BASE - timedelta(days=18, hours=-16)), "state": "done"})

# =====================================================================
# 14. TÀI SẢN: PHIẾU ĐIỀU CHUYỂN (nháp) - đổi vị trí khác hiện tại
# =====================================================================
goc("phieu_dieu_chuyen", "ten_phieu", "DC-0001", {
    "tai_san": m1.id, "vi_tri_moi": vt_t3.id,
    "ngay_dieu_chuyen": L2U(BASE + timedelta(days=1, hours=10)),
    "trang_thai": "nhap", "ghi_chu": "Chuyển màn hình lên tầng 3"})

# =====================================================================
# 15. TÀI SẢN: PHIẾU THANH LÝ (nháp)
# =====================================================================
goc2("thanh_ly", [("tai_san_id", "=", m2.id)], {
    "tai_san_id": m2.id, "ngay_thanh_ly": TODAY, "gia_tri_thanh_ly": 1000000,
    "trang_thai": "draft", "ly_do": "Màn hình cũ, đề xuất thanh lý", "nguoi_xu_ly_id": nv_map["NV002"].id})

# =====================================================================
# 16. THIẾT BỊ (trong kho, sẵn sàng)
# =====================================================================
for ten, loai in [("Máy chiếu Epson EB-X06", "may_chieu"), ("Máy chiếu BenQ", "may_chieu"),
                  ("Micro không dây Shure", "micro"), ("Micro Sennheiser", "micro"),
                  ("Loa JBL", "loa"), ("Điều hòa Daikin", "dieu_hoa")]:
    goc("thiet_bi", "name", ten, {"loai_thiet_bi": loai, "vi_tri_hien_tai": "kho", "trang_thai": "san_sang"})

# =====================================================================
# 17. PHÒNG HỌP: ĐƠN ĐẶT PHÒNG (nhiều trạng thái, giờ đã quy đổi UTC)
# =====================================================================
if env["dat_phong"].search_count([]) == 0:
    d1 = BASE + timedelta(days=1)
    d2 = BASE + timedelta(days=2)
    env["dat_phong"].create({
        "phong_id": phong_map["Phòng họp A1"].id, "nguoi_muon_id": nv_map["NV003"].id,
        "so_nguoi_du_hop": 15, "trang_thai": "đã_duyệt",
        "thoi_gian_muon_du_kien": L2U(d1 + timedelta(hours=9)),
        "thoi_gian_tra_du_kien": L2U(d1 + timedelta(hours=11))})
    env["dat_phong"].create({
        "phong_id": phong_map["Phòng họp B2"].id, "nguoi_muon_id": nv_map["NV006"].id,
        "so_nguoi_du_hop": 8, "trang_thai": "chờ_duyệt",
        "thoi_gian_muon_du_kien": L2U(d1 + timedelta(hours=14)),
        "thoi_gian_tra_du_kien": L2U(d1 + timedelta(hours=16))})
    env["dat_phong"].create({
        "phong_id": phong_map["Hội trường lớn"].id, "nguoi_muon_id": nv_map["NV001"].id,
        "so_nguoi_du_hop": 80, "trang_thai": "đã_trả",
        "thoi_gian_muon_du_kien": L2U(d2 + timedelta(hours=8)),
        "thoi_gian_tra_du_kien": L2U(d2 + timedelta(hours=10))})

env.cr.commit()
print("SEED_DONE | nhan_vien=%d hop_dong=%d lich_su_ct=%d chung_chi=%d cham_cong=%d nghi_phep=%d tang_ca=%d phieu_luong=%d | tai_san=%d khau_hao=%d phieu_muon=%d bao_tri=%d dieu_chuyen=%d thanh_ly=%d | phong=%d thiet_bi=%d dat_phong=%d" % (
    env["nhan_vien"].search_count([]), env["hop_dong"].search_count([]),
    env["lich_su_cong_tac"].search_count([]), env["chung_chi"].search_count([]),
    env["cham_cong"].search_count([]), env["don_nghi_phep"].search_count([]),
    env["don_tang_ca"].search_count([]), env["phieu_luong"].search_count([]),
    env["tai_san"].search_count([]), env["khau_hao"].search_count([]),
    env["phieu_muon"].search_count([]), env["phieu_bao_tri"].search_count([]),
    env["phieu_dieu_chuyen"].search_count([]), env["thanh_ly"].search_count([]),
    env["quan_ly_phong_hop"].search_count([]), env["thiet_bi"].search_count([]),
    env["dat_phong"].search_count([])))
