import requests
import base64
from odoo import models, fields, api
import logging


# Configurar el logger
_logger = logging.getLogger(__name__)

class VexMarketCompetition(models.Model):
    _name = 'vex.market_competition'
    _description = 'Mercado y Competencia'

    # name = fields.Char("Producto", required=True)
    image_product = fields.Binary(string='Imagen',store=True)  # Imagen
    mercado_id = fields.Char("ID en Mercado Libre")
    posicion = fields.Integer("Posición en el Ranking")
    tipo = fields.Selection([
        ('item', 'Ítem'),
        ('product', 'Producto')
    ], string="Tipo", default="item")
    categoria = fields.Char("Categoría")
    site_id = fields.Char("País")
    price = fields.Float("Precio")  
    title = fields.Char("Título")  
    mercado_libre_url = fields.Char(string="URL Mercado Libre")
    instance_id = fields.Many2one('vex.instance', string="Instancia")

    @api.model
    def consumir_api_mercado_libre(self):
        current_user = self.env.user 
        meli_instance = current_user.meli_instance_id

        if not meli_instance:
            _logger.warning("No se encontró instancia de MercadoLibre para el usuario actual.")
            return

        ACCESS_TOKEN = meli_instance.meli_access_token
        SITE_ID = meli_instance.meli_country

        # ✅ CORREGIDO: domain debe ser una lista de tuplas
        category_ids = self.env['vex.category'].search([('instance_id', '=', meli_instance.id)])

        for category in category_ids:
            CATEGORY_ID = category.codigo_ml

            url = f"https://api.mercadolibre.com/highlights/{SITE_ID}/category/{CATEGORY_ID}"
            headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

            try:
                response = requests.get(url, headers=headers)

                # Si el token está vencido
                if response.status_code == 401 and response.json().get('message') == 'invalid_token':
                    _logger.warning("Token vencido. Actualizando token...")
                    meli_instance.get_access_token()
                    ACCESS_TOKEN = meli_instance.meli_access_token
                    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
                    response = requests.get(url, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    _logger.info("Datos de Mercado Libre: %s", data)

                    site = {
                        'MLM': 'México',
                        'MLA': 'Argentina',
                        'MPE': 'Perú'
                    }.get(SITE_ID, '')

                    for item in data.get("content", []):
                        _logger.info("Item: %s", item)
                        obj = {
                            'mercado_id': item['id'],
                            'posicion': item['position'],
                            'tipo': item['type'].lower(),
                            'categoria': category.description,
                            'site_id': site,
                            'instance_id': meli_instance.id
                        }
                        new_register = self.env['vex.market_competition'].create(obj)
                        if new_register:
                            _logger.info("Se creó con éxito: %s", item['id'])
                        else:
                            _logger.info("No se pudo crear el registro: %s", item['id'])

                else:
                    _logger.error("Error %s: %s", response.status_code, response.text)

            except Exception as e:
                _logger.error("Error al consumir la API de Mercado Libre: %s", str(e))


    @api.model
    def consumir_api_buscador_de_productos(self):
        current_user = self.env.user 
        meli_instance = current_user.meli_instance_id
        
        ACCESS_TOKEN = meli_instance.meli_access_token
        #ACCESS_TOKEN = "APP_USR-2822929086258615-020718-9e3d709f839f91c2e7c71f953f82ea96-2205765982"
        STATUS_ID = "active"
        SITE_ID = meli_instance.meli_country  # Cambia según tu país

        product_ids = self.env['vex.market_competition'].search([('tipo','=', 'product'),('instance_id','=', meli_instance.id)])

        for product in product_ids:
            # Obtener el valor del campo mercado_id directamente
            PRODUCT_IDENTIFIER = product.mercado_id 

            url = f"https://api.mercadolibre.com/products/search?status={STATUS_ID}&site_id={SITE_ID}&product_identifier={PRODUCT_IDENTIFIER}"
            headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

            response = requests.get(url, headers=headers)

            # Si el token está vencido
            if response.status_code == 401 and response.json().get('message') == 'invalid_token':
                _logger.warning("Token vencido. Actualizando token...")
                meli_instance.get_access_token()
                # Usamos el nuevo token
                ACCESS_TOKEN = meli_instance.meli_access_token
                headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
                response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                # print(data)
                # print(data["results"])
                for item in data["results"]:
                    print("===================================================================================")
                    obj = {
                        'title': item['name']
                    }

                    write_register = product.write(obj)
                    if write_register:
                        _logger.info("Producto actualizado con éxito: %s", item['name'])
                    else:
                        _logger.info("No se pudo actualizar el registro: %s", item['name'])
                    
            else:
                print(f"Error {response.status_code}: {response.text}")

    @api.model
    def consumir_api_detail_items(self):
        current_user = self.env.user 
        meli_instance = current_user.meli_instance_id
        
        ACCESS_TOKEN = meli_instance.meli_access_token
        #ACCESS_TOKEN = "APP_USR-2822929086258615-020718-9e3d709f839f91c2e7c71f953f82ea96-2205765982"

        product_ids = self.env['vex.market_competition'].search([('instance_id','=', meli_instance.id)])
    
        for product in product_ids:

            if product.tipo == 'item':

                # Obtener el valor del campo mercado_id directamente
                ITEM_ID = product.mercado_id 

                url = f"https://api.mercadolibre.com/items/{ITEM_ID}"
            
                headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

                response = requests.get(url, headers=headers)

                # Si el token está vencido
                if response.status_code == 401 and response.json().get('message') == 'invalid_token':
                    _logger.warning("Token vencido. Actualizando token...")
                    meli_instance.get_access_token()
                    # Usamos el nuevo token
                    ACCESS_TOKEN = meli_instance.meli_access_token
                    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
                    response = requests.get(url, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    print(data['price'])
                    imagen_url = data['thumbnail'] if data else False
                    image_response = requests.get(imagen_url) if imagen_url else False
                    image_product = base64.b64encode(image_response.content).decode('utf-8') if image_response else False    
                    obj = {
                        'price': data['price'],
                        'title': data['title'],
                        'mercado_libre_url': data['permalink'],
                        'image_product': image_product
                    }
                    write_register = product.write(obj)
                    if write_register:
                        _logger.info("Producto actualizado con éxito: %s", data['id'])
                    else:
                        _logger.info("No se pudo actualizar el registro: %s", data['id'])
                else:
                    print(f"Error {response.status_code}: {response.text}")

            elif product.tipo  == 'product':
                # Obtener el valor del campo mercado_id directamente
                PRODUCT_ID = product.mercado_id 

                url = f"https://api.mercadolibre.com/products/{PRODUCT_ID}"

                headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

                response = requests.get(url, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    imagen_url = data['pickers'][0]['products'][0]['thumbnail'] if data['pickers'] else False
                    image_response = requests.get(imagen_url) if imagen_url else False
                    image_product = base64.b64encode(image_response.content).decode('utf-8') if image_response else False
                    obj = {
                        'title': data['name'],
                        'price': data['buy_box_winner']['price'],
                        'image_product': image_product,
                        'mercado_libre_url': data['permalink']
                    }
                    write_register = product.write(obj)
                    if write_register:
                        _logger.info("Producto actualizado con éxito: %s", data['id'])
                    else:
                        _logger.info("No se pudo actualizar el registro: %s", data['id'])
                else:
                    print(f"Error {response.status_code}: {response.text}")