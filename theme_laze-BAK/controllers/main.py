# -*- coding: utf-8 -*-

from odoo import http, SUPERUSER_ID
from odoo.http import request
import time
from odoo.addons.http_routing.models.ir_http import slug
from odoo.tools.translate import _
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers.main import TableCompute
from odoo.addons.website_sale.controllers.main import QueryURL
from odoo.addons.website_sale.controllers import main

main.PPG = 18
PPG = main.PPG


class WebsiteSale(WebsiteSale):
	
	@http.route(
		['/page/product_brands'],
		type='http',
		auth='public',
		website=True)
	def product_brands(self, **post):
		cr, context, pool = (request.cr,
		                     request.context,
		                     request.registry)
		b_obj = request.env['product.brand']
		domain = []
		if post.get('search'):
			domain += [('name', 'ilike', post.get('search'))]
		brand_ids = b_obj.search(domain)
		
		keep = QueryURL('/page/product_brands', brand_id=[])
		values = {'brand_rec': brand_ids,
		          'keep': keep}
		if post.get('search'):
			values.update({'search': post.get('search')})
		return request.render(
			'theme_laze.product_brands',
			values)
	
	@http.route()
	def shop(self, page=0, category=None, search='', ppg=False, **post):
		res = super(WebsiteSale, self).shop(page, category, search, ppg, **post)
		if post.get('brand'):
			if ppg:
				try:
					ppg = int(ppg)
				except ValueError:
					ppg = PPG
				post["ppg"] = ppg
			else:
				ppg = PPG
			
			attrib_list = request.httprequest.args.getlist('attrib')
			attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
			attributes_ids = {v[0] for v in attrib_values}
			attrib_set = {v[1] for v in attrib_values}
			domain = self._get_search_domain(search, category, attrib_values)
			product_designer_obj = request.env['product.brand']
			brand_ids = product_designer_obj.search([('id', '=', int(post.get('brand')))])
			
			if brand_ids:
				domain += [('product_brand_id', 'in', brand_ids.ids)]
			
			keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list,
			                order=post.get('order'))
			
			pricelist_context = dict(request.env.context)
			
			if not pricelist_context.get('pricelist'):
				pricelist = request.website.get_current_pricelist()
				pricelist_context['pricelist'] = pricelist.id
			else:
				pricelist = request.env['product.pricelist'].browse(pricelist_context['pricelist'])
			
			request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)
			url = "/shop"
			if search:
				post["search"] = search
			if category:
				category = request.env['product.public.category'].browse(int(category))
				url = "/shop/category/%s" % slug(category)
			if attrib_list:
				post['attrib'] = attrib_list
			
			categs = request.env['product.public.category'].search([('parent_id', '=', False)])
			Product = request.env['product.template']
			parent_category_ids = []
			if category:
				parent_category_ids = [category.id]
				current_category = category
				while current_category.parent_id:
					parent_category_ids.append(current_category.parent_id.id)
					current_category = current_category.parent_id
			
			product_count = Product.search_count(domain)
			pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
			products = Product.search(domain, limit=ppg, offset=pager['offset'], order=self._get_search_order(post))
			ProductAttribute = request.env['product.attribute']
			if products:
				attributes = ProductAttribute.search([('attribute_line_ids.product_tmpl_id', 'in', products.ids)])
			else:
				attributes = ProductAttribute.browse(attributes_ids)
			
			from_currency = request.env.user.company_id.currency_id
			to_currency = pricelist.currency_id
			compute_currency = lambda price: from_currency.compute(price, to_currency)
			res.qcontext.update({
				'category': category,
				'attrib_values': attrib_values,
				'attrib_set': attrib_set,
				'pager': pager,
				'products': products,
				'search_count': product_count,  # common for all searchbox
				'bins': TableCompute().process(products, ppg),
				'categories': categs,
				'attributes': attributes,
				'compute_currency': compute_currency,
				'keep': keep,
				'parent_category_ids': parent_category_ids,
			})
		else:
			return res
		return res
	
	@http.route(['/shop/cart/clean_cart'], type='json', auth="public", website=True)
	def clean_cart(self, type_id=None):
		order = request.website.sale_get_order()
		request.website.sale_reset()
		if order:
			order.sudo().unlink();
		return {}
	
	@http.route(['/shop/product/update_cart_popup'], type='http', auth="public", website=True)
	def update_cart_popup(self):
		order = request.website.sale_get_order()
		return request.render("theme_laze.product_cart", {'website': request.website})
	
	def get_attribute_value_ids(self, product):
		""" list of selectable attributes of a product

		:return: list of product variant description
		   (variant id, [visible attribute ids], variant price, variant sale price)
		"""
		# product attributes with at least two choices
		quantity = product._context.get('quantity') or 1
		product = product.with_context(quantity=quantity)
		
		visible_attrs_ids = product.attribute_line_ids.filtered(lambda l: len(l.value_ids) > 1).mapped(
			'attribute_id').ids
		to_currency = request.website.get_current_pricelist().currency_id
		rate = request.env['product.pricelist'].search([('selectable', '=', True)])
		attribute_value_ids = []
		for variant in product.product_variant_ids:
			
			price_item = rate.item_ids.filtered(
				lambda item: item.product_id.id == variant.id and item.compute_price == 'fixed')
			price_pvp = request.env['report.product.report_pricelist']._get_price(rate, variant, 1)
			
			if to_currency != product.currency_id:
				price = variant.currency_id.compute(variant.website_public_price, to_currency) / quantity
				price_pvp = variant.currency_id.compute(price_pvp, to_currency)
			else:
				price = variant.website_public_price / quantity
			
			# Nuevo requerimiento pvp * 19%
			price_pvp *= 1.19
			
			# if price_item:
			# 	price_pvp *= 1.19
			#
			visible_attribute_ids = [v.id for v in variant.attribute_value_ids if
			                         v.attribute_id.id in visible_attrs_ids]
			attribute_value_ids.append(
				[variant.id, visible_attribute_ids, variant.website_price / quantity, price, variant.default_code,
				 price_pvp, variant.qty_available, variant.virtual_available])
		return attribute_value_ids
