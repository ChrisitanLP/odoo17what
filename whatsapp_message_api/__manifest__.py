
# -*- coding: utf-8 -*-
{
    'name': "WhatsappMessageAPI",

    'description': 'Send Product, Real All in One. Send and receive messages. Real ChatRoom. WhatsApp integration. '
                   'WhatsApp Connector. apichat.io. GupShup. Chat-Api. ChatApi. Drag and Drop. ChatRoom 2.0.',

    'author': "CodeCraft Studio",
    'website': "https://chrisitanlp.github.io/",
    'support': 'https://chrisitanlp.github.io/',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'price': 0.0,
    'currency': 'USD',
    'images': ['static/description/whatsapp.gif'],
    'application': True,
    'installable': True,
    'category': 'Discuss/Sales/CRM',
    'version': '16.0.1',
    #'uninstall_hook': 'uninstall_hook',
    'license': 'OPL-1',
    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sales_team',
        'product',
        'website',
    ],
    'test':[
        'tests/test_whatsapp_message.py',
    ],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/contact_template.xml',
        'views/message_template.xml',
        'views/chat_template.xml',
        'views/default_message_template.xml',
        'views/product_template.xml',
        'data/ir_config_parameter_data.xml',
        'views/Autentication.xml',
        'views/error_template.xml',
        'views/menu_template.xml',
        'views/options_template.xml',
    ],

    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'assets':{
        'web.assets_backend': [
            'whatsapp_message_api/static/src/scss/custom_style.scss',
            'whatsapp_message_api/static/src/scss/auth_style.scss',
            'whatsapp_message_api/static/src/js/qrcode.min.js',
            'whatsapp_message_api/static/src/js/sweetalert2.min.js',
            'whatsapp_message_api/static/src/scss/error_style.scss',
            'whatsapp_message_api/static/src/scss/menu_style.scss'
        ],
        'web.assets_frontend': [
            'whatsapp_message_api/static/src/scss/custom_style.scss',
            'whatsapp_message_api/static/src/scss/auth_style.scss',
            'whatsapp_message_api/static/src/js/qrcode.min.js',
            'whatsapp_message_api/static/src/js/sweetalert2.min.js',
            'whatsapp_message_api/static/src/scss/error_style.scss',
            'whatsapp_message_api/static/src/scss/menu_style.scss'
        ],
    }
}
