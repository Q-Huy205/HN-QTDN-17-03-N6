# -*- coding: utf-8 -*-
"""
Mixin tạo bút toán kế toán (account.move) cho các nghiệp vụ tài sản.

✅ Cải tiến bám yêu cầu Đề 6 (Tài sản – Giai đoạn 1):
   "Nút bấm 'Tạo bút toán' -> tạo bản ghi account.move".

Thiết kế tự chủ (self-contained): nếu công ty chưa cài biểu đồ tài khoản
(chart of accounts), mixin sẽ tự tạo sổ nhật ký (journal) và các tài khoản
cần thiết theo nhóm loại tài khoản chuẩn của module `account`. Nhờ vậy nút
"Tạo bút toán" chạy được ngay cả trên DB mới chỉ vừa cài `account`.

Bút toán được tạo ở trạng thái Nháp (draft) để kế toán rà soát rồi mới ghi sổ.
"""
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ButToanMixin(models.AbstractModel):
    _name = "tai_san.but_toan_mixin"
    _description = "Mixin tạo bút toán kế toán cho nghiệp vụ tài sản"

    # =========================================================
    # HẠ TẦNG KẾ TOÁN (tự tạo nếu DB chưa có)
    # =========================================================
    def _bt_get_journal(self):
        """Lấy (hoặc tạo) sổ nhật ký kiểu 'general' cho bút toán tài sản."""
        Journal = self.env["account.journal"]
        company = self.env.company
        journal = Journal.search(
            [("type", "=", "general"), ("company_id", "=", company.id)],
            limit=1,
        )
        if not journal:
            journal = Journal.create({
                "name": "Bút toán tài sản",
                "code": "TS",
                "type": "general",
                "company_id": company.id,
            })
        return journal

    def _bt_get_account(self, code, name, type_xmlid):
        """Lấy (hoặc tạo) tài khoản theo mã + nhóm loại tài khoản chuẩn."""
        Account = self.env["account.account"]
        company = self.env.company
        acc = Account.search(
            [("code", "=", code), ("company_id", "=", company.id)],
            limit=1,
        )
        if not acc:
            acc = Account.create({
                "code": code,
                "name": name,
                "user_type_id": self.env.ref(type_xmlid).id,
                "company_id": company.id,
            })
        return acc

    def _bt_tao_but_toan(self, ref, ngay, so_tien, tk_no, tk_co, dien_giai):
        """Tạo 1 bút toán cân đối (Nợ = Có = so_tien) ở trạng thái Nháp."""
        if not so_tien or so_tien <= 0:
            raise UserError(_("Giá trị bút toán phải lớn hơn 0."))
        move = self.env["account.move"].create({
            "move_type": "entry",
            "journal_id": self._bt_get_journal().id,
            "date": ngay or fields.Date.context_today(self),
            "ref": ref or "/",
            "line_ids": [
                (0, 0, {
                    "name": dien_giai,
                    "account_id": tk_no.id,
                    "debit": so_tien,
                    "credit": 0.0,
                }),
                (0, 0, {
                    "name": dien_giai,
                    "account_id": tk_co.id,
                    "debit": 0.0,
                    "credit": so_tien,
                }),
            ],
        })
        return move

    def _bt_action_xem(self, move):
        """Trả về action mở form bút toán vừa tạo (dùng form gọn hiển thị Nợ/Có)."""
        action = {
            "type": "ir.actions.act_window",
            "name": _("Bút toán kế toán"),
            "res_model": "account.move",
            "res_id": move.id,
            "view_mode": "form",
            "target": "current",
        }
        form_view = self.env.ref("tai_san.view_but_toan_tai_san_form", raise_if_not_found=False)
        if form_view:
            action["views"] = [(form_view.id, "form")]
        return action
