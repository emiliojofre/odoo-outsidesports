
from odoo import api, fields, models, _

class ProductProduct(models.Model):
    _inherit = 'product.product'

    stock_value = fields.Float(
        'Value', compute='_compute_stock_value', store=True)


#
# class StockMove(models.Model):
#     _inherit = "stock.move"
#
#     account_move_id = fields.Many2one('account.move', 'Stock JE ID')
#
#     def _create_account_move_line(self,credit_account_id, debit_account_id, journal_id):
#         if self._is_out():
#             return super(StockMove, self)._create_account_move_line(
#                 self, credit_account_id, debit_account_id, journal_id)
#         else:
#             self.ensure_one()
#             AccountMove = self.env['account.move']
#             quantity = self.env.context.get('forced_quantity', self.product_qty)
#             quantity = quantity if self._is_in() else -1 * quantity
#
#             # Make an informative `ref` on the created account move to differentiate between classic
#             # movements, vacuum and edition of past moves.
#             ref = self.picking_id.name
#             if self.env.context.get('force_valuation_amount'):
#                 if self.env.context.get('forced_quantity') == 0:
#                     ref = 'Revaluation of %s (negative inventory)' % ref
#                 elif self.env.context.get('forced_quantity') is not None:
#                     ref = 'Correction of %s (modification of past move)' % ref
#
#             move_lines = self.with_context(forced_ref=ref)._prepare_account_move_line(quantity, abs(self.value), credit_account_id, debit_account_id)
#             if move_lines:
#                 date = self._context.get('force_period_date', fields.Date.context_today(self))
#                 new_account_move = AccountMove.sudo().create({
#                     'journal_id': journal_id,
#                     'line_ids': move_lines,
#                     'date': date,
#                     'ref': ref,
#                     'stock_move_id': self.id,
#                 })
#                 new_account_move.post()
#
#                 # Added relation between Stock Picking and Account Move.
#                 self.write({'account_move_id': new_account_move.id})
#
#