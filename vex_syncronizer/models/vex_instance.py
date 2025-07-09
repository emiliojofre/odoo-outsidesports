from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging
import json
import requests
# Configura el logger
_logger = logging.getLogger(__name__)

class VexInstace(models.Model):
    _name = 'vex.instance'
    _rec_name = 'name'
    _description = 'Vex Instance'

    name = fields.Char('Name', required=True)

    status = fields.Selection([
        ('introduction', 'INTRODUCTION'),
        ('initial_settings', 'INITIAL SETTINGS'),
        ('keys', 'KEYS'),
        ('settings', 'SETTINGS')
    ], string='Status', default="introduction")
    image = fields.Image('Image') # , max_width=30, max_height=30
    url_license = fields.Char(default='https://www.pasarelasdepagos.com/')
    license_secret_key = fields.Char(default='587423b988e403.69821411')
    license_key = fields.Char(string='Licence Key', help='Licence Key by Pasarela de pagos', default='')
    license_valid_str = fields.Char(string="License Status", store=True, readonly=True)
    license_valid = fields.Selection([
        ('activo', 'Active'),
        ('inactivo', 'Inactive')
    ], string="License Status")

    license_date_created = fields.Char(string='Licence Date Created', default='', readonly=True)
    license_renewed = fields.Char(string='Licence Date Renovad', default='', readonly=True)
    license_expiry = fields.Char(string='Licence Date Expiry', default='', readonly=True)
    license_message = fields.Char(string='Licence Message', default='', readonly=True)
    store_type = fields.Selection([
    ], string="Store Type", required=True)
    registered_domain = fields.Char('Registered domain', default=lambda self: self.env['ir.config_parameter'].sudo().get_param('web.base.url'))

    state_filter = fields.Selection([
        ('all', 'All'),
        ('error', 'Error'),
        ('obs', 'Observation'),
        ('done', 'Done'),
        ('pending', 'Pending'),
    ], string="Filter by Status", default='all')
    filtered_import_line_ids = fields.One2many('vex.import_line', string="Filtered Import Lines", compute="_compute_filtered_lines", store=False)
    import_line_ids = fields.One2many('vex.import_line', 'instance_id', string='import_line')
    sync_queue_ids = fields.One2many('vex.sync.queue', 'instance_id', string='Sync Queue')
    def check_licence(self):
        for provider in self:
            if provider.license_key:
                domain = self.env['ir.config_parameter'].sudo().get_param('web.base.url')\
                    .replace('http://', '').replace('https://', '')

                key = provider.license_key
                secret = provider.license_secret_key

                url = f"https://www.pasarelasdepagos.com/?slm_action=slm_check&license_key={key}&secret_key={secret}"

                headers = {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }

                self._log([domain, url, json.dumps(headers)], 'info')

                try:
                    response = requests.get(url, headers=headers, timeout=15)
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('result') == 'success':
                            return True
                        else:
                            _logger.warning(f"Check licence failed: {data.get('message')}")
                            return False
                    else:
                        _logger.error(f"HTTP error during licence check: {response.status_code}")
                        return False
                except Exception as e:
                    _logger.exception(f"Exception during licence check: {e}")
                    return False

        return False

    def test_connection(self):
        self.check_licence()

    def stop_sync(self):
        # cron = self.env['ir.cron'].search([('argument', '=', 'vex_cron'),"|",("active", "=", True), ("active", "=", False)])
        # if cron:
        #     cron.active = False
        pass

    def start_sync(self):
        # print("start_sync")
        self.env['vex.synchro'].sync_import()        

    @api.depends('state_filter', 'import_line_ids.status')
    def _compute_filtered_lines(self):
        for rec in self:
            if rec.state_filter == 'all':
                rec.filtered_import_line_ids = rec.import_line_ids
            else:
                rec.filtered_import_line_ids = rec.import_line_ids.filtered(
                    lambda l: l.status == rec.state_filter
                )
    
    def action_start_sync(self):
        pass