# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import io
import os
import time
import unicodedata
import uuid

from PyPDF2 import PdfFileReader, PdfFileWriter
try:
    from PyPDF2.errors import PdfReadError
except ImportError:
    from PyPDF2.utils import PdfReadError
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.rl_config import TTFSearchPath
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase.pdfmetrics import stringWidth
from werkzeug.urls import url_join, url_quote
from random import randint
from markupsafe import Markup
from hashlib import sha256
from PIL import UnidentifiedImageError

from odoo import api, fields, models, http, _, Command
from odoo.tools import config, email_normalize, get_lang, is_html_empty, format_date, formataddr, groupby
from odoo.exceptions import UserError, ValidationError

class SignRequestItem(models.Model):
    _inherit = "sign.request.item"


    def _send_signature_access_mail(self):
        for signer in self:
            signer_email_normalized = email_normalize(signer.signer_email or '')
            signer_lang = get_lang(self.env, lang_code=signer.partner_id.lang).code
            context = {'lang': signer_lang}
            # body = self.env['ir.qweb']._render('addval_sign_extension.request_to_sign_template', {
            #     'record': signer,
            #     'link': url_join(signer.get_base_url(), "sign/document/mail/%(request_id)s/%(access_token)s" % {'request_id': signer.sign_request_id.id, 'access_token': signer.sudo().access_token}),
            #     'subject': signer.sign_request_id.subject,
            #     'body': signer.sign_request_id.message if not is_html_empty(signer.sign_request_id.message) else False,
            #     'use_sign_terms': self.env['ir.config_parameter'].sudo().get_param('sign.use_sign_terms'),
            #     'user_signature': signer.create_uid.signature,
            # }, lang=signer_lang, minimal_qcontext=True)
            template = self.env.ref('addval_sign_extension.request_to_sign_template')
            rendered_template = template._render_template(template.body_html, 'sign.request.item', self.ids)
            body_html = rendered_template['body_html']


            attachment_ids = signer.sign_request_id.attachment_ids.ids
            self.env['sign.request']._message_send_mail(
                body_html, 'mail.mail_notification_light',
                {'record_name': signer.sign_request_id.reference},
                {'model_description': _('Signature'), 'company': signer.communication_company_id or signer.sign_request_id.create_uid.company_id},
                {'email_from': signer.create_uid.email_formatted,
                 'author_id': signer.create_uid.partner_id.id,
                 'email_to': formataddr((signer.partner_id.name, signer_email_normalized)),
                 'attachment_ids': attachment_ids,
                 'subject': signer.sign_request_id.subject},
                force_send=True,
                lang=signer_lang,
            )
            signer.is_mail_sent = True
            del context