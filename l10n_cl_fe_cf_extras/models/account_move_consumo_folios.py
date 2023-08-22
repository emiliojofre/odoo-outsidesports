# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime
import dateutil.relativedelta as relativedelta


class CFExtras(models.Model):
    _name = 'account.move.consumo_folios'
    _inherit = ['account.move.consumo_folios', 'mail.thread']

    @api.model
    def cron_procesar_autoenvio(self):
        fecha_inicio = datetime.now() + relativedelta.relativedelta(days=-1)
        cf = self.sudo().create({
                    'name': 'auto_%s' % fecha_inicio,
                    'fecha_inicio': fecha_inicio,
                    'fecha_final': fecha_inicio,
            })
        cf.set_data()
        cf.validar_consumo_folios()
        cf.do_dte_send_consumo_folios()
