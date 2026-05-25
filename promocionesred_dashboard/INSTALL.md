# ============================================================
# INSTRUCCIONES DE INSTALACIÓN — promocionesred_dashboard en Odoo 18
# Ruta Odoo: D:\Odoo-Proyect\odoo-18
# Fuente React: A:\03-DESARROLLO-APP\04_ODOO-MODULOS\Prototipos-Modulo-Odoo\01-Dashboard-Admin
# ============================================================

## PASO 1 — Copiar el módulo a la carpeta de addons de Odoo

Odoo 18 lee los módulos desde el directorio configurado en addons_path dentro de odoo.conf.
Tu instalación tiene la carpeta: D:\Odoo-Proyect\odoo-18\addons

### Opción A — Copiar directamente (más sencillo para desarrollo):
```powershell
Copy-Item -Recurse -Force `
  "A:\03-DESARROLLO-APP\04_ODOO-MODULOS\Prototipos-Modulo-Odoo\promocionesred_dashboard" `
  "D:\Odoo-Proyect\odoo-18\addons\promocionesred_dashboard"
```

### Opción B — Symlink (recomendado para desarrollo activo):
```powershell
# Ejecutar como Administrador:
New-Item -ItemType SymbolicLink `
  -Path "D:\Odoo-Proyect\odoo-18\addons\promocionesred_dashboard" `
  -Target "A:\03-DESARROLLO-APP\04_ODOO-MODULOS\Prototipos-Modulo-Odoo\promocionesred_dashboard"
```

---

## PASO 2 — Verificar addons_path en odoo.conf

Abre D:\Odoo-Proyect\odoo-18\odoo.conf y asegúrate de que la ruta de addons incluya
la carpeta donde está el módulo. Ejemplo:

```ini
addons_path = D:\Odoo-Proyect\odoo-18\addons,D:\Odoo-Proyect\odoo-18\oca_addons\l10n-spain
```

---

## PASO 3 — Actualizar la lista de módulos en Odoo

1. Activar modo desarrollador: URL → /web?debug=1
2. Ir a: Ajustes → Técnico → Actualizar lista de módulos
   (o bien: Ajustes → Módulos → Actualizar lista)
3. Buscar "PromocionesRed.com Dashboard" e instalar

---

## PASO 4 — Instalar desde línea de comandos (alternativa)

```powershell
# Desde D:\Odoo-Proyect\odoo-18\server
.\python\python.exe odoo-bin -u promocionesred_dashboard -d nombre_de_tu_bd --stop-after-init
```

---

## PASO 5 — Verificar el módulo en Odoo

1. Ir al menú principal de Odoo
2. Buscar "PromocionesRed.com" en la barra de apps
3. El menú debe aparecer en el top bar de Odoo

---

## VALIDACIÓN DE ZERO-ERRORES (3 Checks)

✅ Check 1 — Cabecera JS:
   Todos los archivos .js inician con: /** @odoo-module **/

✅ Check 2 — Template Matching:
   app.js:  static template = "promocionesred_dashboard.DashboardApp"
   app.xml: <t t-name="promocionesred_dashboard.DashboardApp">

✅ Check 3 — Tag Matching:
   app.js:      registry.category("actions").add("promocionesred.DashboardApp", DashboardApp)
   actions.xml: <field name="tag">promocionesred.DashboardApp</field>

---

## NOTAS DE MIGRACIÓN (Supabase → Odoo ORM)

| Supabase Table    | Odoo Model        | Notas                              |
|-------------------|-------------------|------------------------------------|
| leads             | pr.lead           | Migración directa de campos        |
| network           | pr.network        | Con jerarquía parent_id nativa     |
| email_logs        | pr.email.log      | Sin integración Gmail OAuth2 aún   |
| email_templates   | pr.email.template | Plantillas de correo básicas       |
| system_users      | res.users (Odoo)  | Login/autenticación nativa de Odoo |
| logs_movimientos  | mail.message      | Usando el chatter nativo de Odoo   |

## NOTA SOBRE GMAIL API

La integración de Gmail OAuth2 (Google GSI) no puede replicarse directamente en Odoo.
Alternativas disponibles en Odoo 18:
1. mail.outgoing.server — Configura SMTP de Gmail en Ajustes → Técnico → Servidores de correo
2. mail.thread — El chatter de Odoo para comunicaciones registradas
3. Para tracking de aperturas: módulo mass_mailing de Odoo (Marketing por Email)
