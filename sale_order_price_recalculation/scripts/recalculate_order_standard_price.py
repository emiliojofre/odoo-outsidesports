import odoorpc
host_ip = 'localhost'
odoocnx = odoorpc.ODOO(host_ip, port=8069)
odoocnx.login('Produccion', 'desarrollo', 'Ger2021;')
x_template = odoocnx.env['product.template']

x_sale_order = odoocnx.env['sale.order']
x_sale_order_line = odoocnx.env['sale.order.line']
o_ids = x_sale_order.search([['id', '>=', 4481], ['id', '<', 5059]], order='id asc')
for order in x_sale_order.browse(o_ids):
    print(str(order.id))
    sum_line_cost = 0
    sum_line_price = 0 
    ol_id = x_sale_order_line.search([['order_id', '=', order.id]])
    for item in x_sale_order_line.browse(ol_id):
        #print(str(item.standard_price))
        item.standard_price = item.product_id.standard_price
        item.purchase_price = item.product_id.standard_price
        sum_line_cost += item.product_id.standard_price * item.product_uom_qty
        sum_line_price += item.price_subtotal
        #print(str(item.standard_price))
    order.margin = sum_line_price - sum_line_cost
    #print(str(order.margin))