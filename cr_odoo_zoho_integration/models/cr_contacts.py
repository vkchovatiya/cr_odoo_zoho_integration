# -*- coding: utf-8 -*-
import requests
from datetime import timedelta
from odoo import models, fields, _
from odoo.exceptions import UserError

class ZohoConfig(models.Model):
    _inherit = 'zoho.config'

    def fetch_contacts_page(self, fields_batch, page):
        """
        Fetch a single page of contacts for the specified fields batch.
        """
        fields_param = ",".join(fields_batch)
        contacts_url = "https://www.zohoapis.com/crm/v7/Contacts"
        params = {
            "fields": fields_param,
            "page": page,
            "per_page": 200,  # Maximum allowed per_page value
        }
        headers = {"Authorization": f"Zoho-oauthtoken {self.cr_access_token}"}

        try:
            response = requests.get(contacts_url, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()
            return data.get('data', []), data.get('info', {}).get('more_records', False)
        except requests.RequestException as e:
            raise UserError(_("Error fetching contacts: %s") % e)

    def import_contacts(self):
        """
        Fetch all contacts from Zoho CRM by batching fields, paginating, and combining results.
        """
        all_fields = self.fetch_zoho_fields("Contacts")


        if not all_fields:
            raise UserError(_("No fields available to fetch contacts."))


        batch_size = 50
        contacts_combined = []


        for i in range(0, len(all_fields), batch_size):
            fields_batch = all_fields[i:i + batch_size]
            print(f"Fetching batch: {fields_batch}")

            page = 1
            while True:
                print(f"Fetching page {page} for fields batch")
                batch_contacts, more_records = self.fetch_contacts_page(fields_batch, page)


                for contact in batch_contacts:
                    contact_id = contact.get('id')
                    existing_contact = next(
                        (c for c in contacts_combined if c.get('id') == contact_id), None)

                    if existing_contact:

                        existing_contact.update(contact)
                    else:

                        contacts_combined.append(contact)

                if not more_records:
                    break
                page += 1


        print(f"Total contacts fetched: {len(contacts_combined)}")
        for contact in contacts_combined:

            last_name = contact.get('Full_Name')
            email = contact.get('Email')

            existing_contact = self.env['res.partner'].search(
                [('email', '=', email)], limit=1)

            if existing_contact:
                existing_contact.write({
                    'name': last_name,
                    'email': email,
                    'comment': str(contact),
                })
                print(f"Updated contact: {last_name}")
            else:
                self.env['res.partner'].create({
                    'name': last_name,
                    'email': email,
                    'comment': str(contact),
                })
                print(f"Created new contact: {last_name}")