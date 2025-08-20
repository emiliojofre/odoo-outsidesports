from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
import logging
_logger = logging.getLogger(__name__)

class VexPublishProductWizard(models.TransientModel):
    _name = 'vex.publish.product.wizard'
    _description = 'Publicar producto en MercadoLibre'

    product_id = fields.Many2one('product.template', string="Producto", required=True)
    name = fields.Char(string="Nombre")
    image_1920 = fields.Binary(string="Imagen")

    # Solo los campos requeridos por la API
    meli_title = fields.Char(string="ML Title", required=True)
    meli_category_vex = fields.Char(string="ML Category ID", required=True)
    meli_currency_id = fields.Char(string="Currency", required=True)
    meli_available_quantity = fields.Integer(string="Available Quantity", required=True)
    meli_buying_mode = fields.Char(string="Buying Mode", required=True)
    meli_condition = fields.Char(string="Condition", required=True)
    meli_listing_type = fields.Char(string="Listing Type", required=True)
    instance_id = fields.Many2one('vex.instance', string="Instancia", required=True)
    meli_base_price = fields.Float(string="Base Price", help="Original base price")
    meli_pictures_ids = fields.One2many('vex.publish.product.wizard.image', 'wizard_id', string="ML Pictures")
    meli_attribute_ids = fields.One2many('vex.publish.product.wizard.attribute', 'wizard_id', string="ML Attributes")
    meli_warranty_type = fields.Char(string="Tipo de Garantía (ID)")
    meli_warranty_time = fields.Char(string="Tiempo de Garantía")


    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        product = self.env['product.template'].browse(self.env.context.get('active_id'))

        res['product_id'] = product.id
        res['name'] = product.name
        res['image_1920'] = product.image_1920

        for field in [
            'meli_title', 'meli_category_vex', 'meli_currency_id',
            'meli_available_quantity', 'meli_buying_mode',
            'meli_condition', 'meli_listing_type', 'meli_base_price',
        ]:
            res[field] = getattr(product, field)

        # Copiar imágenes al wizard
        res['meli_pictures_ids'] = [
            (0, 0, {'secure_url': img.secure_url})
            for img in product.meli_pictures_ids
        ]

        # Copiar atributos al wizard (todos los campos relevantes)
        res['meli_attribute_ids'] = [
            (0, 0, {
                'meli_attribute_id': attr.meli_attribute_id,
                'meli_attribute_name': attr.meli_attribute_name,
                'meli_value_id': attr.meli_value_id,
                'meli_value_name': attr.meli_value_name,
            })
            for attr in product.meli_attribute_ids
        ]

        # Instancia por defecto
        instance = self.env['vex.instance'].search([('name', 'ilike', 'RIFCIF ODOO')], limit=1)
        if instance:
            res['instance_id'] = instance.id

        return res

    def action_publish(self):
        self.ensure_one()
        # Actualizar campos simples en producto.template
        vals = {
            'meli_title': self.meli_title,
            'meli_category_vex': self.meli_category_vex,
            'meli_currency_id': self.meli_currency_id,
            'meli_available_quantity': self.meli_available_quantity,
            'meli_buying_mode': self.meli_buying_mode,
            'meli_condition': self.meli_condition,
            'meli_listing_type': self.meli_listing_type,
            'meli_base_price': self.meli_base_price,
        }
        self.product_id.write(vals)

        # Sincronizar imágenes
        self.product_id.meli_pictures_ids.unlink()
        for img in self.meli_pictures_ids:
            self.product_id.meli_pictures_ids.create({
                'product_tmpl_id': self.product_id.id,
                'secure_url': img.secure_url,
            })

        # Sincronizar atributos
        self.product_id.meli_attribute_ids.unlink()
        for attr in self.meli_attribute_ids:
            self.product_id.meli_attribute_ids.create({
                'product_tmpl_id': self.product_id.id,
                'meli_attribute_id': attr.meli_attribute_id,
                'meli_attribute_name': attr.meli_attribute_name,
                'meli_value_id': attr.meli_value_id,
                'meli_value_name': attr.meli_value_name,
            })

        instance = self.instance_id
        access_token = instance.meli_access_token

        if not access_token or len(access_token) < 20:
            raise UserError("Token de acceso no válido.")
        
        _logger.info(f"Access Token usado: {access_token}")

        url = "https://api.mercadolibre.com/items"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # Imágenes desde el wizard
        pictures = [
            {"source": img.secure_url}
            for img in self.meli_pictures_ids if img.secure_url
        ]
        if not pictures:
            raise UserError("Debes agregar al menos una imagen con URL segura (https) para publicar en MercadoLibre.")

        # Atributos desde el wizard
        attributes = [
            {
                "id": attr.meli_attribute_id,
                "value_id": attr.meli_value_id if attr.meli_value_id else None,
                "value_name": attr.meli_value_name if attr.meli_value_name else None,
            }
            for attr in self.meli_attribute_ids
            if attr.meli_attribute_id and (attr.meli_value_id or attr.meli_value_name)
        ]

        # Términos de venta
        sale_terms = []
        if self.meli_warranty_type:
            sale_terms.append({
                "id": "WARRANTY_TYPE",
                "value_id": self.meli_warranty_type,
            })
        if self.meli_warranty_time:
            sale_terms.append({
                "id": "WARRANTY_TIME",
                "value_name": self.meli_warranty_time
            })

        # Validación de categoría
        if not self.meli_category_vex or not self.meli_category_vex.startswith('ML'):
            raise UserError("Debes ingresar un ID de categoría válido de MercadoLibre, por ejemplo: MLA1055.")

        # Precio entero si es CLP
        price = int(self.meli_base_price) if self.meli_currency_id == 'CLP' else self.meli_base_price

        # Payload final
        payload = {
            "title": self.meli_title,
            "category_id": self.meli_category_vex,
            "currency_id": self.meli_currency_id,
            "available_quantity": self.meli_available_quantity,
            "buying_mode": self.meli_buying_mode,
            "condition": self.meli_condition,
            "listing_type_id": self.meli_listing_type,
            "price": price,
            "pictures": pictures,
            "attributes": attributes,
            "sale_terms": sale_terms,
        }

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 201:
            data = response.json()
            self.product_id.write({
                'meli_product_id': data.get('id'),
                'meli_site_id': data.get('site_id'),
                'meli_status': data.get('status'),
                'meli_sub_status': ','.join(data.get('sub_status', [])) if data.get('sub_status') else False,
                'meli_listing_type': data.get('listing_type_id'),
                'meli_condition': data.get('condition'),
                'meli_title': data.get('title'),
                'meli_permalink': data.get('permalink'),
                'meli_thumbnail': data.get('thumbnail'),
                'meli_domain_id': data.get('domain_id'),
                'meli_catalog_product_id': data.get('catalog_product_id'),
                'meli_category_vex': data.get('category_id'),
                'meli_inventory_id': data.get('inventory_id'),
                'meli_health': data.get('health'),
            })
            if data.get('tags'):
                tag_model = self.env['product.meli.tag']
                tag_ids = []
                for tag_name in data['tags']:
                    tag = tag_model.search([('name', '=', tag_name)], limit=1)
                    if not tag:
                        tag = tag_model.create({'name': tag_name})
                    tag_ids.append(tag.id)
                self.product_id.write({'meli_tag_ids': [(6, 0, tag_ids)]})
            if data.get('id'):
                self.product_id.action_get_details()
        else:
            raise UserError(f"Error al crear el producto en MercadoLibre: {response.text}")

        return {'type': 'ir.actions.act_window_close'}
    
    