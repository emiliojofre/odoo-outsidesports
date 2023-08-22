# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.addons.http_routing.models.ir_http import slugify
from odoo.http import request
import datetime
import math


class website(models.Model):
	"""Adds the fields for Breadcrumb."""
	
	_inherit = 'website'
	
	bread_cum_image = fields.Binary(string="Breadcrumb Image")
	is_breadcum = fields.Boolean(string="Do you want to disable Breadcrumb?")
	
	@api.model
	def get_category_breadcum(self, category):
		data = []
		parent_categ = False
		if category:
			categ_data = self.env['product.public.category'].search([('id', '=', int(category))])
			data.append(categ_data)
			parent_categ = categ_data
			if categ_data and categ_data.parent_id:
				parent_categ = categ_data.parent_id
				data.append(parent_categ)
				while parent_categ.parent_id:
					parent_categ = parent_categ.parent_id
					data.append(parent_categ)
			data.reverse()
		return data
	
	@api.model
	def new_page(self, name=False, add_menu=False, template='website.default_page', ispage=True, namespace=None):
		res = super(website, self).new_page(name, add_menu, template, ispage=True, namespace=namespace)
		if ispage:
			arch = "<?xml version='1.0'?><t t-name='website." + str(name) + "'><t t-call='website.layout'> \
                    <div id='wrap' class='oe_structure oe_empty'>"
			
			arch = arch + '<t t-if="not website.is_breadcum">'
			
			arch = arch + '<t t-if="not website.bread_cum_image">' \
			              '<nav class="is-breadcrumb shop-breadcrumb" role="navigation" aria-label="breadcrumbs">' \
			              '<div class="container">' \
			              '<h1><span>' + str(name) + '</span></h1>' \
			                                         '<ul class="breadcrumb">' \
			                                         '<li><a href="/page/homepage">Home</a></li>' \
			                                         '<li class="active"><span>' + str(name) + '</span></li>' \
			                                                                                   '</ul>' \
			                                                                                   '</div>' \
			                                                                                   '</nav>' \
			                                                                                   '</t>'
			arch = arch + '<t t-if="website.bread_cum_image">' \
			              '<t t-set="bread_cum" t-value="website.image_url(website,' + repr('bread_cum_image') + ')"/>' \
			                                                                                                     '<nav class="is-breadcrumb shop-breadcrumb" role="navigation" aria-label="breadcrumbs" t-attf-style="background-image:url(#{bread_cum}#)">' \
			                                                                                                     '<div class="container">' \
			                                                                                                     '<h1><span>' + str(
				name) + '</span></h1>' \
			            '<ul class="breadcrumb">' \
			            '<li><a href="/page/homepage">Home</a></li>' \
			            '<li class="active"><span>' + str(name) + '</span></li>' \
			                                                      '</ul>' \
			                                                      '</div>' \
			                                                      '</nav>' \
			                                                      '</t>'
			arch = arch + '</t>'
			arch = arch + '</div><div class="oe_structure"/></t></t>'
			view_id = res['view_id']
			view = self.env['ir.ui.view'].browse(int(view_id))
			view.write({'arch': arch})
		return res


class WebsiteConfigSettings(models.TransientModel):
	"""Settings for the Breadcrumb."""
	
	_inherit = 'res.config.settings'
	
	bread_cum_image = fields.Binary(
		related='website_id.bread_cum_image',
		string='Breadcrumb Image',
	)
	is_breadcum = fields.Boolean(string="Do you want to disable Breadcrumb?", related='website_id.is_breadcum')


class ProductTemplate(models.Model):
	_inherit = 'product.template'
	
	hover_image = fields.Binary("Hover Image")
	
	def _calculate_rating(self, product_id):
		records = self.env["product.template"].sudo().search([('id', '=', product_id)])
		domain = [('res_model', '=', "product.template"), ('res_id', 'in', records.ids), ('consumed', '=', True)]
		ratings = self.env['rating.rating'].search(domain, order="id desc", limit=100)
		domdate = domain
		rating_stats = self.env['rating.rating'].read_group(domdate, [], ['rating'])
		total = sum(st['rating_count'] for st in rating_stats)
		total_rating = sum(st['rating'] * st['rating_count'] for st in rating_stats)
		if total:
			return ((total_rating) / total)
		else:
			return 0
	
	@api.model
	def get_product_pvp(self):
		quantity = self._context.get('quantity') or 1
		rate = request.env['product.pricelist'].search([('selectable', '=', True)])
		to_currency = request.website.get_current_pricelist().currency_id
		attribute_value_ids = []
		
		# attribute_line_ids.sorted(key=lambda x: x.attribute_id.sequence)
		variant_ids = self.product_variant_ids.sorted(lambda r: r.attribute_value_ids.mapped('id'))
		for variant in variant_ids:
			price_item = rate.item_ids.filtered(
				lambda item: item.product_id.id == variant.id and item.compute_price == 'fixed')
			price_pvp = request.env['report.product.report_pricelist']._get_price(rate, variant, 1)
			
			if to_currency != self.currency_id:
				price = variant.currency_id.compute(variant.website_price, to_currency) / quantity
				price_pvp = variant.currency_id.compute(price_pvp, to_currency)
			else:
				price = variant.website_price / quantity
			
			if price_item:
				price_pvp *= 1.19
			
			attribute_value_ids.append([variant.id, variant.default_code, price, price_pvp])
		return attribute_value_ids[0]
	
	@api.model
	def get_average_rating(self):
		for data in self:
			avg_rate = self._calculate_rating(self.id)
			if avg_rate > 0:
				val_integer = math.floor(avg_rate)
				val_decimal = avg_rate - val_integer
				val_ext = 5 - (val_integer + math.ceil(val_decimal))
				data = {'val': avg_rate, 'val_integer': val_integer, 'val_decimal': val_decimal,
				        'empty_star': val_ext, }
			else:
				data = {'val': 0, 'val_integer': 0, 'val_decimal': 0, 'empty_star': 5}
			return data
