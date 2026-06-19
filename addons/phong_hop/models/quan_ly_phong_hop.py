# -*- coding: utf-8 -*-
from odoo import models, fields, api


class QuanLyPhongHop(models.Model):
    _name = "quan_ly_phong_hop"
    _description = "Quản lý phòng họp, hội trường"

    active = fields.Boolean(string="Đang hoạt động", default=True)

    name = fields.Char(string="Tên phòng họp", required=True)
    loai_phong = fields.Selection([
        ("phong_hop", "Phòng họp"),
        ("hoi_truong", "Hội trường"),
    ], string="Loại phòng", required=True, default="phong_hop")
    suc_chua = fields.Integer(string="Sức chứa")

    # ✅ Cải tiến (Đề 6): quản lý phòng họp như một tài sản dùng chung
    tai_san_id = fields.Many2one(
        "tai_san",
        string="Tài sản tương ứng",
        domain="[('is_phong_hop','=',True)]",
        help="Phòng họp được gắn với một bản ghi tài sản (is_phong_hop=True) "
             "để quản lý tập trung như tài sản dùng chung.",
    )

    trang_thai = fields.Selection([
        ("trong", "Trống"),
        ("da_muon", "Đã mượn"),
        ("dang_su_dung", "Đang sử dụng"),
    ], string="Trạng thái", compute="_compute_trang_thai", store=True)

    dat_phong_ids = fields.One2many("dat_phong", "phong_id", string="Tất cả lượt đặt/mượn")
    thiet_bi_ids = fields.One2many("thiet_bi", "phong_id", string="Thiết bị đang ở phòng")

    lich_dat_phong_ids = fields.One2many(
        "dat_phong", "phong_id",
        string="Lịch đặt phòng",
        domain=[("trang_thai", "in", ["đã_duyệt", "đang_sử_dụng", "da_duyet", "dang_su_dung"])]
    )

    # Audit log đúng nghĩa
    audit_ids = fields.One2many("lich_su_thay_doi", "phong_id", string="Audit log", readonly=True)

    # Tổng hợp mượn trả theo ngày/phòng
    lich_su_muon_tra_ids = fields.One2many("lich_su_muon_tra", "phong_id", string="Lịch sử mượn trả (theo ngày)", readonly=True)

    @api.depends("dat_phong_ids.trang_thai", "active")
    def _compute_trang_thai(self):
        for record in self:
            if not record.active:
                record.trang_thai = "trong"
                continue

            dang_sd = record.dat_phong_ids.filtered(lambda r: r.trang_thai in ["đang_sử_dụng", "dang_su_dung"])
            da_duyet_or_dang = record.dat_phong_ids.filtered(
                lambda r: r.trang_thai in ["đã_duyệt", "da_duyet", "đang_sử_dụng", "dang_su_dung"]
            )

            if dang_sd:
                record.trang_thai = "dang_su_dung"
            elif da_duyet_or_dang:
                record.trang_thai = "da_muon"
            else:
                record.trang_thai = "trong"

    # ==========================================================
    # ✅ Cải tiến (Đề 6): đồng bộ với tài sản dùng chung
    # ==========================================================
    @api.onchange("tai_san_id")
    def _onchange_tai_san_id(self):
        """Khi gắn tài sản: gợi ý tên phòng và sức chứa từ tài sản."""
        if self.tai_san_id:
            if not self.name:
                self.name = self.tai_san_id.ten_tai_san
            if self.tai_san_id.suc_chua and not self.suc_chua:
                self.suc_chua = self.tai_san_id.suc_chua

    def _sync_tai_san_flag(self):
        """Đảm bảo tài sản được liên kết luôn được đánh dấu là phòng họp."""
        for r in self:
            if r.tai_san_id and not r.tai_san_id.is_phong_hop:
                r.tai_san_id.is_phong_hop = True

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        rec._sync_tai_san_flag()
        return rec

    def write(self, vals):
        res = super().write(vals)
        if "tai_san_id" in vals:
            self._sync_tai_san_flag()
        return res
