# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
{
    'name': 'Zoho Integration',
    'version': '17.0',
    'category': 'Tools',
    'summary': 'Module for Zoho integration with Odoo',
    'author': '',
<<<<<<< HEAD
    'depends': ['base','project'],
=======
    'depends': ['base','product','stock'],
>>>>>>> 133f03343d0f6a744e8175c20278022373b2df0a
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