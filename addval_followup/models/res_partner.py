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