# -*- coding: utf-8 -*-

import time
from odoo import api, fields, models
from datetime import datetime


class ReportOverdue(models.AbstractModel):
    _name = 'report.customer_due_payment.report_overdue'

    def _get_account_move_lines(self, partner_ids):
        res = dict(map(lambda x:(x,[]), partner_ids))
        self.env.cr.execute("SELECT m.name AS move_id, l.date, l.name, l.ref, l.date_maturity, l.partner_id, l.blocked, l.amount_currency, l.currency_id, "
            "CASE WHEN aat.type = 'receivable' "
                "THEN SUM(l.debit) "
                "ELSE SUM(l.credit * -1) "
            "END AS debit, "
            "CASE WHEN aat.type = 'receivable' "
                "THEN SUM(l.credit) "
                "ELSE SUM(l.debit * -1) "
            "END AS credit, "
            "CASE WHEN l.date_maturity < %s "
                "THEN SUM(l.debit - l.credit) "
                "ELSE 0 "
            "END AS mat "
            "FROM account_move_line l "
            "JOIN account_move m ON (l.move_id = m.id) "
            "LEFT JOIN account_account aa ON aa.id = l.account_id "
            "LEFT JOIN account_account_type aat ON aat.id = aa.user_type_id "
            "WHERE l.partner_id IN %s AND aat.type IN ('receivable', 'payable') AND l.full_reconcile_id IS NULL GROUP BY l.date, l.name, l.ref, l.date_maturity, l.partner_id, aat.type, l.blocked, l.amount_currency, l.currency_id, l.move_id, m.name ", (((fields.date.today(), ) + (tuple(partner_ids),))))
        for row in self.env.cr.dictfetchall():
            res[row.pop('partner_id')].append(row)
        return res

    @api.model
    def _get_report_values(self, docids, data=None):
        print("called")
        totals = {}
        lines = self._get_account_move_lines(docids)
        print ("lines",lines)
        lines_to_display = {}
        company_currency = self.env.user.company_id.currency_id
        for partner_id in docids:
            lines_to_display[partner_id] = {}
            totals[partner_id] = {}
            for line_tmp in lines[partner_id]:
                line = line_tmp.copy()
                currency = line['currency_id'] and self.env['res.currency'].browse(line['currency_id']) or company_currency
                if currency not in lines_to_display[partner_id]:
                    lines_to_display[partner_id][currency] = []
                    totals[partner_id][currency] = dict((fn, 0.0) for fn in ['due', 'paid', 'mat', 'total'])
                if line['debit'] and line['currency_id']:
                    line['debit'] = line['amount_currency']
                if line['credit'] and line['currency_id']:
                    line['credit'] = line['amount_currency']
                if line['mat'] and line['currency_id']:
                    line['mat'] = line['amount_currency']
                lines_to_display[partner_id][currency].append(line)
                if not line['blocked']:
                    totals[partner_id][currency]['due'] += line['debit']
                    totals[partner_id][currency]['paid'] += line['credit']
                    totals[partner_id][currency]['mat'] += line['mat']
                    totals[partner_id][currency]['total'] += line['debit'] - line['credit']
        print(docids,totals)
        print(lines_to_display)
        return {
            'doc_ids': docids,
            'doc_model': 'res.partner',
            'docs': self.env['res.partner'].browse(docids),
            'time': time,
            'Lines': lines_to_display,
            'Totals': totals,
            'Date': datetime.now(),
        }
        # print(docargs)
        # return docargs
        # return self.env['report'].render('customer_due_payment.report_overdue', values=docargs)
