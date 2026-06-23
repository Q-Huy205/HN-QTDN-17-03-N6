# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ThanhLy(models.Model):
    _name = "thanh_ly"
    _description = "Thanh lý tài sản"
    _inherit = ["mail.thread", "mail.activity.mixin", "tai_san.but_toan_mixin"]
    _order = "ma_thanh_ly desc"

    _sql_constraints = [
        ("ma_thanh_ly_unique", "unique(ma_thanh_ly)", "Mã thanh lý phải là duy nhất!"),
    ]

    currency_id = fields.Many2one(
        "res.currency",
        string="Tiền tệ",
        default=lambda self: self.env.company.currency_id.id,
        required=True,
    )

    ma_thanh_ly = fields.Char(string="Mã thanh lý", copy=False, default="New", tracking=True)

    ngay_thanh_ly = fields.Date(
        string="Ngày thanh lý",
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )

    tai_san_id = fields.Many2one("tai_san", string="Tài sản", required=True, tracking=True)

    gia_tri_thanh_ly = fields.Monetary(
        string="Giá trị thanh lý",
        currency_field="currency_id",
        required=True,
        tracking=True,
    )

    TRANG_THAI = [
        ("draft", "Nháp"),
        ("confirmed", "Đã xác nhận"),
        ("done", "Hoàn thành"),
        ("cancelled", "Đã hủy"),
    ]
    trang_thai = fields.Selection(
        selection=TRANG_THAI,
        string="Trạng thái",
        default="draft",
        required=True,
        tracking=True,
    )

    ly_do = fields.Text(string="Lý do thanh lý")
    nguoi_xu_ly_id = fields.Many2one("nhan_vien", string="Người xử lý", required=True, tracking=True)

    # ✅ Bút toán kế toán ghi nhận thu từ thanh lý (Nợ tiền / Có thu nhập khác)
    move_id = fields.Many2one(
        "account.move",
        string="Bút toán kế toán",
        readonly=True,
        copy=False,
        tracking=True,
    )

    # =========================================================
    # CREATE: SEQUENCE + default currency theo tài sản (nếu có)
    # =========================================================
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("ma_thanh_ly", "New") in (False, "", "New"):
                vals["ma_thanh_ly"] = self.env["ir.sequence"].next_by_code("thanh_ly") or "New"

            # Nếu chọn tài sản trước, ưu tiên currency của tài sản
            if vals.get("tai_san_id") and not vals.get("currency_id"):
                ts = self.env["tai_san"].browse(vals["tai_san_id"])
                if ts and ts.currency_id:
                    vals["currency_id"] = ts.currency_id.id

        return super().create(vals_list)

    # =========================================================
    # CONSTRAINTS
    # =========================================================
    @api.constrains("tai_san_id")
    def _check_one_active_liquidation(self):
        for rec in self:
            if not rec.tai_san_id:
                continue
            # Nếu tài sản đã trỏ sang phiếu khác => chặn
            if rec.tai_san_id.thanh_ly_id and rec.tai_san_id.thanh_ly_id != rec:
                raise ValidationError(_("Tài sản %s đã có phiếu thanh lý khác!") % rec.tai_san_id.ten_tai_san)

    @api.constrains("trang_thai", "tai_san_id")
    def _check_asset_state(self):
        for rec in self:
            if not rec.tai_san_id:
                continue

            # Khi confirmed/done: không cho nếu tài sản đang mượn hoặc bảo trì
            if rec.trang_thai in ("confirmed", "done") and rec.tai_san_id.trang_thai in ("Muon", "BaoTri"):
                raise ValidationError(_("Không thể thanh lý tài sản đang mượn hoặc bảo trì!"))

            # Nếu done thì tài sản phải là DaThanhLy (để tránh lệch)
            if rec.trang_thai == "done" and rec.tai_san_id.trang_thai != "DaThanhLy":
                raise ValidationError(_("Phiếu đã hoàn thành thì tài sản phải ở trạng thái 'Đã thanh lý'."))

    # =========================================================
    # ACTIONS
    # =========================================================
    def action_confirm(self):
        self.ensure_one()
        if self.trang_thai != "draft":
            raise ValidationError(_("Chỉ có thể xác nhận phiếu ở trạng thái Nháp!"))

        if self.tai_san_id.trang_thai in ("Muon", "BaoTri"):
            raise ValidationError(_("Không thể xác nhận: tài sản đang mượn hoặc bảo trì!"))

        self.write({"trang_thai": "confirmed"})

    def action_done(self):
        self.ensure_one()
        if self.trang_thai != "confirmed":
            raise ValidationError(_("Phiếu cần được xác nhận trước khi hoàn thành!"))

        if self.tai_san_id.trang_thai in ("Muon", "BaoTri"):
            raise ValidationError(_("Không thể hoàn thành: tài sản đang mượn hoặc bảo trì!"))

        # Đồng bộ sang tài sản
        self.tai_san_id.write({
            "trang_thai": "DaThanhLy",
            "thanh_ly_id": self.id,
            "nguoi_su_dung_id": False,
        })
        self.write({"trang_thai": "done"})

    def action_cancel(self):
        self.ensure_one()
        if self.trang_thai not in ("draft", "confirmed"):
            raise ValidationError(_("Không thể hủy phiếu đã hoàn thành!"))

        vals = {"trang_thai": "CatGiu", "nguoi_su_dung_id": False}
        if self.tai_san_id.thanh_ly_id == self:
            vals["thanh_ly_id"] = False
        self.tai_san_id.write(vals)

        self.write({"trang_thai": "cancelled"})

    # =========================================================
    # BÚT TOÁN KẾ TOÁN (account.move)
    # =========================================================
    def action_tao_but_toan(self):
        """Tạo bút toán thu thanh lý: Nợ 111 (Tiền) / Có 711 (Thu nhập khác)."""
        self.ensure_one()
        if self.trang_thai not in ("confirmed", "done"):
            raise ValidationError(_("Chỉ tạo bút toán khi phiếu đã xác nhận hoặc hoàn thành!"))
        if self.move_id:
            raise ValidationError(_("Phiếu thanh lý này đã có bút toán!"))
        tk_no = self._bt_get_account(
            "1111", "Tiền mặt", "account.data_account_type_current_assets"
        )
        tk_co = self._bt_get_account(
            "711", "Thu nhập khác (thanh lý TSCĐ)", "account.data_account_type_other_income"
        )
        dien_giai = _("Thu thanh lý tài sản: %s") % (self.tai_san_id.ten_tai_san or "")
        move = self._bt_tao_but_toan(
            ref=self.ma_thanh_ly,
            ngay=self.ngay_thanh_ly,
            so_tien=self.gia_tri_thanh_ly,
            tk_no=tk_no,
            tk_co=tk_co,
            dien_giai=dien_giai,
        )
        self.move_id = move.id
        self.message_post(body=_("Đã tạo bút toán thanh lý %s.") % move.name)
        return self._bt_action_xem(move)

    def action_xem_but_toan(self):
        self.ensure_one()
        if not self.move_id:
            raise ValidationError(_("Phiếu này chưa có bút toán!"))
        return self._bt_action_xem(self.move_id)
