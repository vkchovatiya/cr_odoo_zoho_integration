# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

import requests
from odoo import models, fields, _
from odoo.exceptions import UserError

class ZohoOrganizations(models.Model):
    _inherit = 'zoho.config'
    _description = 'Zoho Organizations'


    def fetch_zoho_organizations(self):
        """Fetch all organization details from Zoho Books."""
        self._check_access_token()

        # Define the API endpoint for fetching organizations
        organizations_api_url = "https://www.zohoapis.com/books/v3/organizations"

        # Set up the request headers
        headers = {
            "Authorization": f"Zoho-oauthtoken {self.cr_access_token}",
        }

        try:
            # Fetch the organizations
            response = requests.get(organizations_api_url, headers=headers)
            response.raise_for_status()  # Raise an exception for 4xx/5xx responses
            organizations_data = response.json()

            # Check if the response contains organization data
            if organizations_data.get("code") != 0:
                raise UserError(
                    _("Error fetching organizations from Zoho Books: %s") % organizations_data.get("message"))

            # Extract the organization details
            organizations = organizations_data.get("organizations", [])

            # Iterate through each organization and process it
            for org in organizations:
                org_id = org.get("organization_id")
                org_name = org.get("name")
                org_contact_name = org.get("contact_name")
                org_email = org.get("email")
                org_currency = org.get("currency_code")
                org_timezone = org.get("time_zone")
                org_phone = org.get("phone")

                # Process the organization data (you can create/update in Odoo's res.company here)
                self.create_or_update_organization(org_id, org_name, org_contact_name, org_email, org_currency,
                                                   org_timezone, org_phone)

            return organizations  # Return the fetched organizations data

        except requests.RequestException as e:
            error_message = e.response.text if e.response else str(e)
            raise UserError(_("Error fetching organizations from Zoho Books: %s") % error_message)

    def create_or_update_organization(self, org_id, org_name, org_contact_name, org_email, org_currency, org_timezone, org_phone):
        """
        Create or update the organization in Odoo's res.company model.

        Args:
            org_id (int): The ID of the organization.
            org_name (str): The name of the organization.
            org_contact_name (str): The contact name of the organization.
            org_email (str): The email address of the organization.
            org_currency (str): The currency code of the organization.
            org_timezone (str): The timezone of the organization.
        """
        # Step 1: Find or create the associated partner
        partner = self.env['res.partner'].search([('name', '=', org_contact_name)], limit=1)
        if not partner:
            partner = self.env['res.partner'].create({
                'name': org_contact_name,
                'email': org_email,
                'phone': org_phone,
            })
        # Check if the organization already exists in Odoo
        company = self.env['res.company'].search([('external_org_id', '=', org_id)], limit=1)
        if company:
            # Update existing organization
            company.write({
                'name': org_name,
                'partner_id': partner.id,
                'email': org_email,
                'phone': org_phone,
                # 'currency_id': org_currency,  # You may need to map this to Odoo's currency model
                # 'timezone': org_timezone,  # You may need to map this to Odoo's timezone model
            })
            print(f"Updated existing organization: {company.name}")
        else:
            # Create a new organization
            self.env['res.company'].create({
                'name': org_name,
                'external_org_id': org_id,  # Store the external Org ID
                'partner_id': partner.id,
                'email': org_email,
                'phone': org_phone,
                # 'currency_id': org_currency,  # You may need to map this to Odoo's currency model
                # 'timezone': org_timezone,  # You may need to map this to Odoo's timezone model
            })
            print(f"Created new organization: {org_name}")