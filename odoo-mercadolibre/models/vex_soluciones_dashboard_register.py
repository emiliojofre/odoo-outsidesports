from odoo import models, fields, api
import json
from datetime import datetime, time, timedelta
from pytz import timezone, UTC
import logging
_logger = logging.getLogger(__name__)
class VexDashboardRecord(models.Model):
    _name = "vex.dashboard.record"
    _description = "Vex Dashboard Record"
    _order = "date desc"

    date = fields.Date("Fecha", default=fields.Date.context_today, required=True)

    orders_synced_today = fields.Integer()
    total_orders = fields.Integer()
    new_customers_this_month = fields.Integer()
    total_customers = fields.Integer()
    total_products = fields.Integer()
    total_questions = fields.Integer()

    top_clients_json = fields.Text()
    top_products_json = fields.Text()
    recent_orders_json = fields.Text()
    customers_evolution_json = fields.Text()
    total_earnings_json = fields.Text()
    average_customer_order_json = fields.Text()
    top_categories_json = fields.Text()
    completed_and_canceled_json = fields.Text()
    sales_by_channel_json = fields.Text()
    questions_by_category_json = fields.Text()
    
    @api.model
    def generate_json_dashboard(self, *args, **kwargs):
        record = self.search([], order="date desc", limit=1)
        if not record:
            return {}        
        return {
            "orders_synced_today": record.orders_synced_today,
            "total_orders": record.total_orders,
            "new_customers_last_month": record.new_customers_this_month,
            "total_customers": record.total_customers,
            "total_products": record.total_products,
            "total_questions": record.total_questions,
            "top_clients": json.loads(record.top_clients_json or "[]"),
            "top_products": json.loads(record.top_products_json or "[]"),
            "recent_orders": json.loads(record.recent_orders_json or "[]"),
            "customers_evolution": json.loads(record.customers_evolution_json or "{}"),
            "total_earnings": json.loads(record.total_earnings_json or "{}"),
            "average_customer_order": json.loads(record.average_customer_order_json or "{}"),
            "top_categories_sold": json.loads(record.top_categories_json or "[]"),
            "completed_and_canceled": json.loads(record.completed_and_canceled_json or "{}"),
            "sales_distribution_by_channel": json.loads(record.sales_by_channel_json or "{}"),
            "questions": json.loads(record.questions_by_category_json or "{}")
        }

    @api.model
    def generate_dashboard_record_daily(self):
        user_tz = self.env.user.tz or 'UTC'
        _logger.info(f"User: {self.env.user.tz}")
        _logger.info(f"User timezone: {user_tz}")
        today = datetime.now(timezone(user_tz)).date()
        existing_record = self.search([('date', '=', today)], limit=1)

        _logger.info(f"Generating dashboard record for {today}")
        mercado_libre_marketplace = self.env.ref('odoo-mercadolibre.vex_marketplace_mercadolibre')

        total_orders = self.env['sale.order'].search_count([
            ('marketplace_ids', 'in', [mercado_libre_marketplace.id])
        ])
        primer_dia_mes = today.replace(day=1)
        values = {
            'date': today,
            'orders_synced_today': self.env['sale.order'].search_count([
                ('meli_date_create_without_time', '=', today),
                ('meli_order_id', '!=', '')
            ]),
            'total_orders': total_orders,
            'new_customers_this_month': self.env['res.partner'].search_count([
                ('create_date', '>=', primer_dia_mes),
                ('marketplace_ids', 'in', [mercado_libre_marketplace.id]),
            ]),
            'total_customers': self.env['res.partner'].search_count([('marketplace_ids', 'in', [mercado_libre_marketplace.id])]),
            'total_products': self.env['product.template'].search_count([('marketplace_ids', 'in', [mercado_libre_marketplace.id]), ('meli_status','=','active')]),
            'total_questions': self.env['vex.meli.questions'].search_count([]),

            'top_clients_json': json.dumps(self._get_top_clients()),
            'top_products_json': json.dumps(self._get_top_products()),
            'recent_orders_json': json.dumps(self._get_recent_orders()),
            'customers_evolution_json': json.dumps(self._get_customers_evolution()),
            'total_earnings_json': json.dumps(self._get_total_earnings()),
            'average_customer_order_json': json.dumps(self._get_avg_order()),
            'top_categories_json': json.dumps(self._get_top_categories()),
            'completed_and_canceled_json': json.dumps(self._get_completed_and_canceled()),
            'sales_by_channel_json': json.dumps(self._get_sales_by_channel()),
            'questions_by_category_json': json.dumps(self._get_questions_by_category()),
        }
        _logger.info(f"Values to save: {values}")
        if existing_record:
            existing_record.write(values)
        else:
            self.create(values)



    def _get_top_clients(self):
        query = """
            SELECT MIN(s.id) as sale_id, s.partner_id, COUNT(*) as order_count, SUM(s.amount_total) as total_volume
            FROM sale_order s
            WHERE s.state IN ('sale', 'done')
            GROUP BY s.partner_id
            ORDER BY total_volume DESC
            LIMIT 10
        """
        self.env.cr.execute(query)
        return [{
            'name': self.env['res.partner'].browse(r[1]).name,
            'order_number': r[2],
            'volume': r[3],
            'sale_order_id': r[0],  # Aquí está el ID de una orden representativa
        } for r in self.env.cr.fetchall()]


    def _get_top_products(self):
        query = """
            SELECT MIN(id) as line_id, product_id, COUNT(*) as qty, SUM(price_total) as total
            FROM sale_order_line
            GROUP BY product_id
            ORDER BY qty DESC
            LIMIT 10
        """
        self.env.cr.execute(query)
        return [{
            'product_name': self.env['product.product'].browse(r[1]).name,
            'number_of_sales': r[2],
            'sales_volume': r[3],
            'id': r[0]
        } for r in self.env.cr.fetchall()]

    def _get_recent_orders(self):
        orders = self.env['sale.order'].search([('meli_order_id','!=','')], order="date_order desc", limit=5)
        return [{
            'id':o.id,
            'name': o.partner_id.name,
            'order_number': o.name,
            'mail': o.partner_id.email or "",
            'phone': o.partner_id.phone or "",
            'amount': o.amount_total,
            'products': len(o.order_line)
        } for o in orders]

    def _get_customers_evolution(self):
        labels, data = [], []
        for i in range(6):
            date = fields.Date.today() - timedelta(days=i * 30)
            labels.insert(0, date.strftime("%b"))
            data.insert(0, self.env['res.partner'].search_count([
                ('customer_rank', '>', 0),
                ('create_date', '>=', date.replace(day=1)),
                ('create_date', '<', date.replace(day=28) + timedelta(days=4))
            ]))
        return {"labels": labels, "datasets": [{"label": "Customers", "data": data}]}

    def _get_total_earnings(self):
        labels, data = [], []
        for i in range(6):
            date = fields.Date.today() - timedelta(days=i * 30)
            orders = self.env['sale.order'].search([
                ('state', 'in', ['sale', 'done']),
                ('date_order', '>=', date.replace(day=1)),
                ('date_order', '<', date.replace(day=28) + timedelta(days=4))
            ])
            labels.insert(0, date.strftime("%b"))
            data.insert(0, sum(orders.mapped('amount_total')))
        return {"labels": labels, "datasets": [{"label": "Earnings", "data": data}]}

    def _get_avg_order(self):
        labels, data = [], []
        for i in range(6):
            date = fields.Date.today() - timedelta(days=i * 30)
            orders = self.env['sale.order'].search([
                ('state', 'in', ['sale', 'done']),
                ('date_order', '>=', date.replace(day=1)),
                ('date_order', '<', date.replace(day=28) + timedelta(days=4))
            ])
            avg = sum(orders.mapped('amount_total')) / len(orders) if orders else 0
            labels.insert(0, date.strftime("%b"))
            data.insert(0, avg)
        return {"labels": labels, "datasets": [{"label": "Sales evolution", "data": data}]}

    def _get_top_categories(self):
        query = """
            SELECT pt.categ_id, SUM(sol.price_total) AS total_sales
            FROM sale_order_line sol
            JOIN product_product pp ON sol.product_id = pp.id
            JOIN product_template pt ON pp.product_tmpl_id = pt.id
            JOIN sale_order so ON sol.order_id = so.id
            WHERE so.state IN ('sale', 'done')
            GROUP BY pt.categ_id
            ORDER BY total_sales DESC
            LIMIT 5
        """
        self.env.cr.execute(query)
        result = []
        for categ_id, total in self.env.cr.fetchall():
            category = self.env['product.category'].browse(categ_id)
            result.append({
                "category": category.display_name,
                "sales": total
            })
        return result


    def _get_completed_and_canceled(self):
        labels, completed, canceled = [], [], []
        for i in range(5):
            date = fields.Date.today() - timedelta(days=i * 30)
            labels.insert(0, date.strftime("%b"))
            completed.append(self.env['sale.order'].search_count([
                ('state', '=', 'done'),
                ('date_order', '>=', date.replace(day=1)),
                ('date_order', '<', date.replace(day=28) + timedelta(days=4))
            ]))
            canceled.append(self.env['sale.order'].search_count([
                ('state', '=', 'cancel'),
                ('date_order', '>=', date.replace(day=1)),
                ('date_order', '<', date.replace(day=28) + timedelta(days=4))
            ]))
        return {"labels": labels, "datasets": [
            {"label": "Completed", "data": completed},
            {"label": "Canceled", "data": canceled}
        ]}

    def _get_sales_by_channel(self):
        return {
            "labels": ["Ene", "Feb", "Mar", "Abr", "May"],
            "datasets": [
                {"label": "Web", "data": [10000, 15000, 18000, 16000, 17000]},
                {"label": "Marketplace", "data": [8000, 9000, 10000, 9500, 9800]}
            ]
        }

    def _get_questions_by_category(self):
        return {
            "labels": ["Electrónica", "Moda", "Hogar", "Otros"],
            "datasets": [{"label": "History", "data": [6, 3, 4, 1]}]
        }
