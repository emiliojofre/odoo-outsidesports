# addval_website_b2b_login_fix (Odoo 16)

Parche para Outside Sports (`production/16.0` en Odoo.sh).

No reemplaza `addval_website_b2b_login`; solo evita el 500 en logout.

## Error

```
GET /web/session/logout?redirect=/ → 500
File ".../addval_website_b2b_login/models/ir_http.py", line 55
    if not request.env.user._is_public():
ValueError: Expected singleton: res.users()
```

## Deploy en Odoo.sh (Outside)

1. Copiar este módulo a `src/user/addval_website_b2b_login_fix` del repo git del proyecto.
2. Commit + push a la rama de producción (`16.0` / production).
3. En el shell Odoo.sh, tras el build:

```bash
odoo-bin -u addval_website_b2b_login_fix -d addval-connect-odoo-outsidesports-main-14434118 --stop-after-init
```

O instalarlo desde Apps: **Addval Website B2B Login - Logout Fix**.

## Fix inmediato en shell (sin esperar git, se pierde en rebuild)

```bash
FILE=/home/odoo/src/user/addval_website_b2b_login/models/ir_http.py
cp -a "$FILE" "${FILE}.bak.$(date +%Y%m%d%H%M%S)"
python3 - <<'PY'
from pathlib import Path
path = Path('/home/odoo/src/user/addval_website_b2b_login/models/ir_http.py')
text = path.read_text()
old = 'if not request.env.user._is_public():'
new = (
    'user = request.env.user\n'
    '        if not user:\n'
    '            return\n'
    '        if not user._is_public():'
)
if old not in text:
    raise SystemExit('Patrón no encontrado; revisar el archivo manualmente')
if 'if not user:\n            return' in text:
    raise SystemExit('Ya parece parcheado')
path.write_text(text.replace(old, new, 1))
print('OK: parche aplicado en', path)
PY
# Reiniciar workers (Odoo.sh: botón Restart, o)
# kill -HUP 1   # según entorno
```

Verificar:

```bash
curl -sI 'https://b2b.outsidesports.cl/web/session/logout?redirect=/' | head -5
# Esperado: HTTP/2 303  (no 500)
```
