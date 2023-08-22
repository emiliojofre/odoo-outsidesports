# -*- coding: utf-8 -*-
import copy
from odoo import fields, models, api, _
from odoo.exceptions import RedirectWarning, ValidationError  ,Warning
from odoo.addons.odoo_multi_channel_sale.tools import parse_float, extract_list as EL
import logging

Fields = [
    'name',
    'store_id',
    'store_source',
]
PartnerFields = Fields + [
    'email',
    'phone',
    'mobile',
    'website',
    'last_name',
    'street',
    'street2',
    'city',
    'zip',
    'state_id',
    'state_name',
    'country_id',
    'type',
    'parent_id',
    'document_number',
]
OrderFields = Fields + [
    'partner_id',
    'order_state',
    'carrier_id',

    'date_invoice',
    # 'min_date',
    'date_order',
    'confirmation_date',

    'line_ids',
    'line_name',
    'line_price_unit',
    'line_product_id',
    'line_product_default_code',
    'line_product_barcode',
    'line_variant_ids',
    'line_source',
    'line_product_uom_qty',
    'line_taxes',
]

LineType = [
    ('single', 'Single Order Line'),
    ('multi', 'Multi Order Line')
]
LineSource = [
    ('product','Product'),
    ('delivery','Delivery'),
    ('discount','Discount'),
]
PartnerType = [
    ('contact','Contact'),
    ('invoice','Invoice'),
    ('delivery','Delivery'),
]

class PartnerFeed(models.Model):

    _inherit = "partner.feed"
    
    document_number = fields.Char(
        string='Document number',
        size=64,
    )
    
    def import_partner(self,channel_id):

        
        message = ""
        state = 'done'
        update_id = None
        create_id=None
        self.ensure_one()
        vals = EL(self.read(PartnerFields))
        _type =vals.get('type')
        store_id = vals.pop('store_id')
        vals.pop('website_message_ids','')
        vals.pop('message_follower_ids','')
        match = channel_id.match_partner_mappings(store_id,_type)
        name = vals.pop('name')
        if not name:
            message+="<br/>Partner without name can't evaluated."
            state = 'error'
        if not store_id:
            message+="<br/>Partner without store id can't evaluated."
            state = 'error'
        parent_store_id = vals['parent_id']
        if parent_store_id:
            partner_res = self.get_partner_id(parent_store_id,channel_id=channel_id)
            message += partner_res.get('message')
            partner_id = partner_res.get('partner_id')
            if partner_id:
                vals['parent_id'] =partner_id.id
            else:
                state = 'error'
        if state == 'done':
            country_id = vals.pop('country_id')
            if country_id:
                country_id = channel_id.get_country_id(country_id)
                if country_id:
                    vals['country_id'] = country_id.id
            state_id = vals.pop('state_id')
            state_name = vals.pop('state_name')

            if (state_id or state_name) and country_id:
                state_id = channel_id.get_state_id(state_id,country_id,state_name)
                if state_id:
                    vals['state_id'] = state_id.id
            last_name = vals.pop('last_name','')
            if last_name:
                vals['name'] = "%s %s" % (name, last_name)
            else:
                vals['name'] =name
        if match:
            if  state =='done' :
                try:
                    match.odoo_partner.write(vals)
                    message +='<br/> Partner %s successfully updated'%(name)
                except Exception as e:
                    message += '<br/>%s' % (e)
                    state = 'error'
                update_id = match

            elif state =='error':
                message+='Error while partner updated.'

        else:
            if state == 'done':
                try:
                    erp_id = self.env['res.partner'].create(vals)
                    create_id =  channel_id.create_partner_mapping(erp_id, store_id,_type)
                    message += '<br/>Partner %s successfully evaluated.'%(name)
                except Exception as e:
                    message += '<br/>%s' % (e)
                    state = 'error'
        self.set_feed_state(state=state)
        self.message = "%s <br/> %s" % (self.message, message)
        return dict(
            create_id=create_id,
            update_id=update_id,
            message=message
        )    