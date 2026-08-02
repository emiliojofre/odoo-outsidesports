# addval_website_b2b_login

Fuerza login en sitios web B2B (Outside: `b2b.outsidesports.cl`).

## Bug corregido

`/web/session/logout` respondía **500**:

```
File ".../addval_website_b2b_login/models/ir_http.py", line 55, in _frontend_pre_dispatch
    if not request.env.user._is_public():
ValueError: Expected singleton: res.users()
```

Causa: la ruta de logout usa `auth='none'`, `request.env.user` queda vacío y
`_is_public()` exige singleton.

## Fix

1. Whitelist de `/web/session/logout` (y assets / login / signup / reset).
2. Guard `if not request.env.user: return` antes de `_is_public()`.
3. Ruta logout con `auth='public'` + `website=True`.

## Deploy en Odoo.sh (Outside)

Sustituir el módulo en el repo git del proyecto Odoo.sh (`src/user/`):

```text
addval_website_b2b_login/
```

Luego en el build / shell:

```bash
odoo-bin -u addval_website_b2b_login -d <DB> --stop-after-init
```

Verificar en el website B2B:

- Website → Configuration → Settings → **B2B require login** = activado
  (el `post_init_hook` lo activa solo si el dominio/nombre contiene `b2b`).

## Prueba rápida

```bash
curl -sI https://b2b.outsidesports.cl/web/session/logout
# Esperado: 303 (no 500)
```
