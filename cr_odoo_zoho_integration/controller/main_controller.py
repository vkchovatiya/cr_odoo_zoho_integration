# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class ZohoController(http.Controller):

    @http.route('/zoho/auth', type='http', auth='public', csrf=False)
    def zoho_auth(self, **kwargs):
        """Handle Zoho OAuth2 callback."""
        grant_token = kwargs.get('code')
        if not grant_token:
            return "Authorization failed: Grant token not found."

        zoho_config = request.env['zoho.config'].sudo().search([], limit=1)
        if not zoho_config:
            return "Zoho Configuration not found."

        try:
            zoho_config.exchange_grant_token(grant_token)
            return request.render('cr_odoo_zoho_integration.success_redirect_template')
        except Exception as e:
            return f"Authorization failed: {str(e)}"
