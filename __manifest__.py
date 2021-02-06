# -*- coding: utf-8 -*-
{
    'name': "ganado",
    'version': '0.1',
    'sequence': 1,
    'category': 'Human Resources/Ganado',
    'website': 'https://www.serviporno.com',
    'summary': """
        EL toro a al vaca se la mete y se la saca... 
        la vaca agradecida se la chupa y se la estira""",

    'description': """
        Modulo de control de produccion...
    """,

    'author': "Jaime Velez",
    'website': "http://www.yourcompany.com",


    'depends': ['base',
                'show_db_name'],

    'data': [
        'security/ganado_security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/animales.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
}
