# 📦 Guión de Migración — `redlmc_es_labels`
## Del entorno local (Windows/Docker) al servidor Hetzner

> **Módulo:** `redlmc_es_labels` v18.0.1.0.0  
> **Propósito:** Adapta "Individuo" → "Persona Física" y "Compañía" → "Empresa"  
> **Instancia destino:** REDLMC SL (instancia 0, la maestra)  
> **Fecha de creación:** 2026-05-08  
> **Última revisión:** 2026-05-11

---

## ⚠️ Antes de empezar — Conceptos clave

Este módulo **NO crea tablas propias en PostgreSQL**.  
Solo redefine las etiquetas del campo `company_type` de `res.partner` (tabla nativa de Odoo).

Consecuencias para la migración:
- ✅ No hay datos propios que exportar
- ✅ No hay scripts SQL que ejecutar
- ✅ Solo hay que copiar el código y ejecutar `--init`
- ✅ La BD de producción no necesita ninguna preparación previa

---

## 📋 Checklist de migración

### FASE 1 — Preparar el servidor Hetzner

```bash
# 1. Verificar que Odoo 18 está corriendo en el servidor
curl http://localhost:8069/web/health

# 2. Verificar que la BD de producción REDLMC existe
psql -U odoo -h localhost -c "\l" | grep redlmc
```

### FASE 2 — Copiar el módulo al servidor

```bash
# Desde Windows, subir el módulo al servidor por SCP:
scp -r "D:\Odoo-Proyect\odoo-redlmc\addons\redlmc_es_labels" \
    usuario@hetzner-ip:/opt/odoo/addons/

# O si usas Git (recomendado):
# El módulo debe estar en el repositorio de módulos de REDLMC
git clone https://github.com/redlmc/odoo-modules /opt/odoo/addons
```

### FASE 3 — Verificar que la ruta está en addons_path

En el `odoo.conf` del servidor Hetzner, verificar que la ruta de addons incluye `/opt/odoo/addons`:

```ini
[options]
addons_path = /opt/odoo/addons,/usr/lib/python3/dist-packages/odoo/addons
```

### FASE 4 — Instalar el módulo en producción

```bash
# Opción A: Con el servidor parado (más seguro para primera instalación)
sudo systemctl stop odoo

odoo -d odoo_redlmc_produccion \
     --init=redlmc_es_labels \
     --stop-after-init \
     --no-http \
     --config=/etc/odoo/odoo.conf

sudo systemctl start odoo

# Opción B: Con el servidor corriendo (solo si ya está instalado y actualizas)
odoo -d odoo_redlmc_produccion \
     --update=redlmc_es_labels \
     --stop-after-init \
     --no-http \
     --config=/etc/odoo/odoo.conf
```

### FASE 5 — Verificar la instalación

```bash
# Comprobar que el módulo aparece como instalado en la BD
psql -U odoo -d odoo_redlmc_produccion -c \
  "SELECT name, state, latest_version FROM ir_module_module 
   WHERE name = 'redlmc_es_labels';"

# Resultado esperado:
#       name        |  state    | latest_version
# ------------------+-----------+----------------
#  redlmc_es_labels | installed | 18.0.1.0.0
```

### FASE 6 — Verificar visualmente

```
1. Acceder al Odoo del servidor
2. Ir a: Compras → Proveedores → Nuevo proveedor
3. En el campo "Tipo de entidad" verificar que aparece:
   ✅ "Persona Física"  (no "Individuo")
   ✅ "Empresa"         (no "Compañía")
```

---

## 🔄 Si actualizas el módulo en local y quieres llevar los cambios al servidor

### ¿Cuándo necesitas `--update` vs `--init`?

| Situación | Comando |
|---|---|
| Primera instalación en el servidor | `--init=redlmc_es_labels` |
| Ya instalado y cambias el código Python/XML | `--update=redlmc_es_labels` |
| Cambias la versión en `__manifest__.py` | `--update=redlmc_es_labels` (ejecuta migraciones) |

### Flujo completo de actualización

```
[LOCAL] Modificas el código
     ↓
[LOCAL] Pruebas con --update en odoo_redlmc_v2
     ↓
[LOCAL] Si todo ok → subir version en __manifest__.py
        (ej: 18.0.1.0.0 → 18.0.1.1.0)
     ↓
[LOCAL] Commit y push al repositorio Git
     ↓
[SERVIDOR] git pull en /opt/odoo/addons/
     ↓
[SERVIDOR] odoo -d produccion --update=redlmc_es_labels --stop-after-init
     ↓
[SERVIDOR] systemctl restart odoo
     ↓
✅ Cambio aplicado en producción
```

---

## 📌 Reglas de versionado del módulo

El número de versión en `__manifest__.py` sigue el formato:  
**`18.0.X.Y.Z`** donde:
- `18.0` = versión de Odoo (no cambiar)
- `X` = cambio mayor (nueva funcionalidad importante)
- `Y` = cambio menor (mejora o campo nuevo)
- `Z` = bugfix (corrección sin cambio de estructura)

| Tipo de cambio | Ejemplo | Incrementa |
|---|---|---|
| Corrección de texto | Cambiar etiqueta | `Z` (18.0.1.0.**1**) |
| Nuevo campo en `res.partner` | Añadir `nif_type` | `Y` (18.0.1.**1**.0) |
| Nuevo modelo propio | Crear `redlmc.entidad` | `X` (18.0.**2**.0.0) |

**Regla de oro:** Si cambias `X` o `Y`, crea un script de migración en `migrations/`.

---

## 🗺️ Dependencias del módulo

```
redlmc_es_labels
├── Depende de: base, contacts
├── Hereda: res.partner (_inherit)
├── Crea tablas: NINGUNA
└── Instancias donde debe instalarse:
    ✅ odoo_redlmc_v2 (REDLMC SL — YA INSTALADO en local)
    ⏳ odoo_redlmc_produccion (Hetzner — PENDIENTE)
    ❌ premiosred_dev (PremiosRed — no aplica, tiene su propia instancia)
```

---

## 📞 Contacto técnico

- **Desarrollador:** REDLMC SL / Arqvi Dev
- **Vault:** `80-TECNOLOGIA/80.19 ODOO-Modulos-REDLMC.md`
- **Instancia local:** http://localhost:8001

---
*Documento generado: 2026-05-11 | Versión del módulo: 18.0.1.0.0*
