# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def get_description_name(self, product):
        name = product.name
        if product.attribute_value_ids:
            str_name = " ("
            for n in product.attribute_value_ids.mapped('name'):
                str_name += "{0},".format((n))
            str_name = str_name[:-1]
            str_name += ")"
            name += str_name

        return name


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def get_description_name(self, product):
        name = product.name
        if product.attribute_value_ids:
            str_name = " ("
            for n in product.attribute_value_ids.mapped('name'):
                str_name += "{0},".format((n))
            str_name = str_name[:-1]
            str_name += ")"
            name += str_name

        return name


class product_description(models.Model):
    _inherit = 'sale.order.line'

    name = fields.Text(
        string='Description',
        compute='_compute_get_description', store=True, readonly=False,
        required=True)

    @api.multi
    @api.depends('product_id')
    def _compute_get_description(self):
        for record in self:
            name = record.product_id.name
            if record.product_id.attribute_value_ids:
                str_name = " ("
                for n in record.product_id.attribute_value_ids.mapped('name'):
                    str_name += "{0},".format((n))
                str_name = str_name[:-1]
                str_name += ")"
                name += str_name

            record.name = name

    @api.constrains('product_id')
    def _check_get_description(self):
        if self.product_id:
            name = self.product_id.name
            if self.product_id.attribute_value_ids:
                str_name = " ("
                for n in self.product_id.attribute_value_ids.mapped('name'):
                    str_name += "{0},".format((n))
                str_name = str_name[:-1]
                str_name += ")"
                name += str_name

            self.update({"name": name})

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        result = super(product_description, self).product_id_change()

        if self.product_id:
            name = self.product_id.name
            if self.product_id.attribute_value_ids:
                str_name = " ("
                for n in self.product_id.attribute_value_ids.mapped('name'):
                    str_name += "{0},".format((n))
                str_name = str_name[:-1]
                str_name += ")"
                name += str_name

            self.name = name
            self.update({'name': name})

        return result
