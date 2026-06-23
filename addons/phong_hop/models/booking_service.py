# -*- coding: utf-8 -*-
"""
✅ Cải tiến bám yêu cầu Đề 6 (Phòng họp – Giai đoạn 2):
   Model mới `booking_service` quản lý các DỊCH VỤ ĐI KÈM khi đặt phòng họp
   (Trà, Cà phê, Nước suối, Bánh ngọt, Hoa trang trí, Người phục vụ...).

   Được gắn vào `dat_phong.service_ids` (Many2many) hiển thị bằng
   widget `many2many_checkboxes`.
"""
from odoo import models, fields, api


class BookingService(models.Model):
    _name = "booking_service"
    _description = "Dịch vụ đi kèm phòng họp"
    _order = "sequence, name"

    name = fields.Char(string="Tên dịch vụ", required=True)
    sequence = fields.Integer(string="Thứ tự", default=10)
    gia = fields.Monetary(string="Đơn giá", currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency",
        string="Tiền tệ",
        default=lambda self: self.env.company.currency_id.id,
        required=True,
    )
    mo_ta = fields.Char(string="Mô tả")
    active = fields.Boolean(string="Đang áp dụng", default=True)

    _sql_constraints = [
        ("name_unique", "unique(name)", "Tên dịch vụ phải là duy nhất!"),
    ]
