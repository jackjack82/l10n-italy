# -*- coding: utf-8 -*-


from odoo import fields, models, api, _


class StockPickingPackagePreparation(models.Model):
    _inherit = "stock.picking.package.preparation"

    # def _get_service_ids(self):
    #     ddt_ids = self.env['stock.picking.package.preparation'].browse(
    #         self.env.context['active_ids'])
    #     order_ids = ddt_ids.line_ids.mapped('sale_line_id.order_id')
    #     line_ids = order_ids.order_line.filtered(
    #         lambda l: l.qty_to_invoice > 0 and l.product_id.type == 'service')
    #     return line_ids.ids
    #
    # invoice_services = fields.Boolean('Invoice Services', default=True)
    # service_ids = fields.Many2many(
    #     'sale.order.line', default=_get_service_ids)

    @api.multi
    def action_invoice_create(self):
        """
        Once invoices are created with stockable products, we add them
        all the invoiceable services available in the SO related to the
        DDTs linked to the invoice
        """
        invoice_ids = super(StockPickingPackagePreparation, self).action_invoice_create()
        invoice_ids = self.env['account.invoice'].browse(invoice_ids)

        for invoice in invoice_ids:
            ddt_ids = invoice.ddt_ids
            order_ids = ddt_ids.line_ids.mapped('sale_line_id.order_id')
            line_ids = order_ids.order_line.filtered(
                lambda l: l.qty_to_invoice > 0 and
                l.product_id.type == 'service')

            # we call the Sale method for creating invoice
            for line in line_ids:
                qty = line.qty_to_invoice
                line.invoice_line_create(invoice.id, qty)

        return invoice_ids
