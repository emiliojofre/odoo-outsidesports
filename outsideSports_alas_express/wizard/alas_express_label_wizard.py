# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AlasExpressLabelWizard(models.TransientModel):
    """
    Wizard para enviar múltiples albaranes a Alas Express de una vez
    y/o regenerar etiquetas en lote.
    """
    _name = 'alas.express.label.wizard'
    _description = 'Wizard Alas Express - Envío masivo'

    picking_ids = fields.Many2many(
        'stock.picking',
        string='Albaranes',
        required=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Empresa',
        default=lambda self: self.env.company,
    )
    action_type = fields.Selection([
        ('create_order', 'Crear Órdenes de Entrega'),
        ('get_labels', 'Obtener Etiquetas'),
        ('get_status', 'Actualizar Estado'),
        ('reject', 'Rechazar Órdenes'),
    ], string='Acción', default='create_order', required=True)

    result_log = fields.Text(
        string='Resultado',
        readonly=True,
    )

    @api.model
    def action_open_wizard(self):
        """Abre el wizard desde la acción masiva en la lista de pickings."""
        wizard = self.create({
            'picking_ids': [(6, 0, self.env.context.get('active_ids', []))],
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'dialog_size': 'extra-large'},
        }

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_ids = self.env.context.get('active_ids', [])
        if active_ids:
            res['picking_ids'] = [(6, 0, active_ids)]
        return res

    def action_execute(self):
        """Ejecuta la acción seleccionada sobre todos los albaranes."""
        self.ensure_one()
        results = []
        errors = []

        for picking in self.picking_ids:
            carrier = picking.carrier_id
            if not carrier or carrier.delivery_type != 'alas_express':
                errors.append(f'  - {picking.name}: No tiene método de envío Alas Express.')
                continue

            try:
                if self.action_type == 'create_order':
                    if picking.alas_delivery_order_id:
                        errors.append(f'  - {picking.name}: Ya tiene orden Alas (ID: {picking.alas_delivery_order_id}).')
                        continue
                    carrier.alas_create_delivery_order(picking)
                    results.append(f'  ✔ {picking.name} → ID: {picking.alas_delivery_order_id}')

                elif self.action_type == 'get_labels':
                    carrier.alas_get_label(picking)
                    results.append(f'  ✔ {picking.name} → Etiqueta guardada.')

                elif self.action_type == 'get_status':
                    carrier.alas_get_status(picking)
                    results.append(f'  ✔ {picking.name} → Estado: {picking.alas_status}')

                elif self.action_type == 'reject':
                    carrier.alas_reject_order(picking)
                    results.append(f'  ✔ {picking.name} → Rechazada. Estado: {picking.alas_status}')

            except UserError as e:
                errors.append(f'  ✘ {picking.name}: {e.args[0]}')
            except Exception as e:
                _logger.exception('Alas Wizard: error inesperado en %s', picking.name)
                errors.append(f'  ✘ {picking.name}: Error inesperado - {str(e)}')

        log_parts = []
        if results:
            log_parts.append('EXITOSOS:\n' + '\n'.join(results))
        if errors:
            log_parts.append('CON ERRORES:\n' + '\n'.join(errors))

        self.result_log = '\n\n'.join(log_parts) if log_parts else 'Sin resultados.'

        # Mantener wizard abierto mostrando resultados
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
