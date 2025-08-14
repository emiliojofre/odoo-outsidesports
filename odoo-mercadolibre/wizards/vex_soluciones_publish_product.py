from odoo import models, fields, api

class VexPublishProductWizard(models.TransientModel):
    _name = 'vex.publish.product.wizard'
    _description = 'Publicar producto en MercadoLibre'

    product_id = fields.Many2one('product.template', string="Producto", required=True)
    name = fields.Char(string="Nombre")
    image_1920 = fields.Binary(string="Imagen")

    # Campos a editar (los mismos que en General Info)
    meli_product_id = fields.Char(string="ML Product ID", required=True)
    meli_site_id = fields.Char(string="ML Site ID", required=True)
    meli_status = fields.Char(string="ML Status", required=True)
    meli_sub_status = fields.Char(string="Substatus")
    meli_listing_type = fields.Char(string="Listing Type", required=True)
    meli_condition = fields.Char(string="Condition", required=True)
    meli_title = fields.Char(string="ML Title", required=True)
    meli_permalink = fields.Char(string="Product URL", required=True)
    meli_thumbnail = fields.Char(string="Thumbnail URL")
    meli_domain_id = fields.Char(string="Domain ID")
    meli_catalog_product_id = fields.Char(string="Catalog Product ID")
    meli_category_vex = fields.Char(string="ML Category ID")
    meli_inventory_id = fields.Char(string="Inventory ID")
    meli_tag_ids = fields.Many2many('product.meli.tag', string="ML Tags")
    meli_channel_ids = fields.Many2many('product.meli.channel', string="ML Channels")
    meli_health = fields.Float(string="Health Score")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        product = self.env['product.template'].browse(self.env.context.get('active_id'))
        res['product_id'] = product.id
        res['name'] = product.name
        res['image_1920'] = product.image_1920
        for field in [
            'meli_product_id', 'meli_site_id', 'meli_status', 'meli_sub_status', 'meli_listing_type',
            'meli_condition', 'meli_title', 'meli_permalink', 'meli_thumbnail', 'meli_domain_id',
            'meli_catalog_product_id', 'meli_category_vex', 'meli_inventory_id', 'meli_tag_ids',
            'meli_channel_ids', 'meli_health'
        ]:
            res[field] = getattr(product, field)
        res['product_id'] = product.id
        return res

    def action_publish(self):
        self.ensure_one()
        vals = {
            'meli_product_id': self.meli_product_id,
            'meli_site_id': self.meli_site_id,
            'meli_status': self.meli_status,
            'meli_sub_status': self.meli_sub_status,
            'meli_listing_type': self.meli_listing_type,
            'meli_condition': self.meli_condition,
            'meli_title': self.meli_title,
            'meli_permalink': self.meli_permalink,
            'meli_thumbnail': self.meli_thumbnail,
            'meli_domain_id': self.meli_domain_id,
            'meli_catalog_product_id': self.meli_catalog_product_id,
            'meli_category_vex': self.meli_category_vex,
            'meli_inventory_id': self.meli_inventory_id,
            'meli_tag_ids': [(6, 0, self.meli_tag_ids.ids)],
            'meli_channel_ids': [(6, 0, self.meli_channel_ids.ids)],
            'meli_health': self.meli_health,
        }
        self.product_id.write(vals)
        return {'type': 'ir.actions.act_window_close'}