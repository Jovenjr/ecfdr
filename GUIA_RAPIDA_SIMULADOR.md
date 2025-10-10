# 🚀 Guía Rápida - Simulador DGII para Desarrollo

## 📋 Descripción

El simulador DGII te permite desarrollar y probar toda la funcionalidad de facturación electrónica **sin necesidad de conexión real con DGII**. Es perfecto para desarrollo, testing y certificación.

---

## ⚙️ Configuración Inicial

### 1. Configurar el Modo del Simulador

1. Ir a **DGII Configuration** en ERPNext
2. Configurar el campo **Modo API**:
   - `simulator` - Para desarrollo (usa el simulador)
   - `test` - Para certificación con DGII
   - `production` - Para producción real

**Para usar el simulador, selecciona `simulator`**

### 2. Configurar Escenarios de Prueba (Opcional)

1. Ir a **DGII Simulator Config** en ERPNext
2. Configurar escenarios:
   - `scenario_envio`: success, validation_error, timeout, server_error
   - `scenario_consulta`: success, not_found
   - `scenario_acuse`: success, error

---

## 🧪 Cómo Probar la Aplicación

### Opción 1: Ejecutar Script de Prueba Automático

```powershell
# Dentro del directorio del proyecto
python test_simulator_complete.py
```

Este script ejecutará automáticamente:
- ✅ Envío de e-CF
- ✅ Consulta de estado con progresión temporal
- ✅ Generación de e-CF de proveedor
- ✅ Acuse de recibo (ACECFAR)
- ✅ Prueba del cliente DGII

### Opción 2: Probar Manualmente desde ERPNext

#### A. Enviar un e-CF

```python
# En la consola de Frappe (bench console)
from csf_do.csf_do.integrations.dgii_client import get_dgii_client

client = get_dgii_client()

# Enviar e-CF de prueba
result = client.enviar_ecf(
    xml_content="<xml>contenido del e-CF</xml>",
    ecf_type="31",
    ncf="B0100000001"
)

print(result)
# Salida:
# {
#   "success": True,
#   "track_id": "abc-123-def-456",
#   "mensaje": "e-CF recibido correctamente"
# }
```

#### B. Consultar Estado

```python
# Usando el track_id del paso anterior
track_id = result["track_id"]

# Consultar inmediatamente (RECIBIDO)
estado1 = client.consultar_estado(track_id)
print(f"Estado: {estado1['estado']}")  # RECIBIDO

# Esperar 12 segundos y consultar (EN_PROCESO)
import time
time.sleep(12)
estado2 = client.consultar_estado(track_id)
print(f"Estado: {estado2['estado']}")  # EN_PROCESO

# Esperar 20 segundos más (ACEPTADO/RECHAZADO)
time.sleep(20)
estado3 = client.consultar_estado(track_id)
print(f"Estado: {estado3['estado']}")  # ACEPTADO o RECHAZADO
```

#### C. Generar e-CF de Proveedor (para ACECFAR)

```python
from csf_do.csf_do.integrations.dgii_simulator import DGIISimulator

simulator = DGIISimulator()

# Generar e-CF de un proveedor
xml = simulator.generar_ecf_proveedor(
    supplier_rnc="131793916",
    amount=11800.00  # RD$ 11,800
)

# Guardar el XML
with open("ecf_proveedor.xml", "w", encoding="utf-8") as f:
    f.write(xml)

print("e-CF de proveedor generado: ecf_proveedor.xml")
```

#### D. Enviar Acuse de Recibo

```python
# Enviar acuse de recibo
acuse = client.enviar_acuse_recibo(
    track_id="track-id-del-ecf-recibido",
    estado="ACEPTADO",
    motivo=""  # Solo si es RECHAZADO
)

print(acuse)
```

---

## 📊 Progresión de Estados del Simulador

El simulador simula la progresión temporal real de DGII:

| Tiempo | Estado | Descripción |
|--------|--------|-------------|
| 0-10 seg | **RECIBIDO** | e-CF recibido, en cola de procesamiento |
| 10-30 seg | **EN_PROCESO** | e-CF en proceso de validación |
| 30+ seg | **ACEPTADO** (95%) o **RECHAZADO** (5%) | Estado final |

---

## 🎯 Flujo de Trabajo Típico

### 1. Crear una Factura de Venta

1. Ir a **Sales Invoice** en ERPNext
2. Crear una nueva factura
3. Completar datos del cliente (debe tener RNC/Cédula)
4. Agregar items
5. Guardar y enviar (Submit)

### 2. El Sistema Automáticamente:

- ✅ Genera el XML del e-CF
- ✅ Firma digitalmente el e-CF
- ✅ Lo envía a DGII (o al simulador)
- ✅ Registra el Track ID
- ✅ Consulta el estado periódicamente

### 3. Verificar el Estado

1. Ir a **e-CF** (DocType de e-CF)
2. Ver el documento creado
3. Campo `estado_dgii` mostrará: Pendiente → En Proceso → Aceptado/Rechazado

### 4. Para Facturas de Compra (ACECFAR)

1. Generar un e-CF de proveedor usando el simulador
2. El sistema automáticamente:
   - Valida la firma
   - Crea el Supplier si no existe
   - Crea la Purchase Invoice
   - Envía acuse de recibo

---

## 🔧 Comandos Útiles

### Ejecutar Pruebas Unitarias

```powershell
# Todas las pruebas
bench --site [tu-sitio] run-tests --app csf_do

# Solo pruebas del simulador
bench --site [tu-sitio] run-tests csf_do.csf_do.tests.test_dgii_simulator

# Solo pruebas de ACECFAR
bench --site [tu-sitio] run-tests csf_do.csf_do.tests.test_acecfar
```

### Limpiar Cache del Simulador

```python
# En bench console
import frappe
frappe.cache().delete_keys("dgii_simulator_*")
```

### Verificar Configuración

```python
# En bench console
from csf_do.csf_do.integrations.dgii_client import get_dgii_client

client = get_dgii_client()
info = client.get_info()
print(info)

# Salida:
# {
#   "modo": "simulator",
#   "url_api": "http://localhost:8000/dgii/api",
#   "rnc_empresa": "...",
#   "simulador_activo": True
# }
```

---

## 📁 Archivos Importantes

### Módulos del Simulador
- `csf_do/csf_do/integrations/dgii_simulator.py` - Simulador principal
- `csf_do/csf_do/integrations/dgii_client.py` - Cliente unificado
- `csf_do/csf_do/doctype/dgii_simulator_config/` - Configuración UI

### Módulos ACECFAR
- `csf_do/csf_do/utils/acecfar_parser.py` - Parser de XML
- `csf_do/csf_do/utils/signature_validator.py` - Validador de firma
- `csf_do/csf_do/integrations/acecfar_processor.py` - Procesador

### Pruebas
- `csf_do/csf_do/tests/test_dgii_simulator.py` - Pruebas unitarias
- `csf_do/csf_do/tests/test_acecfar.py` - Pruebas ACECFAR
- `test_simulator_complete.py` - Pruebas de integración

### Documentación
- `csf_do/docs/SIMULADOR_DGII.md` - Documentación completa
- `csf_do/docs/MODULO_ACECFAR.md` - Documentación ACECFAR
- `RESUMEN_SIMULADOR.md` - Resumen de implementación

---

## ⚡ Solución de Problemas

### Error: "DGII Configuration not found"

**Solución:**
1. Ir a **DGII Configuration**
2. Completar los campos obligatorios:
   - RNC Emisor
   - Versión e-CF
   - Modo API: `simulator`
3. Guardar

### Error: "Simulador no está activo"

**Solución:**
- Verificar que `api_mode` = `simulator` en DGII Configuration
- Reiniciar el servidor: `bench restart`

### Las consultas de estado no cambian

**Solución:**
- El simulador simula progresión temporal
- Esperar al menos 30 segundos para ver ACEPTADO/RECHAZADO
- O limpiar cache: `frappe.cache().delete_keys("dgii_simulator_*")`

### No se crean Purchase Invoices desde e-CF

**Solución:**
1. Verificar que el proveedor existe o se puede crear automáticamente
2. Verificar que los items existen o están configurados para crearse
3. Revisar logs: `bench --site [tu-sitio] doctor` o ver Error Log en ERPNext

---

## 🎓 Próximos Pasos

### Para Desarrollo
1. ✅ Configurar simulador (modo `simulator`)
2. ✅ Ejecutar `test_simulator_complete.py`
3. ✅ Crear facturas de prueba
4. ✅ Verificar generación de XML
5. ✅ Probar ACECFAR con e-CF de proveedor

### Para Certificación con DGII
1. Cambiar modo a `test`
2. Configurar certificado digital real
3. Configurar credenciales DGII
4. Ejecutar set de pruebas de DGII
5. Enviar declaración jurada

### Para Producción
1. Cambiar modo a `production`
2. Configurar certificado de producción
3. Configurar URLs de producción
4. Habilitar monitoreo y alertas
5. Plan de contingencia (Serie B)

---

## 📞 Soporte

- **Documentación completa:** Ver `csf_do/docs/`
- **Código fuente:** `csf_do/csf_do/integrations/`
- **Pruebas:** `csf_do/csf_do/tests/`
- **Issues:** Reportar en el repositorio del proyecto

---

## ✅ Checklist de Verificación

Antes de pasar a producción, verifica:

- [ ] Simulador funciona correctamente
- [ ] Envío de e-CF exitoso
- [ ] Consulta de estado funciona
- [ ] ACECFAR procesa e-CF de proveedores
- [ ] Purchase Invoices se crean automáticamente
- [ ] Firma digital funciona (modo test)
- [ ] Certificado digital válido
- [ ] Todos los tests unitarios pasan
- [ ] Documentación actualizada
- [ ] Plan de contingencia documentado

---

**¡Listo para probar! 🚀**

El simulador está completamente funcional y listo para usar. Cualquier duda, consulta la documentación completa en `csf_do/docs/SIMULADOR_DGII.md`.
