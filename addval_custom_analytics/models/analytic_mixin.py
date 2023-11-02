from odoo import models, fields, api, _
from odoo.tools.float_utils import float_round, float_compare
from odoo.exceptions import UserError, ValidationError

class AnalyticMixin(models.AbstractModel):
    _inherit = 'analytic.mixin'

    analytic_distribution_area = fields.Json(
        'Área',
        compute='_compute_analytic_distribution_area', store=True, copy=True, readonly=False,
        precompute=True
    )

    analytic_distribution_activity = fields.Json(
        'Actividad',
        compute='_compute_analytic_distribution_activity', store=True, copy=True, readonly=False,
        precompute=True
    )

    analytic_distribution_area_search = fields.Json(
        store=False,
        search='_search_analytic_distribution_area'
    )

    analytic_distribution_activity_search = fields.Json(
        store=False,
        search='_search_analytic_distribution_activity'
    )

    def init(self):
        query = ''' SELECT table_name
                    FROM information_schema.tables
                    WHERE table_name=%s '''
        self.env.cr.execute(query,[self._table])
        if self.env.cr.dictfetchone(): 
            query = f"""
                CREATE INDEX IF NOT EXIST {self._table}_analytic_distribution_area_gin_index
                                       ON {self._table} USING gin(analytic_distribution_area);
            """
            self.env.cr.execute(query)
        query = ''' SELECT table_name
                    FROM information_schema.tables
                    WHERE table_name=%s '''
        self.env.cr.execute(query,[self._table])
        if self.env.cr.dictfetchone(): 
            query = f"""
                CREATE INDEX IF NOT EXIST {self._table}_analytic_distribution_activity_gin_index
                                       ON {self._table} USING gin(analytic_distribution_activity);
            """
            self.env.cr.execute(query)
        super().init()

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super().fields_get(allfields, attributes)
        if res.get('analytic_distribution_area_search'):
            res['analytic_distribution_area_search']['searchable'] = False
        if res.get('analytic_distribution_activity_search'):
            res['analytic_distribution_activity_search']['searchable'] = False
        return res
    
    def _compute_analytic_distribution_area(self):
        pass

    def _compute_analytic_distribution_activity(self):
        pass

    def _search_analytic_distribution(self, operator, value):
        if operator not in ['=', '!=', 'ilike', 'not ilike'] or not isinstance(value, (str, bool)):
            raise UserError(_('Operator nor supported'))
        operator_name_search = '=' if operator in ('=', '!=') else 'ilike'
        account_ids = list(self.env['account.analytic.account'].name_search(name=value, operator=operator_name_search))
        user_company = self.env.user.company_id        
        company_plan_id =  user_company.project_analytic_plan_id.id
        query = f"""
            SELECT id
            FROM {self._table}
            JOIN account_analytic_account ON {self._table}.analytic_account_id = account_analytic_account.id
            WHERE analytic_distribution ?| array[%s] AND account_analytic_acocunt.plan_id = %s
        """

        operator_inselect = 'inselect' if operator in ('=', 'ilike') else 'not inselect'
        return [('id', operator_inselect, (query, [[str(account_id) for account_id in account_ids], company_plan_id]))]
    
    def _search_analytic_distribution_area(self, operator, value):
        if operator not in ['=', '!=', 'ilike', 'not ilike'] or not isinstance(value, (str, bool)):
            raise UserError(_('Operator nor supported'))
        operator_name_search = '=' if operator in ('=', '!=') else 'ilike'
        account_ids = list(self.env['account.analytic.account'].name_search(name=value, operator=operator_name_search))
        user_company = self.env.user.company_id        
        company_plan_id =  user_company.area_analytic_plan_id.id
        query = f"""
            SELECT id
            FROM {self._table}
            JOIN account_analytic_account ON {self._table}.analytic_account_id = account_analytic_account.id
            WHERE analytic_distribution ?| array[%s] AND account_analytic_acocunt.plan_id = %s
        """

        operator_inselect = 'inselect' if operator in ('=', 'ilike') else 'not inselect'
        return [('id', operator_inselect, (query, [[str(account_id) for account_id in account_ids], company_plan_id]))]
    
    def _search_analytic_distribution_activity(self, operator, value):
        if operator not in ['=', '!=', 'ilike', 'not ilike'] or not isinstance(value, (str, bool)):
            raise UserError(_('Operator nor supported'))
        operator_name_search = '=' if operator in ('=', '!=') else 'ilike'
        account_ids = list(self.env['account.analytic.account'].name_search(name=value, operator=operator_name_search))
        user_company = self.env.user.company_id        
        company_plan_id =  user_company.activity_analytic_plan_id.id
        query = f"""
            SELECT id
            FROM {self._table}
            JOIN account_analytic_account ON {self._table}.analytic_account_id = account_analytic_account.id
            WHERE analytic_distribution ?| array[%s] AND account_analytic_acocunt.plan_id = %s
        """

        operator_inselect = 'inselect' if operator in ('=', 'ilike') else 'not inselect'
        return [('id', operator_inselect, (query, [[str(account_id) for account_id in account_ids], company_plan_id]))]

    def _apply_analytic_distribution_domain(self, domain):
        return[
            ('analytic_distribution_search', leaf[1], leaf[2]) if len(leaf) == 3 and leaf[0] == 'analytic_distribution' and isinstance(leaf[2], str) else leaf
            ('analytic_distribution_area_search', leaf[1], leaf[2]) if len(leaf) == 3 and leaf[0] == 'analytic_distribution_area' and isinstance(leaf[2], str) else leaf
            ('analytic_distribution_activity_search', leaf[1], leaf[2]) if len(leaf) == 3 and leaf[0] == 'analytic_distribution_activity' and isinstance(leaf[2], str) else leaf
            for leaf in domain
        ]