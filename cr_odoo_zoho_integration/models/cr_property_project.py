# -*- coding: utf-8 -*-
# Part of Creyox Technologies.

import requests
from odoo import models, fields, _
from odoo.exceptions import UserError

class ZohoPropertyProject(models.Model):
    _inherit = 'zoho.config'
    _description = 'Zoho Property Project'

    def fetch_zoho_property_project(self):
        """
        Fetch data from a custom module in Zoho CRM and create or update project records.
        """
        property_project_module = "Property_Project"  # Replace with your actual module name
        zoho_data = self.fetch_zoho_data(property_project_module)
        self.create_project_records_from_zoho(zoho_data)


    def fetch_zoho_data(self, Property_Project):
        """
        Fetch data from a custom module in Zoho CRM v7.
        :param module_api_name: API name of the custom module
        :return: Data from the custom module
        """
        self._check_access_token()

        # Define the API endpoints
        fields_metadata_url = f"https://www.zohoapis.com/crm/v7/settings/fields"
        module_api_url = f"https://www.zohoapis.com/crm/v7/{Property_Project}"

        headers = {
            "Authorization": f"Zoho-oauthtoken {self.cr_access_token}",
        }

        try:
            # Step 1: Fetch metadata to get all fields
            metadata_params = {"module": Property_Project}
            metadata_response = requests.get(fields_metadata_url, headers=headers, params=metadata_params)
            metadata_response.raise_for_status()
            metadata = metadata_response.json()

            # Extract all field names
            fields = [field["api_name"] for field in metadata.get("fields", [])]
            fields_param = ",".join(fields)  # Convert list to comma-separated string

            # Step 2: Fetch data from the custom module
            module_params = {"fields": fields_param}
            module_response = requests.get(module_api_url, headers=headers, params=module_params)
            module_response.raise_for_status()
            module_data = module_response.json()

            # Debugging: Print the full JSON response
            print("Custom Module Data:", module_data)

            return module_data

        except requests.RequestException as e:
            error_message = e.response.text if e.response else str(e)
            raise UserError(_("Error fetching data from Zoho custom module: %s") % error_message)

    def create_project_records_from_zoho(self, module_data):
        """
        Create project.project records in Odoo from Zoho CRM custom module data.
        :param module_data: Data fetched from Zoho CRM
        """
        if not module_data or 'data' not in module_data:
            raise UserError(_("No data found in Zoho CRM response."))

        for record in module_data['data']:
            organisation_id = record.get('Organisation_ID')
            if not organisation_id:
                continue

            # Match Organisation_ID with the company in Odoo
            company = self.env['res.company'].search([('external_org_id', '=', organisation_id)], limit=1)
            if not company:
                continue
            project_vals = self._prepare_project_values(record, company)
            self._create_or_update_project(record, project_vals)

    def _prepare_project_values(self, record, company):
        """
        Prepare values for creating or updating a project.
        :param record: Single Zoho record
        :param company: Matched Odoo company
        :return: Dictionary of project values
        """
        return {
            'name': record.get('Name', 'Unnamed Project'),
            'description': record.get('Building') or record.get('Description_of_Land'),
            'company_id': company.id,
            'user_id': self.env.user.id,  # Assign to the current user by default
            # 'partner_id': self.get_or_create_partner(record.get('Owner')),
            'date_start': record.get('Anticipated_Start_Date')[:10] if record.get('Anticipated_Start_Date') else False,
            'date': record.get('Anticipated_Completion_Date')[:10] if record.get(
                'Anticipated_Completion_Date') else False,
            # 'x_master_developer': record.get('Master_Developer_Name'),
            # 'x_developer': record.get('Developer'),
            # 'x_project_type': record.get('Project_Type'),
            # 'x_project_status': record.get('Project_Satus'),
            'x_zoho_id': record.get('id'),
        }

    def _create_or_update_project(self, record, project_vals):
        """
        Create or update a project record in Odoo.
        :param record: Single Zoho record
        :param project_vals: Prepared values for the project
        """
        project = self.env['project.project'].search([('x_zoho_id', '=', record['id'])], limit=1)
        if project:
            project.write(project_vals)
        else:
            self.env['project.project'].create(project_vals)

    def get_or_create_partner(self, owner_data):
        """
        Get or create a partner from Zoho owner data.
        :param owner_data: Dictionary containing owner information
        :return: ID of the partner record
        """
        if not owner_data or 'id' not in owner_data:
            return False

        partner = self.env['res.partner'].search([('x_zoho_owner_id', '=', owner_data['id'])], limit=1)
        if not partner:
            partner_vals = {
                'name': owner_data.get('name', 'Unknown Owner'),
                'email': owner_data.get('email'),
                'x_zoho_owner_id': owner_data['id'],
            }
            partner = self.env['res.partner'].create(partner_vals)
        return partner.id
