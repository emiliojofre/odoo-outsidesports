# addval_website_b2b_login (Odoo 16)

Versión corregida para Outside Sports (`production/16.0`).

## Error de deploy que corrigió este commit

```
ParseError: Element '<xpath expr="//setting[@id='website_login_documents']">'
cannot be located in parent view
```

Ese xpath es de **Odoo 19**. En 16 las settings usan `div#website_info_settings`.

## Si el registry ya falló en Odoo.sh

En el shell:

```bash
# 1) Quitar la vista rota de la BD (permite volver a arrancar)
psql -d addval-connect-odoo-outsidesports-main-14434118 -c \
  "DELETE FROM ir_ui_view WHERE name = 'res.config.settings.view.form.b2b.login';
   DELETE FROM ir_model_data WHERE module='addval_website_b2b_login'
     AND name='res_config_settings_view_form_b2b_login';"

# 2) Reemplazar el módulo en src/user con esta versión 16.0
# 3) Restart + upgrade:
odoo-bin -u addval_website_b2b_login -d addval-connect-odoo-outsidesports-main-14434118 --stop-after-init
```

## Verificar logout

```bash
curl -sI 'https://b2b.outsidesports.cl/web/session/logout?redirect=/' | head -3
# Esperado: 303 (no 500)
```
