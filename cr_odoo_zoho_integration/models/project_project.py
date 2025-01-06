# -*- coding: utf-8 -*-
from odoo import models, fields

class ProjectProject(models.Model):
    _inherit = 'project.project'

    # Define the custom field to store the Zoho ID
    x_zoho_id = fields.Char(string='Zoho ID')
