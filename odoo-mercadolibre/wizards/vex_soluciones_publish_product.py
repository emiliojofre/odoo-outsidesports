from odoo import models, fields, api

class VexPublishProductWizard(models.TransientModel):
    _name = 'vex.publish.product.wizard'
    _description = 'Publicar producto en MercadoLibre'

    product_id = fields.Many2one('product.template', string="Producto", required=True)
    name = fields.Char(string="Nombre")
    image_1920 = fields.Binary(string="Imagen")

    # Solo los campos requeridos por la API
    meli_title = fields.Char(string="ML Title", required=True)
    meli_category_vex = fields.Char(string="ML Category ID", required=True)
    meli_price = fields.Float(string="Price", required=True)
    meli_currency_id = fields.Char(string="Currency", required=True)
    meli_available_quantity = fields.Integer(string="Available Quantity", required=True)
    meli_buying_mode = fields.Char(string="Buying Mode", required=True)
    meli_condition = fields.Char(string="Condition", required=True)
    meli_listing_type = fields.Char(string="Listing Type", required=True)
    instance_id = fields.Many2one('vex.instance', string="Instancia", required=True)
    meli_base_price = fields.Float(string="Base Price", help="Original base price")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        product = self.env['product.template'].browse(self.env.context.get('active_id'))
        res['product_id'] = product.id
        res['name'] = product.name
        res['image_1920'] = product.image_1920
        for field in [
            'meli_title', 'meli_category_vex', 'meli_price', 'meli_currency_id',
            'meli_available_quantity', 'meli_buying_mode', 'meli_condition', 'meli_listing_type',
            'meli_base_price',
        ]:
            res[field] = getattr(product, field)
        instance = self.env['vex.instance'].search([('name', 'ilike', 'odoo')], limit=1)
        if instance:
            res['instance_id'] = instance.id
        return res

    def action_publish(self):
        self.ensure_one()
        vals = {
            'meli_title': self.meli_title,
            'meli_category_vex': self.meli_category_vex,
            'meli_price': self.meli_price,
            'meli_currency_id': self.meli_currency_id,
            'meli_available_quantity': self.meli_available_quantity,
            'meli_buying_mode': self.meli_buying_mode,
            'meli_condition': self.meli_condition,
            'meli_listing_type': self.meli_listing_type,
            'meli_base_price': self.meli_base_price
        }
        self.product_id.write(vals)
        return {'type': 'ir.actions.act_window_close'}
    
    def process_meli_response(self, json_response):
        """Procesa la respuesta de MercadoLibre al crear producto."""
        self.ensure_one()
        # Solo si no tiene meli_product_id
        if not self.meli_product_id:
            meli_id = json_response.get('id')
            if meli_id:
                self.meli_product_id = meli_id
                self.meli_permalink = json_response.get('permalink')
                # self.meli_title = json_response.get('title')
                # etc.

                # Ejecutar automáticamente la sincronización de detalles
                self.action_get_details()