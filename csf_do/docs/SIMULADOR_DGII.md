# Simulador DGII - Guía de Uso

## Descripción

El **Simulador DGII** es una herramienta de desarrollo que replica el comportamiento de la API real de DGII sin necesidad de conexión real. Permite desarrollar, probar y validar toda la funcionalidad de facturación electrónica antes de conectar con el ambiente real de DGII.

## Características

✅ **Envío de e-CF simulado** con generación de Track ID  
✅ **Consulta de estado** con progresión temporal realista  
✅ **Acuse de recibo (ACECFAR)** para e-CF recibidos  
✅ **Generación de e-CF de proveedores** para testing  
✅ **Múltiples escenarios** (éxito, errores, timeouts)  
✅ **Cambio transparente** entre simulador y API real  
✅ **Estadísticas y monitoreo** de operaciones  

---

## Instalación y Configuración

### 1. Activar el Simulador

El simulador se activa automáticamente en modo desarrollo. Para configurarlo manualmente:

1. Ir a **DGII Settings**
2. Configurar el campo `api_mode`:
   - `simulator` - Usa el simulador (desarrollo)
   - `test` - Usa ambiente de pruebas DGII
   - `production` - Usa ambiente de producción DGII

### 2. Configurar Escenarios

Ir a **DGII Simulator Config** para configurar diferentes escenarios:

#### Escenarios de Envío:
- **success** - Envío exitoso (por defecto)
- **validation_error** - Error de validación
- **timeout** - Timeout de conexión
- **server_error** - Error del servidor

#### Escenarios de Consulta:
- **success** - Consulta exitosa
- **not_found** - Track ID no encontrado
- **timeout** - Timeout

#### Escenarios de Acuse:
- **success** - Acuse exitoso
- **error** - Error al enviar acuse

---

## Uso Básico

### Enviar un e-CF

```python
from csf_do.csf_do.integrations.dgii_client import get_dgii_client

# Obtener cliente (usa simulador automáticamente si está configurado)
client = get_dgii_client()

# Enviar e-CF
result = client.enviar_ecf(
    xml_content="<ECF>...</ECF>",
    ecf_type="31",
    ncf="B0100000001"
)

if result.get("success"):
    track_id = result.get("track_id")
    print(f"e-CF enviado exitosamente. Track ID: {track_id}")
else:
    print(f"Error: {result.get('mensaje')}")
```

### Consultar Estado

```python
# Consultar estado de un e-CF enviado
result = client.consultar_estado(track_id="abc-123-def")

if result.get("success"):
    estado = result.get("estado")
    print(f"Estado: {estado}")
    # Estados posibles: RECIBIDO, EN_PROCESO, ACEPTADO, RECHAZADO
```

### Enviar Acuse de Recibo

```python
# Enviar acuse de recibo de un e-CF recibido
result = client.enviar_acuse_recibo(
    track_id="xyz-789",
    estado="ACEPTADO",
    motivo=""  # Solo si es RECHAZADO
)
```

---

## Progresión de Estados

El simulador replica la progresión temporal de estados de DGII:

```
RECIBIDO (0-10 seg) → EN_PROCESO (10-30 seg) → ACEPTADO/RECHAZADO (30+ seg)
```

- **RECIBIDO**: e-CF recibido, en cola de procesamiento
- **EN_PROCESO**: e-CF en proceso de validación
- **ACEPTADO**: e-CF aceptado por DGII (95% de casos)
- **RECHAZADO**: e-CF rechazado (5% de casos, aleatorio)

---

## Generar e-CF de Prueba

Para testing del módulo ACECFAR (recepción de e-CF):

```python
from csf_do.csf_do.integrations.dgii_simulator import DGIISimulator

simulator = DGIISimulator()

# Generar e-CF de un proveedor
xml = simulator.generar_ecf_proveedor(
    supplier_rnc="131793916",
    amount=11800.00  # Incluye ITBIS
)

# Usar este XML para probar recepción
```

---

## Cambiar entre Simulador y API Real

El cambio es **completamente transparente**. Solo necesitas cambiar la configuración:

### Opción 1: Desde DGII Settings

```python
settings = frappe.get_single("DGII Settings")
settings.api_mode = "production"  # o "test" o "simulator"
settings.save()
```

### Opción 2: Desde la interfaz

1. Ir a **DGII Settings**
2. Cambiar el campo **API Mode**
3. Guardar

**Todo el código sigue funcionando igual**, el cliente detecta automáticamente el modo y usa la implementación correcta.

---

## Testing

### Ejecutar Tests del Simulador

```bash
# Ejecutar todos los tests
cd /path/to/frappe-bench
bench --site [site-name] run-tests csf_do.csf_do.tests.test_dgii_simulator

# Ejecutar test específico
bench --site [site-name] run-tests csf_do.csf_do.tests.test_dgii_simulator.TestDGIISimulator.test_envio_exitoso
```

### Tests Incluidos

- ✅ Inicialización del simulador
- ✅ Envío exitoso de e-CF
- ✅ Consulta de estado
- ✅ Consulta con Track ID inexistente
- ✅ Generación de e-CF de proveedor
- ✅ Envío de acuse de recibo
- ✅ Generación de NCF
- ✅ Cliente unificado

---

## API Pública (Whitelisted)

Funciones disponibles desde el frontend:

```javascript
// Enviar e-CF
frappe.call({
    method: 'csf_do.csf_do.integrations.dgii_client.enviar_ecf',
    args: {
        xml_content: xml,
        ecf_type: '31',
        ncf: 'B0100000001'
    },
    callback: function(r) {
        console.log(r.message);
    }
});

// Consultar estado
frappe.call({
    method: 'csf_do.csf_do.integrations.dgii_client.consultar_estado',
    args: {
        track_id: 'abc-123'
    },
    callback: function(r) {
        console.log(r.message);
    }
});

// Probar conexión
frappe.call({
    method: 'csf_do.csf_do.integrations.dgii_client.test_connection',
    callback: function(r) {
        console.log(r.message);
    }
});
```

---

## Arquitectura

```
┌─────────────────────────────────────────┐
│         Tu Código / ERPNext             │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         DGIIClient (Adaptador)          │
│  - Detecta modo (simulator/test/prod)   │
│  - Enruta a implementación correcta     │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
┌─────────────┐  ┌──────────────┐
│  Simulator  │  │   API Real   │
│  (Local)    │  │   (DGII)     │
└─────────────┘  └──────────────┘
```

---

## Ventajas del Simulador

1. **Desarrollo sin conexión**: No necesitas credenciales DGII para desarrollar
2. **Testing rápido**: Respuestas instantáneas, sin latencia de red
3. **Escenarios controlados**: Simula errores y casos edge fácilmente
4. **Sin costos**: No consume cuota de API de DGII
5. **Reproducibilidad**: Mismos resultados en cada ejecución
6. **Debugging fácil**: Logs locales, sin depender de logs de DGII

---

## Limitaciones

⚠️ **El simulador NO valida**:
- Firma digital real (acepta cualquier firma)
- Certificados DGII reales
- Validación XSD completa
- Reglas de negocio específicas de DGII

⚠️ **Para validación real**, debes usar el ambiente de pruebas de DGII.

---

## Migración a Producción

Cuando estés listo para producción:

1. **Obtener certificado digital** autorizado por DGII
2. **Registrar aplicación** en portal DGII
3. **Obtener credenciales** de API (RNC, usuario, contraseña)
4. **Completar certificación** en ambiente de pruebas
5. **Cambiar modo** a `production` en DGII Settings
6. **Configurar URLs** de producción

**El código NO cambia**, solo la configuración.

---

## Troubleshooting

### El simulador no responde

```python
# Verificar que está activo
from csf_do.csf_do.integrations.dgii_simulator import DGIISimulator
simulator = DGIISimulator()
print(simulator.is_simulator_active())  # Debe ser True
```

### Cambiar escenario no funciona

```python
# Limpiar caché
frappe.cache().delete_value("dgii_simulator_*")

# Recargar configuración
frappe.clear_cache()
```

### Track ID no se encuentra

El simulador usa caché con TTL de 24 horas. Si pasó ese tiempo, el Track ID expira.

---

## Próximos Pasos

1. ✅ Simulador básico implementado
2. 🔄 Implementar módulo ACECFAR usando el simulador
3. 🔄 Mejorar validaciones 606/607
4. 🔄 Ampliar suite de tests
5. 🔄 Implementar monitoreo

---

## Soporte

Para reportar bugs o sugerir mejoras del simulador:
- Crear issue en el repositorio
- Contactar al equipo de desarrollo

---

**Última actualización**: 10 de Enero, 2025  
**Versión del simulador**: 1.0.0
