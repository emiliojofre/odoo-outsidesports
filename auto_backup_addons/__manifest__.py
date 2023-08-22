# -*- coding: utf-8 -*-
###############################################################################
#
#   Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
#   Copyright (C) 2016-today Geminate Consultancy Services (<http://geminatecs.com>).
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

{
    'name' : 'Addons Auto-Backup',
    'description': """Geminate comes with feature to auto backup your addons and custom addons from your "source location" to desired "destination location" in same server or different server over secure ftp layer in zip format. No worries about crash or damage of the system. we ll help you to take care of your source codes. :)""",
    'summary': 'Addons Auto-Backup',
    'version' : '11.0.1.0',
    'author' : 'Geminate Consultancy Services',
    'company': 'Geminate Consultancy Services',
    'website' : 'https://www.geminatecs.com',
    'category' : 'Generic Modules',
    'depends' : ['base'],
    'data': [
      'security/ir.model.access.csv',   
      'views/bkp_conf_view.xml',
      'data/backup_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'price': 39.99,
    'currency': 'EUR',
    'images': ['static/description/backup.png']
}
