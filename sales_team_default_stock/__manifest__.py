#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
    'name': 'Sales Team : Default Stock Location',
    'version': '1.0.1',
	'sequence': 1,
	'summary':"""Change source location of stock move according to sales team""",
    'category': 'A Module of WEBKUL Software Pvt Ltd.',
    'description': """	
               Module will set source location for stock moves according to routes defined for sales team.Different sales team can sell products from different locations of same warehouse
    """,
    'author': 'Webkul Software Pvt. Ltd.',
    "license" :  "Other proprietary",
    'depends': ['sale_stock'],
    'website': 'http://www.webkul.com',
    "live_test_url" : "http://odoodemo.webkul.com/?module=sales_team_default_stock",
    'data': ['views/inherited_view.xml'],
    "images" : ['static/description/Banner.png'],
    'installable': True,
    'auto_install': False,
    "price" :  49,
    "currency" : "EUR",
    #'certificate': '0084849360985',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
