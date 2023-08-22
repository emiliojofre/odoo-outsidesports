# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from datetime import datetime


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    cf_hour = fields.Char(
            string="Auto Envío Consumo de Folios",
            default="01:00:00",
        )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        cf_autosend = ICPSudo.get_param(
                    'cf_extras.cf_autosend', '01:00:00')
        res.update(
                cf_autosend=cf_autosend,
            )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param('cf_extras.auto_send',
                          self.cf_autosend)
        cron_cf = self.env.ref('l10n_cl_fe_cf_extras.ir_cron_cf_autosend')
        next_call = datetime.strptime(cron_cf.nextcall.strftime("%Y-%m-%d ") + self.cf_hour, DTF)
        cron_cf.nextcall = next_call
        cron_cf.numbercall = -1
        cron_cf.interval_number = 1
        cron_cf.type = "days"
