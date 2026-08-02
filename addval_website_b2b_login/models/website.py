# -*- coding: utf-8 -*-
from odoo import fields, models


class Website(models.Model):
    _inherit = 'website'

    b2b_login_required = fields.Boolean(
        string='B2B: require login',
        help='If enabled, anonymous visitors are redirected to /web/login '
             'for every frontend page of this website (except login, signup, '
             'password reset, logout and static assets).',
        default=False,
    )
