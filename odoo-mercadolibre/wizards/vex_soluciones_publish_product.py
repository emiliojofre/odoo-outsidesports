from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
import logging
import json
from io import BytesIO
from PIL import Image

_logger = logging.getLogger(__name__)

class VexPublishProductWizard(models.TransientModel):
    _name = 'vex.publish.product.wizard'
    _description = 'Publicar producto en MercadoLibre'

    # Información del producto
    product_id = fields.Many2one(
        "product.template", 
        string="Producto", 
        required=True
    )
    name = fields.Char(string="Nombre")
    image_1920 = fields.Binary(string="Imagen")
    meli_thumbnail = fields.Char(
        string="Miniatura (URL)", 
        help="URL de la miniatura del producto", 
        required=True
    )
    instance_id = fields.Many2one(
        "vex.instance", 
        string="Instancia", 
        required=True
    )

    # Campos requeridos por la API
    meli_title = fields.Char(string="Título", required=True)
    meli_category_vex = fields.Char(string="Categoría ID", required=True)
    meli_currency_id = fields.Char(string="Moneda", required=True)
    meli_available_quantity = fields.Integer(string="Cantidad disponible", required=True)
    meli_buying_mode = fields.Char(string="Modo de compra", required=True)
    meli_condition = fields.Char(string="Condición", required=True)
    meli_listing_type = fields.Char(string="Tipo de publicación", required=True)
    percentaje_fee = fields.Float(string="Porcentaje de comisión", help="Porcentaje de comisión de MercadoLibre")
    fixed_fee = fields.Float(string="Comisión fija", help="Comisión fija de MercadoLibre")
    gross_amount = fields.Float(string="Monto bruto", help="Monto bruto antes de comisiones")
    meli_base_price = fields.Float(string="Precio base", help="Precio original del producto")

    # Garantía
    meli_warranty_type = fields.Char(string="Tipo de garantía (ID)", required=True)
    meli_warranty_time = fields.Char(string="Tiempo de garantía", required=True)

    # Descripción
    meli_description = fields.Text(string="Descripción", required=True)

    # Logística
    meli_logistic_type = fields.Selection([
        ("fulfillment", "Fulfillment (Mercado Libre Full)"),
        ("cross_docking", "Cross Docking"),
        ("drop_off", "Drop Off (Sucursal de correo)"),
        ("xd_drop_off", "Cross Docking + Drop Off"),
        ("self_service", "Self Service (Logística propia)"),
        ("not_specified", "No especificado"),
    ],
        default="not_specified",
        string="Tipo de logística",
        required=True,
        help="""
        fulfillment: El producto está en los almacenes de Mercado Libre (Full).
        cross_docking: El vendedor lleva la mercadería a una estación de Mercado Libre y desde ahí se despacha.
        drop_off: El vendedor despacha el producto en una sucursal de correo autorizado por ML.
        xd_drop_off: Variante mixta: drop off + cross docking.
        self_service: El vendedor organiza y paga su propia logística.
        not_specified: No se especifica ningún tipo de logística.
        """
    )

    # Relaciones
    meli_pictures_ids = fields.One2many(
        "vex.publish.product.wizard.image", 
        "wizard_id", 
        string="Imágenes", 
        required=True
    )
    meli_attribute_ids = fields.One2many(
        "vex.publish.product.wizard.attribute", 
        "wizard_id", 
        string="Atributos", 
        required=True
    )

    @api.model
    def set_odoo_image_url_as_thumbnail(self, product):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        image_url = f"{base_url}/web/image/product.template/{product.id}/image_1920"
        product.meli_thumbnail = image_url

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        product = self.env['product.template'].browse(self.env.context.get('active_id'))

        res['product_id'] = product.id
        res['name'] = product.name
        res['image_1920'] = product.image_1920

        # --- Generar URL imagen principal ---
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        variant = product.product_variant_id
        res['meli_thumbnail'] = f"{base_url}/web/image/product.product/{variant.id}/image_1920"

        # --- Copiar campos simples ---
        for field in [
            'meli_title', 'meli_category_vex', 'meli_currency_id',
            'meli_buying_mode',
            'meli_condition', 'meli_listing_type',
            'meli_warranty_time', 'meli_warranty_type',
        ]:
            res[field] = getattr(product, field)

        res['meli_base_price'] = product.list_price
        res['meli_description'] = product.description_sale

        # --- Calcular gross_amount con API de ML ---
        price = product.list_price
        category = product.meli_category_vex
        instance = product.instance_id or self.env['vex.instance'].search([('name', 'ilike', 'RIFCIF ODOO')], limit=1)
        if instance:
            res['instance_id'] = instance.id
        if price and category:
            try:
                url = f"https://api.mercadolibre.com/sites/MLC/listing_prices?price={int(price)}&category_id={category}"
                headers = {"Authorization": f"Bearer {instance.meli_access_token}"}
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    if data and isinstance(data, list):
                        info = data[0]
                        res['percentaje_fee'] = info.get('sale_fee_details', {}).get('percentage_fee', 0)
                        res['fixed_fee'] = info.get('sale_fee_details', {}).get('fixed_fee', 0)
                        res['gross_amount'] = info.get('sale_fee_details', {}).get('gross_amount', 0)

                        # Si gross_amount viene con valor, lo usamos como precio
                        if res['gross_amount']:
                            res['meli_base_price'] = res['gross_amount']

                        _logger.info(f"[default_get] API ML precios: {info}")
                    else:
                        _logger.warning("[default_get] Respuesta vacía o inesperada de la API de Mercado Libre.")
                else:
                    _logger.warning(f"[default_get] Error al consultar la API de ML: {response.status_code} - {response.text}")
            except Exception as e:
                _logger.error(f"[default_get] Error al consumir la API de ML: {e}")

        # --- Imágenes secundarias ---
        pictures = [
            (0, 0, {'url': img.url, 'secure_url': img.secure_url})
            for img in product.meli_pictures_ids
            if img.secure_url != product.meli_thumbnail
        ]
        res['meli_pictures_ids'] = pictures

        # --- Atributos ---
        res['meli_attribute_ids'] = [
            (0, 0, {
                'meli_attribute_id': attr.meli_attribute_id,
                'meli_attribute_name': attr.meli_attribute_name,
                'meli_value_id': attr.meli_value_id,
                'meli_value_name': attr.meli_value_name,
            })
            for attr in product.meli_attribute_ids
        ]

        # --- Instancia por defecto ---
        instance = self.env['vex.instance'].search([('name', 'ilike', 'RIFCIF ODOO')], limit=1)
        if instance:
            res['instance_id'] = instance.id

        # --- Definir tipo logístico por defecto ---
        logistic_type = res.get('meli_logistic_type') or 'not_specified'
        res['meli_logistic_type'] = logistic_type

        return res

    @api.onchange('meli_logistic_type', 'instance_id', 'product_id')
    def _onchange_meli_logistic_type(self):
        for wizard in self:
            qty = 0
            instance = wizard.instance_id
            product = wizard.product_id
            location = False
            if instance and product:
                if wizard.meli_logistic_type == 'fulfillment':
                    location = instance.ml_full_location_id
                else:
                    location = instance.ml_not_full_location_id
                if location:
                    quants = self.env['stock.quant'].search([
                        ('product_id', 'in', product.product_variant_ids.ids),
                        ('location_id', '=', location.id)
                    ])
                    qty = sum(quants.mapped('quantity'))
            wizard.meli_available_quantity = qty
            _logger.info(f"Logistic Type: {wizard.meli_logistic_type} | Location: {location.display_name if location else 'N/A'} | Qty: {qty}")

    @api.onchange('meli_base_price', 'meli_category_vex')
    def _onchange_meli_base_price_or_category(self):
        for wizard in self:
            price = self.meli_base_price
            category = self.meli_category_vex
            instance = wizard.instance_id
            if instance and instance.meli_access_token:
                access_token = instance.meli_access_token
            else:
                access_token = False
            if price and category:
                try:
                    url = f"https://api.mercadolibre.com/sites/MLC/listing_prices?price={int(price)}&category_id={category}"
                    headers = {"Authorization": f"Bearer {access_token}"}
                    response = requests.get(url, headers=headers)
                    if response.status_code == 200:
                        data = response.json()
                        if data and isinstance(data, list):
                            info = data[0]
                            wizard.percentaje_fee = info.get('sale_fee_details', {}).get('percentage_fee', 0)
                            wizard.fixed_fee = info.get('sale_fee_details', {}).get('fixed_fee', 0)
                            wizard.gross_amount = info.get('sale_fee_details', {}).get('gross_amount', 0)
                            if wizard.gross_amount:
                                wizard.meli_base_price = wizard.gross_amount
                                _logger.info(f"API ML precios: {info}")
                        else:
                            _logger.warning("Respuesta vacía o inesperada de la API de Mercado Libre.")
                    else:
                        _logger.warning(f"Error al consultar la API de ML: {response.status_code} - {response.text}")
                except Exception as e:
                    _logger.error(f"Error al consumir la API de ML: {e}")

    def action_publish(self):
        self.ensure_one()
        _logger.info(f"=== Iniciando publicación del producto {self.product_id.name} (ID {self.product_id.id}) ===")

        # --- ACTUALIZAR CAMPOS SIMPLES EN product.template ---
        vals = {
            'meli_title': self.meli_title,
            'meli_category_vex': self.meli_category_vex,
            'meli_currency_id': self.meli_currency_id,
            'meli_available_quantity': self.meli_available_quantity,
            'meli_buying_mode': self.meli_buying_mode,
            'meli_condition': self.meli_condition,
            'meli_listing_type': self.meli_listing_type,
            'meli_base_price': self.meli_base_price,
            'meli_warranty_type': self.meli_warranty_type,
            'meli_warranty_time': self.meli_warranty_time,
            'meli_description': self.meli_description,
            'meli_thumbnail': self.meli_thumbnail,
        }
        self.product_id.write(vals)
        _logger.info(f"Campos simples sincronizados con product.template: {vals}")

        # --- SINCRONIZAR IMÁGENES ---
        self.product_id.meli_pictures_ids.unlink()
        _logger.info("Imágenes previas eliminadas en product.template.")
        for img in self.meli_pictures_ids:
            self.product_id.meli_pictures_ids.create({
                'product_tmpl_id': self.product_id.id,
                'url': img.url,
                'secure_url': img.secure_url,
            })
        _logger.info(f"Imágenes secundarias sincronizadas: {len(self.meli_pictures_ids)}")

        # --- SINCRONIZAR ATRIBUTOS ---
        self.product_id.meli_attribute_ids.unlink()
        _logger.info("Atributos previos eliminados en product.template.")
        for attr in self.meli_attribute_ids:
            self.product_id.meli_attribute_ids.create({
                'product_tmpl_id': self.product_id.id,
                'meli_attribute_id': attr.meli_attribute_id,
                'meli_attribute_name': attr.meli_attribute_name,
                'meli_value_id': attr.meli_value_id,
                'meli_value_name': attr.meli_value_name,
            })
        _logger.info(f"Atributos sincronizados: {len(self.meli_attribute_ids)}")

        # --- TOKEN ---
        instance = self.instance_id
        access_token = instance.meli_access_token
        if not access_token or len(access_token) < 20:
            raise UserError("Token de acceso no válido.")
        _logger.info(f"Access Token usado: {access_token[:10]}... (ocultado por seguridad)")

        # --- ARMAR IMÁGENES CON SUBIDA PREVIA A ML ---
        pictures = []
        if self.meli_thumbnail:
            pictures.append({"source": self.meli_thumbnail})

        # Agregar imágenes secundarias
        for pic in self.meli_pictures_ids:
            if pic.secure_url:
                pictures.append({"source": pic.secure_url})

        if not pictures:
            _logger.warning("No se encontraron imágenes válidas para publicar en ML.")
            raise UserError("Debes agregar al menos una imagen válida para publicar en MercadoLibre.")

        _logger.info(f"Total imágenes preparadas para ML: {len(pictures)}")

        # --- ATRIBUTOS ---
        attributes = [
            {
                "id": attr.meli_attribute_id,
                "value_id": attr.meli_value_id if attr.meli_value_id else None,
                "value_name": attr.meli_value_name if attr.meli_value_name else None,
            }
            for attr in self.meli_attribute_ids
            if attr.meli_attribute_id and (attr.meli_value_id or attr.meli_value_name)
        ]
        _logger.info(f"Atributos preparados para ML: {attributes}")

        # --- TÉRMINOS DE VENTA ---
        sale_terms = []
        if self.meli_warranty_type:
            sale_terms.append({"id": "WARRANTY_TYPE", "value_id": self.meli_warranty_type})
        if self.meli_warranty_time:
            sale_terms.append({"id": "WARRANTY_TIME", "value_name": self.meli_warranty_time})
        _logger.info(f"Términos de venta: {sale_terms}")

        # --- VALIDACIÓN ---
        if not self.meli_category_vex or not self.meli_category_vex.startswith('ML'):
            _logger.error("Categoría inválida detectada.")
            raise UserError("Debes ingresar un ID de categoría válido de MercadoLibre, por ejemplo: MLA1055.")

        # --- PAYLOAD ---
        payload = {
            "title": self.meli_title,
            "category_id": self.meli_category_vex,
            "currency_id": self.meli_currency_id,
            "available_quantity": self.meli_available_quantity,
            "buying_mode": self.meli_buying_mode,
            "condition": self.meli_condition,
            "listing_type_id": self.meli_listing_type,
            "price": self.meli_base_price,
            "pictures": pictures,
            "attributes": attributes,
            "sale_terms": sale_terms,
            "logistic_type": self.meli_logistic_type,
            "description": {
                "plain_text": self.meli_description,
            }
        }
        _logger.info(f"Payload final enviado a ML: {json.dumps(payload, indent=2, ensure_ascii=False)}")

        # --- POST A MERCADO LIBRE ---
        url = "https://api.mercadolibre.com/items"
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        response = requests.post(url, headers=headers, json=payload)
        _logger.info(f"Respuesta de Mercado Libre [{response.status_code}]: {response.text}")

        if response.status_code != 201:
            _logger.error(f"Error al crear el producto en ML: {response.text}")
            raise UserError(f"Error al crear el producto en MercadoLibre: {response.text}")

        # --- ACTUALIZAR CAMPOS DESDE RESPUESTA ---
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
        _logger.info(f"Producto publicado con éxito en ML. ID: {data.get('id')} | Status: {data.get('status')}")

        return {
            'type': 'ir.actions.act_window',
            "res_model": 'product.tempaate',
            "view_model": 'form',
            "res_id": self.product_id.id
        }

