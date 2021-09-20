# -*- coding: utf-8 -*-
{
    'name': "ganado",
    'version': '0.2',
    'sequence': 1,
    'category': 'Human Resources/Ganado',
    'website': 'https://www.yourcompany.com',
    'summary': """
        prototipo informacion finca ganadera doble proposito""",

    'description': """
        Modulo de control de produccion...
    """,

    'author': "Jaime Velez",
    'website': "http://www.yourcompany.com",


    'depends': ['base',
                'show_db_name',
                'web_widget_multi_image',
                'report_xlsx',
                'board'],

    'data': [
        'security/ganado_security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/caricaturas.xml',
        'views/animales.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
}
