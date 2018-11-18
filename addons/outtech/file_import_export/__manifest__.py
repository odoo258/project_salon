# -*- coding: utf-8 -*-
# © 2017 Outtech - http://www.outtech.com.br/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'File Import/Export',
    'description': '''== File Import/Export ==
    Import and Export Files to Oddo

    Extensions avaliable to import and export:

     - XML
     - TXT
     - CSV ''',
    'category': 'Base',
    'author': 'Outtech',
    'maintainer': 'Outtech',
    'summary': 'Import/Export File Module',
    'website': 'http://www.outtech.com.br/',
    'version': '001.01',
    'depends': [
                'base'
               ],
    'js': [],
    'css': [],
    'data': [
            'views/file_export_layout_view.xml',
            'views/file_import_layout_view.xml'
            ],

    'installable': True,
    'license': 'AGPL-3'
}

