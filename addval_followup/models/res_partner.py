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

        all_data = self._query_followup_data()
        for partner in self:
            
            partner_data = all_data.get(partner._origin.id, {'followup_status': 'no_action_needed', 'followup_line_id': False})
            partner.followup_status = partner_data['followup_status']
            
            unpaid_invoices_days = {}

            for unpaid_invoice in partner.unpaid_invoice_ids: 

                days_after_due = fields.Date.today() - unpaid_invoice.invoice_date_due

                unpaid_invoices_days[partner.id] = days_after_due.days

            if unpaid_invoices_days:
                max_days_overdue = max(unpaid_invoices_days.values())

                matching_followup_lines = self.env['account_followup.followup.line'].search([
                    ('delay', '<=', max_days_overdue),
                    ('company_id', '=', self.env.company.id)
                ], order="delay desc", limit=1)

                if matching_followup_lines:

                    partner.followup_line_id = matching_followup_lines.id
                else:
                    partner.followup_line_id = partner_data['followup_line_id']
            else:
                partner.followup_line_id = partner_data['followup_line_id']

    @api.model
    def _get_first_followup_level(self):
        return self.env['account_followup.followup.line'].search([('company_id', '=', self.env.company.id)], order='delay asc', limit=1)

    def _update_next_followup_action_date(self, followup_line):
        """Updates the followup_next_action_date of the right account move lines
        """
        self.ensure_one()

        # Arbitrary 1 days delay (like the _get_next_date() method) if there is no followup_line
        # This will be changed/removed in an upcoming improvement
        next_date =  fields.Date.today() + timedelta(days=1)
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
        previous_line_id = None
        followup_lines_info = {}
        for line in followup_lines:
            delay_in_days = line.delay

            followup_lines_info[previous_line_id] = {
                'next_followup_line_id': line.id,
                'next_delay': delay_in_days,
            }

            previous_line_id = line.id

        if previous_line_id:
            followup_lines_info[previous_line_id] = {
                'next_followup_line_id': previous_line_id,
                'next_delay': delay_in_days,
            }
        return followup_lines_info    
        
    def _execute_followup_partner(self, options=None):
        """ Execute the actions to do with follow-ups for this partner (apart from printing).
        This is either called when processing the follow-ups manually (wizard), or automatically (cron).
        Automatic follow-ups can also be triggered manually with *action_manually_process_automatic_followups*.
        When processing automatically, options is None.

        Returns True if any action was processed, False otherwise
        """
        self.ensure_one()
        if options is None:

            unpaid_invoices_days = {}

            for unpaid_invoice in self.unpaid_invoice_ids: 

                days_after_due = fields.Date.today() - unpaid_invoice.invoice_date_due

                unpaid_invoices_days[self.id] = days_after_due.days

            if unpaid_invoices_days:
                max_days_overdue = max(unpaid_invoices_days.values())

                matching_followup_lines = self.env['account_followup.followup.line'].search([
                    ('delay', '<=', max_days_overdue),
                    ('company_id', '=', self.env.company.id)
                ], order="delay desc", limit=1)

                if matching_followup_lines:

                    followup_line = matching_followup_lines
                else:
                    followup_line = self.followup_line_id or self._get_first_followup_level()
            else:
                followup_line = self.followup_line_id or self._get_first_followup_level()
            
            if followup_line.create_activity:
                # log a next activity for today
                self.activity_schedule(
                    activity_type_id=followup_line.activity_type_id and followup_line.activity_type_id.id or self._default_activity_type().id,
                    note=followup_line.activity_note,
                    summary=followup_line.activity_summary,
                    user_id=(self._get_followup_responsible()).id
                )

            self._update_next_followup_action_date(followup_line)
            self._send_followup(options={'followup_line': followup_line})

            return True
        
        if options.get('manual_followup', self.followup_status in ('in_need_of_action', 'with_overdue_invoices')):
            followup_line = self.followup_line_id or self._get_first_followup_level()

            if followup_line.create_activity:
                # log a next activity for today
                self.activity_schedule(
                    activity_type_id=followup_line.activity_type_id and followup_line.activity_type_id.id or self._default_activity_type().id,
                    note=followup_line.activity_note,
                    summary=followup_line.activity_summary,
                    user_id=(self._get_followup_responsible()).id
                )

            self._update_next_followup_action_date(followup_line)

            self._send_followup(options={'followup_line': followup_line, **options})

            return True
        return False

    def _cron_execute_followup_company(self):
        #followup_data = self._query_followup_data(all_partners=True)
        #in_need_of_action = self.env['res.partner'].browse([d['partner_id'] for d in followup_data.values() if d['followup_status'] == 'in_need_of_action' or d['followup_status'] == 'with_overdue_invoices'])
        #in_need_of_action_auto = in_need_of_action.filtered(lambda p: p.followup_line_id.auto_execute and p.followup_reminder_type == 'automatic')

        partner_need_of_action = self.env['res.partner'].search([('followup_status', 'in', ('in_need_of_action', 'with_overdue_invoices'))])
        _logger.warning('partner_need_of_action: %s', partner_need_of_action)
        partner_need_of_action_auto = partner_need_of_action.filtered(lambda p: p.followup_line_id.auto_execute and p.followup_reminder_type == 'automatic')
        _logger.warning('partner_need_of_action_auto: %s', partner_need_of_action_auto)
        for partner in partner_need_of_action_auto:
            try:
                _logger.warning('partner : %s', partner)
                _logger.warning('partner.followup_line_id : %s', partner.followup_line_id)
                partner._execute_followup_partner()
            except UserError as e:
                # followup may raise exception due to configuration issues
                # i.e. partner missing email
                _logger.warning(e, exc_info=True)