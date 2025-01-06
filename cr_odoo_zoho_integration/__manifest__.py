# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
{
    'name': 'Zoho Integration',
    'version': '17.0',
    'category': 'Tools',
    'summary': 'Module for Zoho integration with Odoo',
    'author': '',
    'depends': ['base','product','stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/zoho_config_views.xml',
        'views/view_success_message.xml',
        'views/logs.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'OPL-1',
}

