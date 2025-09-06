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

    product_id = fields.Many2one('product.template', string="Producto", required=True)
    name = fields.Char(string="Nombre")
    image_1920 = fields.Binary(string="Imagen")
    meli_thumbnail = fields.Char(string="Thumbnail URL", help="URL of the product thumbnail", required=True)

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
    meli_pictures_ids = fields.One2many('vex.publish.product.wizard.image', 'wizard_id', string="ML Pictures", required=True)
    meli_attribute_ids = fields.One2many('vex.publish.product.wizard.attribute', 'wizard_id', string="ML Attributes", required=True)
    meli_warranty_type = fields.Char(string="Tipo de Garantía (ID)", required=True)
    meli_warranty_time = fields.Char(string="Tiempo de Garantía", required=True)
    meli_description = fields.Text(string="Descripción en MercadoLibre", required=True)
    meli_logistic_type = fields.Selection([
    ('fulfillment', 'Fulfillment (Mercado Libre Full)'),
    ('cross_docking', 'Cross Docking'),
    ('drop_off', 'Drop Off (Sucursal de correo)'),
    ('xd_drop_off', 'Cross Docking + Drop Off'),
    ('self_service', 'Self Service (Logística propia)'),
    ('not_specified', 'No especificado'),
    ], 
    default="not_specified",
    string="Tipo de Logística",
    required=True,
    help="""
    **fulfillment**: El producto está en los almacenes de Mercado Libre (Full). ML se encarga de almacenamiento, empaque, envío y postventa.
    **cross_docking**: El vendedor lleva la mercadería a una estación de Mercado Libre y desde ahí ML hace el despacho.
    **drop_off**: El vendedor despacha el producto en una sucursal de correo autorizado por ML.
    **xd_drop_off**: Variante mixta: drop off + cross docking.
    **self_service**: El vendedor organiza y paga su propia logística, sin integración con ML.
    **not_specified**: No se especifica ningún tipo de logística (por defecto).
    """
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

        # --- Cantidad según tipo logístico ---
        qty = 0
        if instance and product:
            if logistic_type == 'fulfillment':
                location = instance.ml_full_location_id
            else:
                location = instance.ml_not_full_location_id
            if location:
                quant = self.env['stock.quant'].search([
                    ('product_id', 'in', product.product_variant_ids.ids),
                    ('location_id', '=', location.id)
                ], limit=1)
                qty = quant.quantity if quant else 0
        res['meli_available_quantity'] = qty

        return res

    def _upload_picture_to_meli(self, url, access_token):
        upload_url = "https://api.mercadolibre.com/pictures/items/upload"
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            img_resp = requests.get(url, stream=True)
            if img_resp.status_code != 200:
                raise UserError(f"No se pudo descargar la imagen: {url}")

            content_type = img_resp.headers.get("Content-Type", "")
            if not any(t in content_type for t in ["jpeg", "jpg", "png", "gif", "webp"]):
                _logger.warning(f"Content-Type sospechoso ({content_type}) para {url}. Forzando image/jpeg")
                content_type = "image/jpeg"

            files = {"file": ("image.jpg", img_resp.content, content_type)}

            resp = requests.post(upload_url, headers=headers, files=files)
            if resp.status_code == 201:
                return resp.json()  # devuelve todo (id, secure_url, etc.)
            else:
                _logger.error(f"Error al subir imagen a ML [{resp.status_code}]: {resp.text}")
                raise UserError(f"Error al subir imagen a MercadoLibre: {resp.text}")

        except Exception as e:
            raise UserError(f"No se pudo subir la imagen {url}: {str(e)}")

    @api.onchange('meli_logistic_type', 'instance_id', 'product_id')
    def _onchange_meli_logistic_type(self):
        qty = 0
        instance = self.instance_id
        product = self.product_id
        if instance and product:
            if self.meli_logistic_type == 'fulfillment':
                location = instance.ml_full_location_id
            else:
                location = instance.ml_not_full_location_id
            if location:
                quant = self.env['stock.quant'].search([
                    ('product_id', 'in', product.product_variant_ids.ids),
                    ('location_id', '=', location.id)
                ], limit=1)
                qty = quant.quantity if quant else 0
        self.meli_available_quantity = qty


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

        # Imagen principal
        if self.meli_thumbnail:
            thumb_url = self.meli_thumbnail
            _logger.info(f"Procesando thumbnail: {thumb_url}")
            if "mlstatic.com" not in thumb_url:
                _logger.info("Thumbnail externo detectado. Subiendo a ML...")
                pic_data = self._upload_picture_to_meli(thumb_url, access_token)
                self.meli_thumbnail = pic_data.get("secure_url")
                self.product_id.meli_thumbnail = pic_data.get("secure_url")
                pictures.append({"id": pic_data.get("id")})
            else:
                pictures.append({"source": thumb_url})

        # Imágenes secundarias
        for img in self.meli_pictures_ids:
            img_url = img.secure_url or img.url
            if not img_url:
                continue
            if "mlstatic.com" not in img_url:
                _logger.info("Imagen externa detectada. Subiendo a ML...")
                pic_data = self._upload_picture_to_meli(img_url, access_token)
                img.write({"secure_url": pic_data.get("secure_url"), "url": pic_data.get("secure_url")})
                pictures.append({"id": pic_data.get("id")})
            else:
                pictures.append({"source": img_url})

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

        precio_base = self.meli_base_price
        tipo_comision = self.instance_id.type_of_commission
        valor_comision = self.instance_id.meli_commission

        if tipo_comision == 'fixed':
            precio_meli = precio_base+valor_comision
        elif tipo_comision == 'percentage':
            precio_meli = precio_base*(1+valor_comision/100)
        else:
            precio_meli = precio_base

        price = int(precio_meli) if self.meli_currency_id == 'CLP' else precio_meli
        _logger.info(f"Precio preparado para ML: {price}")

        # --- PAYLOAD ---
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

        return {'type': 'ir.actions.act_window_close'}

