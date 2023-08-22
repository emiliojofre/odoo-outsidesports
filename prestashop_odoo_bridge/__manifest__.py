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
  "name"                 :  "Multi Channel Prestashop Odoo Bridge(POB)",
  "summary"              :  "A solution to integrate your Prestashop ecommerce with the Odoo ERP.",
  "category"             :  "Website",
  "version"              :  "1.3",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Multi-Channel-Prestashop-Odoo-Bridge.html",
  "description"          :  """""",
  "live_test_url"        :  "http://prestashop.webkul.com/pob/pob_multichannel/content/6-demo-link",
  "depends"              :  ['odoo_multi_channel_sale', 'base_address_city'],
  "data"                 :  [
                             'data/cron.xml',
                             'data/data.xml',
                             'views/dashboard.xml',
                             'views/views.xml',
                             'wizard/inherits.xml',
                             'wizard/wizard.xml'
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  99,
  "currency"             :  "EUR",
  "external_dependencies": {"python":["html2text"]}
}
