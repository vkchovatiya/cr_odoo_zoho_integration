# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

from odoo import models, fields

class ZohoConfig(models.Model):
    _name = 'zoho.config'
    _description = 'Zoho Configuration'

    name = fields.Char(string="Configuration Name", required=True, default="Zoho Configuration")
    client_id = fields.Char(string="Client ID", required=True)
    client_secret = fields.Char(string="Client Secret", required=True)
    redirect_uri = fields.Char(string="Redirect URI", required=True)
    access_token = fields.Text(string="Access Token")
    refresh_token = fields.Text(string="Refresh Token")
