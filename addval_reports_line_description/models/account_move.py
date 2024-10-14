import base64
import logging

from odoo import fields, models

from io import BytesIO

_logger = logging.getLogger(__name__)

try:
    import pdf417gen
except ImportError:
    pdf417gen = None
    _logger.error('Could not import library pdf417gen')

class AccountMove(models.Model):
    _inherit = 'account.move'


    def _pdf417_barcode(self, barcode_data):
        #  This method creates the graphic representation of the barcode
        barcode_file = BytesIO()
        if pdf417gen is None:
            return False
        bc = pdf417gen.encode(barcode_data, security_level=5, columns=13)
        image = pdf417gen.render_image(bc, padding=15, scale=1)
        image.save(barcode_file, 'PNG')
        data = barcode_file.getvalue()
        _logger.warning('data: %s', data)

        _logger.warning('base64.b64encode(data): %s', base64.b64encode(data))
        return base64.b64encode(data)
    

    def _get_name_invoice_report(self):
        self.ensure_one()
        _logger.warning('l10n_latam_use_documents: %s', self.l10n_latam_use_documents)
        _logger.warning('account_fiscal_country_id: %s', self.company_id.account_fiscal_country_id.code)
        if self.l10n_latam_use_documents and self.company_id.account_fiscal_country_id.code == 'CL':
            return 'l10n_cl.report_invoice_document'
        return super()._get_name_invoice_report()