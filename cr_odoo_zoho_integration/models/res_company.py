
# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    external_org_id = fields.Char(string='External Organization ID', help="Store Zoho Books Organization ID")
