# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

import requests
from datetime import timedelta
from odoo import models, fields, _
from odoo.exceptions import UserError

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
    cr_data_logs_ids = fields.One2many(
        "cr.data.processing.log", "cr_configuration_id", string="Logs"
    )


    def generate_auth_url(self):
        """Generate the authorization URL to get the grant token."""
        auth_url = "https://accounts.zoho.com/oauth/v2/auth"
        params = {
            "scope": "ZohoCRM.users.ALL,ZohoCRM.modules.ALL,ZohoCRM.modules.leads.ALL,ZohoCRM.modules.deals.ALL,ZohoCRM.settings.ALL,ZohoBooks.fullaccess.all",
            "client_id": self.cr_client_id,
            "response_type": "code",
            "access_type": "offline",
            "redirect_uri": self.cr_redirect_uri,
        }
        url= f"{auth_url}?{requests.compat.urlencode(params)}"
        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "self",
        }

    def exchange_grant_token(self, grant_token):
        """Exchange grant token for access and refresh tokens."""
        token_url = "https://accounts.zoho.com/oauth/v2/token"
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
            print(tokens)
            self.write({
                'cr_access_token': tokens.get('access_token'),
                'cr_token_expiry': fields.Datetime.now() + timedelta(seconds=tokens.get('expires_in', 3600)),
            })
        except requests.RequestException as e:
            raise UserError(_("Error refreshing access token: %s") % e)
    
    def fetch_zoho_fields(self,module):
        """
        Fetch available fields for the Contacts module from Zoho CRM.
        """
        print('called')
        fields_url = "https://www.zohoapis.com/crm/v7/settings/fields"
        params = {"module": module}
        headers = {"Authorization": f"Zoho-oauthtoken {self.cr_access_token}"}

        try:
            response = requests.get(fields_url, headers=headers, params=params)

            data = response.json()

            if 'fields' in data:
                field_names = [field['api_name'] for field in data['fields']]
                print(f"Fetched fields: {field_names}")
                return field_names
            else:
                raise UserError(_("No fields data found in Zoho response."))

        except requests.RequestException as e:
            raise UserError(_("Error fetching Zoho fields: %s") % e)

    def _get_zoho_api_url(self, endpoint):
        """Helper method to build the Zoho API URL."""
        base_url = "https://www.zohoapis.com/crm/v2"
        return f"{base_url}/{endpoint}"

    def _check_access_token(self):
        """Ensure the access token is valid, refreshing it if necessary."""
        if not self.cr_access_token or fields.Datetime.now() >= self.cr_token_expiry:
            self.refresh_access_token()

    def fetch_zoho_deals(self):
        """Fetch all fields for deals from Zoho CRM v7."""
        self._check_access_token()

        # Define the API endpoints
        fields_metadata_url = "https://www.zohoapis.com/crm/v7/settings/fields"
        deals_api_url = "https://www.zohoapis.com/crm/v7/Deals"

        # Set up the request headers
        headers = {
            "Authorization": f"Zoho-oauthtoken {self.cr_access_token}",
        }

        try:
            # Step 1: Fetch metadata to get all fields
            metadata_params = {"module": "Deals"}
            metadata_response = requests.get(fields_metadata_url, headers=headers, params=metadata_params)
            metadata_response.raise_for_status()
            metadata = metadata_response.json()

            # Extract all field names
            fields = [field["api_name"] for field in metadata.get("fields", [])]
            fields_param = ",".join(fields)  # Convert list to comma-separated string

            # Step 2: Fetch deals with all fields
            deals_params = {"fields": fields_param}
            deals_response = requests.get(deals_api_url, headers=headers, params=deals_params)
            deals_response.raise_for_status()
            deals = deals_response.json()

            # Debugging: Print the full JSON response
            print("Deals Response:", deals)

            return deals

        except requests.RequestException as e:
            error_message = e.response.text if e.response else str(e)
            raise UserError(_("Error fetching deals from Zoho: %s") % error_message)

    def fetch_zoho_companies(self):
        """Fetch companies from Zoho CRM."""
        self._check_access_token()
        companies_api_url = "https://www.zohoapis.com/crm/v7/Accounts"
        fields_metadata_url = "https://www.zohoapis.com/crm/v7/settings/fields"
        headers = {
            "Authorization": f"Zoho-oauthtoken {self.cr_access_token}",
        }

        try:
            # Step 1: Fetch metadata to get all available fields
            metadata_params = {"module": "Accounts"}  # 'Accounts' is the Zoho module for companies
            metadata_response = requests.get(fields_metadata_url, headers=headers, params=metadata_params)
            metadata_response.raise_for_status()
            all_fields = [field["api_name"] for field in metadata_response.json().get("fields", [])]

            # Step 2: Split fields into manageable chunks
            def split_fields(fields, chunk_size=50):
                for i in range(0, len(fields), chunk_size):
                    yield fields[i:i + chunk_size]

            # Step 3: Fetch companies in chunks
            all_companies = []
            for field_chunk in split_fields(all_fields, chunk_size=50):
                field_params = ",".join(field_chunk)
                params = {"fields": field_params, "per_page": 200}  # Adjust per_page as needed
                response = requests.get(companies_api_url, headers=headers, params=params)
                response.raise_for_status()
                companies = response.json().get("data", [])
                all_companies.extend(companies)

            print("Fetched Companies:", all_companies)  # Process or store fetched companies

        except requests.RequestException as e:
            error_message = e.response.text if e.response else str(e)
            raise UserError(_("Error fetching companies from Zoho: %s") % error_message)

