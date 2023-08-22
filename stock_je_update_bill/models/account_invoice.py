from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def invoice_validate(self):
        result = super(AccountInvoice, self).invoice_validate()
        for rec in self:
            for line in rec.invoice_line_ids.filtered(lambda x: x.product_id):
                if line.purchase_line_id and line.purchase_line_id.order_id:
                    for picking in line.purchase_line_id.order_id.picking_ids:
                        move = picking.move_lines.filtered(
                            lambda x: x.product_id.id == line.product_id.id)

                        account_move_id = self.env['account.move'].sudo().search([('stock_move_id','=',move.id)], limit=1)
                        if account_move_id:
                            if not account_move_id.journal_id.update_posted:
                                raise UserError(_(
                                    "Please allow cancelling entries in Journal"))

                            account_move_id.button_cancel()

                            for move_line in account_move_id.line_ids:
                                if move_line.credit:
                                    self._cr.execute('''
                                    UPDATE account_move_line set credit=%s
                                    WHERE id=%s''' %(line.price_subtotal, move_line.id))
                                if move_line.debit:
                                    self._cr.execute('''
                                    UPDATE account_move_line set debit=%s
                                    WHERE id=%s''' % (line.price_subtotal, move_line.id))

                                    account_move_id.post()

                            account_move_id.amount = line.price_subtotal
                            move.value = line.price_subtotal

                        # if not move.account_move_id.journal_id.update_posted:
                        #     raise UserError(_(
                        #         "Please allow cancelling entries in Journal"))
                        #
                        # move.account_move_id.button_cancel()
                        #
                        # for move_line in move.account_move_id.line_ids:
                        #     if move_line.credit:
                        #         self._cr.execute('''
                        #         UPDATE account_move_line set credit=%s
                        #         WHERE id=%s''' %(line.price_subtotal, move_line.id))
                        #     if move_line.debit:
                        #         self._cr.execute('''
                        #         UPDATE account_move_line set debit=%s
                        #         WHERE id=%s''' % (line.price_subtotal, move_line.id))
                        #
                        #         move.account_move_id.post()
                        #
                        # move.account_move_id.amount = line.price_subtotal
                        # move.value = line.price_subtotal

                    value_sum = 0
                    stock_moves = self.env['stock.move'].sudo().search([('product_id','=',line.product_id.id),
                                                                        ('state','=','done')])
                    for stock_move in stock_moves:
                        value_sum = value_sum + stock_move.value
                    final_value = value_sum / line.product_id.qty_available
                    line.product_id.sudo()._set_standard_price(final_value)
                    line.product_id.stock_value = value_sum
                    line.product_id.standard_price = final_value

        return result
