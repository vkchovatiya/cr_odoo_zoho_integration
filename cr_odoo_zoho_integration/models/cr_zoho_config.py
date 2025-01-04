# -*- coding: utf-8 -*-
import requests
from datetime import timedelta
from odoo import models, fields, _
from odoo.exceptions import UserError
import webbrowser

class ZohoConfig(models.Model):
    _name = 'zoho.config'
    _description = 'Zoho Configuration'
    _rec_name='cr_name'

    cr_name = fields.Char(string="Configuration Name", required=True, default="Zoho Configuration")
    cr_client_id = fields.Char(string="Client ID", required=True)
    cr_client_secret = fields.Char(string="Client Secret", required=True)
    cr_redirect_uri = fields.Char(string="Redirect URI", required=True)
    cr_access_token = fields.Text(string="Access Token" )
    cr_refresh_token = fields.Text(string="Refresh Token")
    cr_token_expiry = fields.Datetime(string="Token Expiry" )

    def generate_auth_url(self):
        """Generate the authorization URL to get the grant token."""
        auth_url = "https://accounts.zoho.com/oauth/v2/auth"
        params = {
            "scope": "ZohoCRM.users.ALL,ZohoCRM.modules.ALL,ZohoCRM.modules.leads.ALL,ZohoCRM.modules.deals.ALL,ZohoCRM.settings.ALL",
            "client_id": self.cr_client_id,
            "response_type": "code",
            "access_type": "offline",
            "redirect_uri": self.cr_redirect_uri,
        }
        url= f"{auth_url}?{requests.compat.urlencode(params)}"
        webbrowser.open(url)

    def exchange_grant_token(self, grant_token):
        """Exchange grant token for access and refresh tokens."""
        token_url = "https://accounts.zoho.in/oauth/v2/token"
        payload = {
            "grant_type": "authorization_code",
            "client_id": self.cr_client_id,
            "client_secret": self.cr_client_secret,
            "redirect_uri": self.cr_redirect_uri,
            "code": grant_token,
        }
        try:
            response = requests.post(token_url, data=payload)
            response.raise_for_status()
            tokens = response.json()
            print(tokens)
            self.write({
                'cr_access_token': tokens.get('access_token'),
                'cr_refresh_token': tokens.get('refresh_token'),
                'cr_token_expiry': fields.Datetime.now() + timedelta(seconds=tokens.get('expires_in', 3600)),
            })
        except requests.RequestException as e:
            raise UserError(_("Error exchanging grant token: %s") % e)

    def refresh_access_token(self):
        """Refresh the access token using the refresh token."""
        token_url = "https://accounts.zoho.com/oauth/v2/token"
        payload = {
            "grant_type": "refresh_token",
            "client_id": self.cr_client_id,
            "client_secret": self.cr_client_secret,
            "refresh_token": self.cr_refresh_token,
        }
        try:
            response = requests.post(token_url, data=payload)
            response.raise_for_status()
            tokens = response.json()
            self.write({
                'cr_access_token': tokens.get('access_token'),
                'cr_token_expiry': fields.Datetime.now() + timedelta(seconds=tokens.get('expires_in', 3600)),
            })
        except requests.RequestException as e:
            raise UserError(_("Error refreshing access token: %s") % e)
