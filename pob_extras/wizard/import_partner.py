# -*- coding: utf-8 -*-
from xmlrpc.client import Error
import logging
from odoo import api, fields, models, _
from odoo.addons.prestashop_odoo_bridge.models.prestapi import PrestaShopWebService,PrestaShopWebServiceDict,PrestaShopWebServiceError,PrestaShopAuthenticationError
_logger = logging.getLogger(__name__)
import itertools

CHANNELDOMAIN = [
    ('channel', '=', 'prestashop'),
    ('state', '=', 'validate')
]


def split_seq(iterable, size):
    it = iter(iterable)
    item = list(itertools.islice(it, size))
    while item:
        yield item
        item = list(itertools.islice(it, size))

customerInfoFields = [
]
Boolean = [

    ('all', 'True/False'),
    ('1', 'True'),
    ('0', 'False'),
]
Source = [
    ('all', 'All'),
    ('partner_ids', 'Partner ID(s)'),
]


class ImportPrestashoppartners(models.TransientModel):
    _inherit = ['import.prestashop.partners']
    
    def _fetch_prestashop_partners(self, prestashop):
        message = ''
        data = None
        customer_list = []
        li_customer_ids = []
        customer_ids = []
        channel_id = self.channel_id
        date_add = channel_id.import_customer_date
        if date_add:
            try:
                data = prestashop.get('customers', options={'display':'[id, firstname, lastname, email, deleted, siret]', 'filter[date_add]':'>['+date_add+']', 'date':1, 'filter[deleted]':0})
            except Exception as e:
                message += '<br/>For Customer %s<br/>%s'%(data, str(e))
                _logger.info('_______________ Error: %r _____________', message)
            if data:
                if data['customers']=='':
                    return dict(
                        data = [],
                        message = message+ 'No customer had been registered after created after  %s. Please select a different date to import. \n'%(date_add)
                    )
                if type(data['customers']['customer'])==list:
                    for i in data['customers']['customer']:
                            customer_list.append(i)
                    li_customer_ids = list(split_seq(customer_list, 100))
                else:
                    customer_list.append(data['customers']['customer'])
                    li_customer_ids = list(split_seq(customer_list, 100))
            return dict(
                data = li_customer_ids,
                message = message
            )
        return dict(
            data = li_customer_ids,
            message = "Import date not set. "
        )        
         
    def get_customer_vals(self, prestashop, customer_id, customer_data):
        vals = super(ImportPrestashoppartners,self).get_customer_vals(prestashop, customer_id, customer_data)
        if 'siret' in customer_data and customer_data.get('siret'):
            vals['document_number'] = customer_data.get('siret')         
        return vals
    
    
    #FIXME: Revsion 2da estapa. Para validar que no se repitan los siret
    """
    def _prestashop_import_customer(self, prestashop, customer_id, data):
        feed_obj = self.env['partner.feed']
        siret = data['siret']
        match = self.channel_id._match_feed(
            feed_obj, [('store_id', '=', customer_id),('type', '=', 'contact'),('document_number','=',siret)])
        update = False
        if match:
            if self.channel_id.update_feed:
                self._prestashop_update_customer_feed( prestashop, match, customer_id, data)
            update = True
        else:
            match = self._prestashop_create_customer_feed(prestashop, customer_id, data)
        return dict(
            feed_id = match,
            update = update
        )    
        """
