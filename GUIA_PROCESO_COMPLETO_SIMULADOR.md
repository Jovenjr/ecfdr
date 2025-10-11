# 🎯 GUÍA COMPLETA: Proceso End-to-End con Simulador DGII

**Fecha:** 10 de octubre de 2025  
**Objetivo:** Demostrar flujo completo desde crear factura hasta generar reportes usando el simulador DGII  
**Tiempo estimado:** 15-20 minutos

---

## 📋 PREREQUISITOS

Antes de comenzar, verifica:

✅ **Frontend corriendo:**
```bash
cd c:\Users\joven\erpnext-dev\Frontend_custom
npm run dev
# ➜ Local: http://localhost:5173/
```

✅ **Backend ERPNext corriendo:**
- Container Docker: `erpnext-backend-1`
- Puerto: 8000
- Módulo `csf_do` instalado

✅ **Simulador activado:**
- `api_mode = "simulator"` (default)
- No necesita certificado ni credenciales

---

## 🚀 PROCESO COMPLETO (10 PASOS)

###  **PASO 1: Abrir Frontend**

1. Navegar a: **http://localhost:5173**
2. Login con credenciales (si es necesario)
3. Verás el Dashboard principal

**Screenshot esperado:**
- Dashboard con métricas
- Sidebar con módulos
- "Gestión DGII" visible en Contabilidad

---

### **PASO 2: Crear Nueva Factura**

#### 2.1 Navegar a Facturas:
```
Sidebar → Contabilidad → Facturas de Venta
O directamente: http://localhost:5173/facturacion
```

#### 2.2 Click en "Nueva Factura"

#### 2.3 Completar Formulario:

**Cliente:** Seleccionar "Acme Corp SRL" (o crear nuevo)
```
RNC: 131793916
Nombre: Acme Corp SRL
Tipo: Company
```

**Fechas:**
- Fecha: Hoy (10/10/2025)
- Vencimiento: 30 días después

**Artículos:** Agregar al menos 1 item
```
Artículo: SRV-CONSULTORIA (o crear nuevo)
Descripción: Servicios de Consultoría
Cantidad: 2
Precio Unitario: RD$ 50,000.00
```

**Totales calculados automáticamente:**
```
Subtotal: RD$ 100,000.00
ITBIS (18%): RD$ 18,000.00
Total: RD$ 118,000.00
```

#### 2.4 Click "Crear Factura"

**Resultado esperado:**
- Factura creada con número: `ACC-SINV-2025-00XXX`
- Estado: "Borrador" o "Pendiente"
- Aparece en tabla de facturas

---

### **PASO 3: Ver Factura en Tabla**

Después de crear, deberías ver:

```
┌────────────────────────────────────────────────────────────────────────┐
│ # │ Número        │ Cliente      │ Fecha      │ Estado  │ e-CF DGII │ Total      │
├────────────────────────────────────────────────────────────────────────┤
│ ✓ │ ACC-SINV-00XX │ Acme Corp    │ 10/10/2025 │ Borrador│ Sin Enviar│ RD$118,000 │
└────────────────────────────────────────────────────────────────────────┘
```

**Columna "e-CF DGII":**
- Badge: ⚪ **Sin Enviar** (gris)
- Indica que no se ha generado ni enviado e-CF

---

### **PASO 4: Generar y Enviar e-CF a DGII (Simulador)**

#### 4.1 Abrir Menú de Acciones:

Click en "⋮" (tres puntos) al final de la fila

**Menú desplegable:**
```
👁️  Ver Factura
✏️  Editar Factura
💰 Registrar Pago
─────────────────────
📤 Enviar e-CF a DGII        ← NUEVA ACCIÓN
🔄 Consultar Estado e-CF      ← NUEVA ACCIÓN
📥 Descargar XML              ← NUEVA ACCIÓN
📑 Descargar PDF              ← NUEVA ACCIÓN
─────────────────────
🗑️  Eliminar Factura
```

#### 4.2 Click en "📤 Enviar e-CF a DGII"

**Lo que sucede internamente:**

1. **Frontend llama:**
   ```typescript
   const result = await endpoints.regional.dgiiDominican.sendToDGII(invoice.name);
   ```

2. **Backend ejecuta:**
   ```python
   # 1. Generar XML e-CF 4.3
   xml = generate_ecf_from_sales_invoice("ACC-SINV-00XX")
   
   # 2. Firmar digitalmente (simulado con SHA-256)
   signed_xml = sign_xml(xml, cert_path, key_path)
   
   # 3. Enviar a simulador DGII
   from csf_do.csf_do.integrations.dgii_simulator import enviar_ecf_simulado
   result = enviar_ecf_simulado(signed_xml, "32", "B0100000456")
   ```

3. **Simulador responde:**
   ```python
   {
       "success": True,
       "track_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
       "codigo": "200",
       "mensaje": "e-CF recibido correctamente",
       "fecha_recepcion": "2025-10-10T10:30:00.000Z",
       "ncf": "B0100000456"
   }
   ```

4. **Frontend muestra Toast:**
   ```
   ╔═══════════════════════════════════════╗
   ║ ✅ e-CF Enviado a DGII                ║
   ║ Factura ACC-SINV-00XX enviada         ║
   ║ exitosamente                          ║
   ╚═══════════════════════════════════════╝
   ```

5. **Badge se actualiza automáticamente:**
   - Antes: ⚪ Sin Enviar
   - **Después: 🟡 Enviado** (amarillo)

**Logs del simulador (backend):**
```
[DGII Simulator] Iniciando envío e-CF - NCF: B0100000456, Tipo: 32
[DGII Simulator] Escenario configurado: success
[DGII Simulator] Generando respuesta exitosa - Track ID: a1b2c3d4...
[DGII Simulator] Resultado: ÉXITO - Código: 200
```

---

### **PASO 5: Consultar Estado del e-CF**

Espera 10-30 segundos para ver la progresión de estados del simulador.

#### 5.1 Click nuevamente en "⋮" → "🔄 Consultar Estado e-CF"

**Primera consulta (0-10 segundos):**
```
╔═══════════════════════════════════════╗
║ ℹ️ Estado e-CF                         ║
║ Estado actual: RECIBIDO               ║
║ Track ID: a1b2c3d4...                 ║
╚═══════════════════════════════════════╝
```

**Segunda consulta (10-30 segundos):**
```
╔═══════════════════════════════════════╗
║ ℹ️ Estado e-CF                         ║
║ Estado actual: EN_PROCESO             ║
║ DGII está validando el e-CF           ║
╚═══════════════════════════════════════╝
```

**Tercera consulta (30+ segundos):**
```
╔═══════════════════════════════════════╗
║ ℹ️ Estado e-CF                         ║
║ Estado actual: ACEPTADO               ║
║ e-CF aprobado por DGII                ║
╚═══════════════════════════════════════╝
```

**Badge se actualiza:**
- De: 🟡 Enviado
- **A: 🟢 Aceptado** (verde)

**Progresión temporal del simulador:**
```
0-10s    → RECIBIDO (e-CF en cola)
10-30s   → EN_PROCESO (validando)
30s+     → ACEPTADO (95% probabilidad) o RECHAZADO (5%)
```

---

### **PASO 6: Descargar XML y PDF**

Una vez el e-CF está aceptado:

#### 6.1 Descargar XML:
Click "⋮" → "📥 Descargar XML"

**Archivo descargado:**
```
ecf_ACC-SINV-2025-00XX.xml
```

**Contenido (ejemplo):**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<ECF xmlns="http://dgii.gov.do/ecf/v1.0">
    <Encabezado>
        <Version>4.3</Version>
        <IdDoc>
            <TipoeCF>32</TipoeCF>
            <eNCF>B0100000456</eNCF>
            <FechaEmision>2025-10-10</FechaEmision>
        </IdDoc>
        <Emisor>
            <RNCEmisor>131793916</RNCEmisor>
            <RazonSocialEmisor>AI Studio RD</RazonSocialEmisor>
        </Emisor>
        <Comprador>
            <RNCComprador>131793916</RNCComprador>
            <RazonSocialComprador>Acme Corp SRL</RazonSocialComprador>
        </Comprador>
        <Totales>
            <MontoTotal>118000.00</MontoTotal>
            <MontoGravado>100000.00</MontoGravado>
            <ITBIS1>18000.00</ITBIS1>
        </Totales>
    </Encabezado>
    <Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
        <SignatureValue>SIMULADO_SHA256_HASH...</SignatureValue>
    </Signature>
</ECF>
```

#### 6.2 Descargar PDF:
Click "⋮" → "📑 Descargar PDF"

**Archivo descargado:**
```
ecf_ACC-SINV-2025-00XX.pdf
```

**Toast de confirmación:**
```
╔═══════════════════════════════════════╗
║ 📥 Descarga Iniciada                  ║
║ Archivo: ecf_ACC-SINV-2025-00XX.pdf   ║
╚═══════════════════════════════════════╝
```

---

### **PASO 7: Verificar en Tab Emisión e-CF**

#### 7.1 Navegar a DGII.tsx:
```
Sidebar → Contabilidad → Gestión DGII
```

#### 7.2 Tab "Emisión e-CF"

Deberías ver dos secciones:

**Sección 1: Facturas Pendientes de Envío**
```
┌─────────────────────────────────────────────────┐
│ 📋 SINV-00124                [NCF: B0100000457] │
│ Cliente: Tech Solutions SA                      │
│ Monto: RD$ 89,450.00                           │
│ Fecha: 10 oct 2025                             │
│ Estado: [🟡 Pendiente]                          │
│                                                 │
│ [Generar]  [Enviar a DGII]  [Ver en ERPNext ↗] │
└─────────────────────────────────────────────────┘
```

**Sección 2: e-CF Enviados a DGII**
```
┌─────────────────────────────────────────────────┐
│ 📋 ACC-SINV-00XX          [NCF: B0100000456]   │
│ Cliente: Acme Corp SRL                          │
│ Monto: RD$ 118,000.00                          │
│ Track ID: a1b2c3d4-e5f6-7890...                │
│ Estado: [🟢 Aceptado]                           │
│                                                 │
│ [Consultar]  [Ver XML]  [Descargar PDF]       │
└─────────────────────────────────────────────────┘
```

---

### **PASO 8: Filtrar por Estado e-CF**

Vuelve a la página de Facturas:
```
http://localhost:5173/facturacion
```

#### 8.1 Usar Filtro de Estado e-CF:

**Selector de filtro:**
```
┌──────────────────────────────────┐
│ Estado e-CF: [▼ Todos e-CF]      │
├──────────────────────────────────┤
│ ○ Todos e-CF                     │
│ ○ Sin Enviar                     │
│ ○ Borrador                       │
│ ○ Enviado                        │
│ ● Aceptado        ← Seleccionar  │
│ ○ Rechazado                      │
└──────────────────────────────────┘
```

#### 8.2 Resultado:

Solo se muestran facturas con estado "Aceptado":
```
┌────────────────────────────────────────────────────────┐
│ ACC-SINV-00XX │ Acme Corp │ ... │ [🟢 Aceptado] │ ... │
└────────────────────────────────────────────────────────┘
```

#### 8.3 Click "Limpiar" para resetear filtros

---

### **PASO 9: Generar Reporte 607 (Ventas)**

#### 9.1 Navegar a Reportes DGII:
```
Gestión DGII → Tab "Reportes"
```

#### 9.2 Configurar Reporte 607:

**Card de Reporte 607:**
```
┌─────────────────────────────────────────┐
│ 📊 Reporte 607                          │
│ Ventas de Bienes y Servicios           │
│                                         │
│ Empresa:  [▼ AI Studio RD]             │
│ Mes:      [▼ 10 - Octubre]             │
│ Año:      [▼ 2025]                     │
│                                         │
│ [📥 Descargar Excel]  [📄 Descargar TXT]│
└─────────────────────────────────────────┘
```

#### 9.3 Click "📄 Descargar TXT"

**Procesando:**
```
╔═══════════════════════════════════════╗
║ ⏳ Generando Reporte 607...           ║
╚═══════════════════════════════════════╝
```

**Archivo generado:**
```
DGII_607_AI_Studio_RD_202510.txt
```

**Contenido (formato DGII):**
```
131793916|02|B01|00000456|10/10/2025|100000.00|18000.00|118000.00|
```

**Toast de éxito:**
```
╔═══════════════════════════════════════╗
║ ✅ Reporte 607 Generado               ║
║ Archivo descargado exitosamente       ║
║ 1 factura incluida                    ║
╚═══════════════════════════════════════╝
```

---

### **PASO 10: Ver Logs del Simulador (Backend)**

#### 10.1 En terminal del backend:

```bash
# Ver logs en tiempo real
docker exec -it erpnext-backend-1 bash
tail -f logs/frappe.log | grep "DGII Simulator"
```

**Salida esperada:**
```
[2025-10-10 10:30:00] INFO [DGII Simulator] Iniciando envío e-CF - NCF: B0100000456, Tipo: 32
[2025-10-10 10:30:00] INFO [DGII Simulator] Escenario configurado: success
[2025-10-10 10:30:00] INFO [DGII Simulator] Generando respuesta exitosa - Track ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
[2025-10-10 10:30:00] INFO [DGII Simulator] Resultado: ÉXITO - Código: 200
[2025-10-10 10:30:15] INFO [DGII Simulator] Consultando estado - Track ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
[2025-10-10 10:30:15] INFO [DGII Simulator] Estado actual: RECIBIDO
[2025-10-10 10:30:35] INFO [DGII Simulator] Consultando estado - Track ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
[2025-10-10 10:30:35] INFO [DGII Simulator] Estado actual: ACEPTADO
```

---

## 📊 RESUMEN DEL FLUJO COMPLETO

```
1. Crear Factura
   ↓
2. Ver en Tabla (Badge: Sin Enviar)
   ↓
3. Enviar e-CF a DGII (Simulador)
   ↓ (genera XML, firma, envía)
   ↓
4. Toast: "e-CF Enviado" (Badge: Enviado)
   ↓ (esperar 10-30s)
   ↓
5. Consultar Estado
   ↓ (RECIBIDO → EN_PROCESO → ACEPTADO)
   ↓
6. Badge: Aceptado (verde)
   ↓
7. Descargar XML/PDF
   ↓
8. Ver en Tab Emisión e-CF
   ↓
9. Filtrar por estado
   ↓
10. Generar Reporte 607
    ↓
11. Verificar en logs del simulador
```

**Tiempo total:** ~5-10 minutos

---

## 🔍 VERIFICACIÓN DE CADA PASO

### ✅ Checklist de Verificación:

- [ ] Frontend cargado en http://localhost:5173
- [ ] Factura creada con cliente y items
- [ ] Factura aparece en tabla
- [ ] Columna "e-CF DGII" visible
- [ ] Badge inicial: "Sin Enviar" (gris)
- [ ] Dropdown menu tiene 4 acciones DGII
- [ ] Click "Enviar e-CF" muestra toast de éxito
- [ ] Badge cambia a "Enviado" (amarillo)
- [ ] Consulta de estado muestra progresión
- [ ] Badge final: "Aceptado" (verde)
- [ ] Descarga de XML funciona
- [ ] Descarga de PDF funciona
- [ ] Factura aparece en Tab Emisión
- [ ] Filtro por estado e-CF funciona
- [ ] Reporte 607 se genera con la factura
- [ ] Logs del simulador se ven en terminal

---

## 🎯 ESCENARIOS DE ERROR (OPCIONAL)

### Escenario 1: Simular Error de Validación

#### 1. Configurar simulador para errores:

```python
# En Frappe Console
from csf_do.csf_do.integrations.dgii_simulator import configurar_escenario

configurar_escenario("envio", "validation_error")
```

#### 2. Intentar enviar otra factura

**Resultado esperado:**
```
╔═══════════════════════════════════════╗
║ ❌ Error al Enviar e-CF                ║
║ DGII_007: Monto total no coincide     ║
║ Campo: MontoTotal                      ║
╚═══════════════════════════════════════╝
```

#### 3. Volver a modo éxito:

```python
configurar_escenario("envio", "success")
```

---

### Escenario 2: Reiniciar Simulador

```python
# En Frappe Console
from csf_do.csf_do.integrations.dgii_simulator import reiniciar_simulador

result = reiniciar_simulador()
# { "success": True, "mensaje": "Simulador reiniciado, caché limpiada" }
```

**Uso:**
- Limpiar Track IDs anteriores
- Empezar testing con estado limpio
- Resolver inconsistencias

---

## 📚 REFERENCIAS

### Documentación:
- `MEJORAS_SIMULADOR_DGII.md` - Mejoras recientes al simulador
- `COMPARACION_SIMULADOR_VS_REAL.md` - Simulador vs API real
- `QUE_VER_EN_EL_FRONTEND.md` - Guía visual del frontend
- `INTEGRACION_ECF_FACTURACION.md` - Integración en Facturacion.tsx

### Archivos Clave:
- Frontend: `Frontend_custom/src/pages/Facturacion.tsx`
- Backend simulador: `csf_do/csf_do/integrations/dgii_simulator.py`
- API layer: `Frontend_custom/src/api/modules/regional.ts`

---

## 🎉 CONCLUSIÓN

Has completado el flujo end-to-end completo:

✅ Crear factura → Enviar e-CF → Consultar estado → Descargar archivos → Generar reportes

**Todo usando el simulador DGII** sin conexión real ni credenciales.

**Próximos pasos:**
1. Practicar el flujo varias veces
2. Probar escenarios de error
3. Crear más facturas
4. Generar reportes 606/607
5. Prepararse para migración a producción

---

**Versión:** 1.0  
**Fecha:** 10 de octubre de 2025  
**Estado:** ✅ COMPLETO Y VERIFICADO
