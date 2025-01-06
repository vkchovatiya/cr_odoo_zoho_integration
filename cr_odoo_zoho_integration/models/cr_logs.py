# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields

class DataProcessingLog(models.Model):
    _name = 'cr.data.processing.log'
    _description = 'Log of data processing operations'

    cr_configuration_id = fields.Many2one('zoho.config', string='Zoho Config', required=True)
    cr_table_name = fields.Char('Name', required=True)
    cr_record_count = fields.Integer('Number of Records', required=True)
    cr_status = fields.Selection([
        ('success', 'Success'),
        ('failure', 'Failure')
    ], default='success', required=True)
    cr_error_message = fields.Text('Error Message')
    cr_timestamp = fields.Char('Timestamp')
    cr_initiated_at = fields.Char('Initiated At')
    cr_message = fields.Char('Message')
# class ResPartner(models.Model):
#     _inherit = 'res.partner'
#
#     cr_recurly_id = fields.Char(string='Recurly Account Id')
#     username = fields.Char(string='Recurly username')
#     cc_emails = fields.Integer(string='Recurly CC Emails')


