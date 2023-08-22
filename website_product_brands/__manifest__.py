# -*- coding: utf-8 -*-
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
    "name" : "Website Product Brand",
    "summary" : "It allows you to add brand to the products and manage them accordingly.",
    "category" : "Website",
    "version" : "1.0.2",
    "sequence" : 1,
    "author" : "Webkul Software Pvt. Ltd.",
    "license" : "Other proprietary",
    "website" : "https://store.webkul.com/Odoo-Website-Product-Brand.html",
    "description" : """http://webkul.com/blog/website-product-brand
        Odoo Website Product Brand For eCommerce""",
    "live_test_url" : "http://odoodemo.webkul.com/?module=website_product_brands",
    "depends" : ['website_base_filter_attribute'],
    "data" : [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/website_product_brands.xml',
        'views/template.xml',
    ],
    "images" : ['static/description/Banner.png'],
    "application" : True,
    "installable" : True,
    "price" : 35,
    "currency" : "EUR",
    "pre_init_hook" : "pre_init_check",
}
