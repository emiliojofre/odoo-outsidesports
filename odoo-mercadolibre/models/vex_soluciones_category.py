from odoo import api, fields, models

class VexProductCategory(models.Model):
    _inherit         = "product.category"

    meli_code = fields.Char('Código ML')
    server_meli = fields.Boolean('server_meli')
    instance_id = fields.Many2one('vex.instance', string='instance')
    meli_category_id = fields.Char(
        string='Meli Category ID',
        help='ID of the category in Mercado Libre',
        copy=False)
    