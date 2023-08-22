================================================
``website_product_brands`` changelog
================================================

*****
[version:0.1.2]  Date : 12-03-2018
*[Update]
    -Update templateas per new update in odoo view 
        template(id="wk_horizontal_brands" ,inherit_id="website_sale.products")
	Ref:https://github.com/odoo/odoo/blob/11.0/addons/website_sale/views/templates.xml#L173
       -<xpath expr="//div[@class='container oe_website_sale']/div[@class='products_pager']" position="after">
       +<xpath expr="//div[contains(@t-attf-class,'container oe_website_sale')]/div[@class='products_pager']" position="after">


*****

