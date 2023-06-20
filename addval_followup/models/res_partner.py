# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import api, fields, models, _
from odoo.tools.misc import format_date
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.depends('unreconciled_aml_ids', 'followup_next_action_date')
    @api.depends_context('company', 'allowed_company_ids')
    def _compute_followup_status(self):
        _logger.warning('ENTRO AL COMPUTE FOLLOWUP STATUS')
        all_data = self._query_followup_data()
        for partner in self:
            partner_data = all_data.get(partner._origin.id, {'followup_status': 'no_action_needed', 'followup_line_id': False})
            partner.followup_status = partner_data['followup_status']

            most_overdue_invoice = self.unpaid_invoices_ids.sorted(key=lambda inv: inv.due_date - fields.Date.today(), reverse=True)
            _logger.warning('ENTRO AL FOR Y  MUESTRA EL MOST_OVERDUE_INVOICE')
            _logger.warning(most_overdue_invoice)

            if most_overdue_invoice:
                _logger.warning('ENTRO AL IF MOST_OVERDUE_INVOICE')

                days_overdue = (fields.Date.today() - most_overdue_invoice.due_date).days

                matching_followup_lines = self.env['account_followup.followup.line'].search([
                    ('delay', '<=', days_overdue),
                    ('company_id', '=', self.company_id.id)
                ], order="delay desc", limit=1)
                _logger.warning('MATCHING_FOLLOWUP_LINES')
                _logger.warning(matching_followup_lines)
                if matching_followup_lines:
                    _logger.warning('ENCONTRO UN MATCHING_FOLLOWUP_LINES')
                    partner.followup_line_id = matching_followup_lines
                else:
                    partner.followup_line_id = partner_data['followup_line_id']

    @api.model
    def _get_first_followup_level(self):
        most_overdue_invoice = self.unpaid_invoices_ids.sorted(key=lambda inv: inv.due_date - fields.Date.today(), reverse=True)
        if most_overdue_invoice:
            days_overdue = (fields.Date.today() - most_overdue_invoice.due_date).days

            matching_followup_lines = self.env['account_followup.followup.line'].search([
                ('delay', '<=', days_overdue),
                ('company_id', '=', self.company_id.id)
            ], order="delay desc", limit=1)

            if matching_followup_lines:
                return matching_followup_lines
            
        return self.env['account_followup.followup.line'].search([('company_id', '=', self.env.company.id)], order='delay asc', limit=1)

    def _update_next_followup_action_date(self, followup_line):
        """Updates the followup_next_action_date of the right account move lines
        """
        self.ensure_one()

        # Arbitrary 1 days delay (like the _get_next_date() method) if there is no followup_line
        # This will be changed/removed in an upcoming improvement
        next_date = followup_line._get_next_date() if followup_line else fields.Date.today() + timedelta(days=1)
        self.followup_next_action_date = datetime.strftime(next_date, DEFAULT_SERVER_DATE_FORMAT)
        msg = _('Next Reminder Date set to %s', format_date(self.env, self.followup_next_action_date))
        self.message_post(body=msg)

        today = fields.Date.today()
        for aml in self._get_included_unreconciled_aml_ids():
            aml.followup_line_id = followup_line
            aml.last_followup_date = today

    def _get_followup_lines_info(self):
        """ returns the followup plan of the current user's company
        in the form of a dictionary with
         * keys being the different possible lines of followup for account.move.line's (None or IDs of account_followup.followup.line)
         * values being a dict of 3 elements:
           - 'next_followup_line_id': the followup ID of the next followup line
           - 'next_delay': the delay in days of the next followup line
        """
        followup_lines = self.env['account_followup.followup.line'].search([('company_id', '=', self.env.company.id)], order="delay asc")
        _logger.warning('ENTRO A LA FUNCION GET_FOLLOWUP_LINES_INFO Y MUESTRA FOLLOWUP_LINES')
        _logger.warning(followup_lines)
        previous_line_id = None
        followup_lines_info = {}
        for line in followup_lines:
            delay_in_days = line.delay

            _logger.warning('VARIABLE DELAY_IN_DAYS')
            _logger.warning(delay_in_days)

            followup_lines_info[previous_line_id] = {
                'next_followup_line_id': line.id,
                'next_delay': delay_in_days,
            }

            _logger.warning('DICCIONARIO FOLLOWUP_LINES_INFO[PREVIOUS_LINE_ID]')
            _logger.warning(followup_lines_info[previous_line_id])

            previous_line_id = line.id

            _logger.warning('VARIABLE PREVIOUS_LINE_ID')
            _logger.warning(previous_line_id)

        if previous_line_id:
            followup_lines_info[previous_line_id] = {
                'next_followup_line_id': previous_line_id,
                'next_delay': delay_in_days,
            }
            _logger.warning('DICCIONARIO FOLLOWUP_LINES_INFO[PREVIOUS_LINE_ID] DENTRO IF')
            _logger.warning(followup_lines_info[previous_line_id])
        
        _logger.warning('DICCIONARIO FOLLOWUP_LINES_INFO QUE RETORNA LA FUNCION')
        _logger.warning(followup_lines_info)

        return followup_lines_info
