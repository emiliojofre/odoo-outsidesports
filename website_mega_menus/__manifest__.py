# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2016-Present Webkul Software Pvt. Ltd.
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

  "name"                 :  "Website Mega Menu",
  "summary"              :  "Add Mega Menus to your website and make it look easy to navigate and attractive.",
  "category"             :  "Website",
  "version"              :  "1.2.1",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com",
  "description"          :  """https://store.webkul.com""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=website_mega_menus&version=11.0",
  "depends"              :  [
                             'website_sale','website_webkul_addons'
                            ],
  "data"                 :  [
                             'views/templates.xml',
                             'views/res_config_view.xml',
                             'views/webiste_view.xml',
                             'views/res_config_view.xml',
                             'views/webkul_addons_config_inherit_view.xml',

                            ],
  "demo"                 :['data/demo.xml'],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  30,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",

}
