# -*- coding: utf-8 -*-
import requests
from datetime import datetime
from odoo import models, fields, _
from odoo.exceptions import UserError

class ZohoConfig(models.Model):
    _inherit = 'zoho.config'

    def fetch_products_page(self, fields_batch, page):
        """
        Fetch a single page of products for the specified fields batch.
        """
        fields_param = ",".join(fields_batch)
        products_url = "https://www.zohoapis.com/crm/v7/Products"
        params = {
            "fields": fields_param,
            "page": page,
            "per_page": 200,
        }
        headers = {"Authorization": f"Zoho-oauthtoken {self.cr_access_token}"}

        try:
            response = requests.get(products_url, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()

            return data.get('data', []), data.get('info', {}).get('more_records', False)
        except requests.RequestException as e:
            raise UserError(_("Error fetching products: %s") % e)


    def import_products(self):
        """
        Import products from Zoho CRM and organize them as variants under a parent product.
        """
        start_time = datetime.now()
        initiated_at = start_time
        # Step 1: Fetch all fields for the Products module from Zoho
        all_fields = self.fetch_zoho_fields("Products")
        if not all_fields:
            raise UserError(_("No fields available to fetch products."))

        # Batch size for Zoho API requests
        batch_size = 50
        products_combined = []

        # Step 2: Fetch and combine product data from Zoho in batches
        for i in range(0, len(all_fields), batch_size):
            fields_batch = all_fields[i:i + batch_size]
            print(f"Fetching batch: {fields_batch}")
            page = 1

            while True:
                print(f"Fetching page {page} for fields batch")
                batch_products, more_records = self.fetch_products_page(fields_batch, page)

                # Merge product data from this batch with existing data
                for product in batch_products:
                    product_id = product.get('id')
                    existing_product = next((p for p in products_combined if p.get('id') == product_id), None)

                    if existing_product:
                        existing_product.update(product)
                    else:
                        products_combined.append(product)

                if not more_records:
                    break
                page += 1

        print(f"Total products fetched: {len(products_combined)}")
        print(products_combined)
        # parent_product_name = ''
        # for product in products_combined:
        #     parent_ = product.get('Project_Name')
        #     parent_product_name =parent_.get('name')
        # print(parent_product_name)
        #
        # parent_product = self.env['product.template'].search([('name', '=', parent_product_name)], limit=1)
        # if not parent_product:
        #     parent_product = self.env['product.template'].create({
        #         'name': parent_product_name,
        #     })
        #     print(f"Created parent product: {parent_product_name}")
        # else:
        #     print(f"Parent product already exists: {parent_product_name}")
        #
        # # Step 4: Fetch or create the "Variant" attribute
        # attribute = self.env['product.attribute'].search([('name', '=', "Rove Home Dubai Marina")], limit=1)
        # if not attribute:
        #     attribute = self.env['product.attribute'].create({'name': "Rove Home Dubai Marina"})
        #     print(f"Created attribute: Variant")
        #
        # # Step 5: Process each product as a variant
        # for product in products_combined:
        #     product_name = product.get('Product_Name')
        #     product_code = product.get('Product_Code')
        #     description = product.get('Description')
        #
        #     # Fetch or create the attribute value
        #     attribute_value = self.env['product.attribute.value'].search([
        #         ('name', '=', product_name),
        #         ('attribute_id', '=', attribute.id)
        #     ], limit=1)
        #
        #     if not attribute_value:
        #         attribute_value = self.env['product.attribute.value'].create({
        #             'name': product_name,
        #             'attribute_id': attribute.id,
        #         })
        #         print(f"Created attribute value: {product_name}")
        #     else:
        #         print(f"Attribute value already exists: {product_name}")
        #
        #     # Check if the attribute line exists for the parent product
        #     attribute_line = parent_product.attribute_line_ids.filtered(
        #         lambda line: line.attribute_id.id == attribute.id)
        #     if not attribute_line:
        #         # Create a new attribute line with the attribute and value
        #         attribute_line = self.env['product.template.attribute.line'].create({
        #             'product_tmpl_id': parent_product.id,
        #             'attribute_id': attribute.id,
        #             'value_ids': [(4, attribute_value.id)],
        #         })
        #         print(f"Created attribute line with value: {product_name}")
        #     else:
        #         # Add the new value to the existing attribute line
        #         attribute_line.write({'value_ids': [(4, attribute_value.id)]})
        #         print(f"Updated attribute line with value: {product_name}")
        #
        # print(f"Successfully imported products and set up variants for {parent_product_name}.")