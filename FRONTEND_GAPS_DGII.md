# Análisis de Brechas: Frontend vs Backend DGII

**Fecha:** 2025-10-10  
**Objetivo:** Identificar componentes y funcionalidades faltantes en el frontend React para aprovechar completamente el módulo `csf_do`

---

## 1. ESTADO ACTUAL DEL BACKEND (csf_do)

### ✅ Funcionalidades Implementadas y Desplegadas

#### 1.1 Módulo ACECFAR (Recepción e-CF)
- ✅ Recepción de e-CF de proveedores (XML)
- ✅ Validación de firma digital (modo simulador y real)
- ✅ Generación automática de Purchase Invoice desde e-CF
- ✅ Envío de Acuse de Recibo (ARECF)
- ✅ Gestión de Aprobación/Rechazo Comercial (ACECF)
- ✅ Buzón de recepción (upload XML, email parsing)
- ✅ Estados: RECIBIDO → VALIDADO → PROCESADO → ACEPTADO/RECHAZADO

**APIs Backend:**
```python
# csf_do/csf_do/doctype/acecfar/acecfar.py
@frappe.whitelist()
def receive_ecf_from_supplier(xml_content, source='upload')
def validate_signature(xml_content)
def create_purchase_invoice_from_ecf(ecf_data)
def send_acceptance(acecfar_name)
def send_rejection(acecfar_name, reason)
```

#### 1.2 Emisión e-CF (Ventas)
- ✅ Generación automática de XML desde Sales Invoice
- ✅ Firma digital XML (SHA-256)
- ✅ Envío a DGII (3 modos: simulator, test, production)
- ✅ Consulta de estado con progresión temporal
- ✅ Descarga de XML firmado y PDF
- ✅ Soporte para todos los tipos de NCF (B01, B02, B14, B15, E31-E47)

**APIs Backend:**
```python
# csf_do/utils/ecf_generator.py
@frappe.whitelist()
def generate_ecf_from_sales_invoice(sales_invoice_name)
def send_to_dgii(ecf_name)
def query_ecf_status(track_id)
def download_ecf_xml(ecf_name)
def download_ecf_pdf(ecf_name)
```

#### 1.3 Validadores Fiscales
- ✅ Validación RNC (Módulo 11 para RNC 9 dígitos, Luhn para cédula 11 dígitos)
- ✅ Validación NCF (formato y secuencia)
- ✅ Cálculo ITBIS con tolerancia (18%)
- ✅ Validación de Customer RNC

**APIs Backend:**
```python
# csf_do/utils/validators.py
@frappe.whitelist()
def check_rnc(rnc)
def check_ncf(ncf)
def calculate_itbis(amount, rate=18)
def validate_customer_rnc(customer)
```

#### 1.4 Dashboard DGII
- ✅ Métricas generales (e-CF emitidos, NCF disponibles, series activas)
- ✅ Lista de series NCF con % uso y alertas de vencimiento
- ✅ Últimos e-CF emitidos

**APIs Backend:**
```python
# csf_do/csf_do/page/dgii_dashboard/dgii_dashboard.py
@frappe.whitelist()
def get_dashboard_data()
def get_ncf_series_list(filters)
def get_recent_ecf(limit=10)
```

#### 1.5 Reportes DGII
- ✅ Reporte 606 (Compras)
- ✅ Reporte 607 (Ventas)
- ✅ Reporte 608 (Cancelaciones)
- ✅ Reporte IT-1 (Declaración Jurada)
- ✅ Exportación a Excel/TXT

**APIs Backend:**
```python
# csf_do/csf_do/report/
@frappe.whitelist()
def generate_606(filters)
def generate_607(filters)
def generate_608(filters)
# Via Query Report
frappe.desk.query_report.run('IT-1 Declaración Jurada', filters)
```

#### 1.6 Gestión NCF Series
- ✅ CRUD completo de NCF Series
- ✅ Control de secuencia automática
- ✅ Alertas de vencimiento (30 días)
- ✅ Alertas de agotamiento (80% uso)
- ✅ Validación de rangos autorizados

**APIs Backend:**
```python
# /api/resource/NCF Series (REST API)
GET /api/resource/NCF Series
POST /api/resource/NCF Series
PUT /api/resource/NCF Series/{name}
DELETE /api/resource/NCF Series/{name}
```

#### 1.7 Configuración DGII
- ✅ DGII Configuration DocType (consolidado)
- ✅ Almacenamiento de certificado digital (.p12/.pfx)
- ✅ Configuración de API mode (simulator/test/production)
- ✅ Credenciales DGII (RNC, usuario, contraseña)
- ✅ Información fiscal (representante legal, teléfono, dirección)

**APIs Backend:**
```python
# /api/resource/DGII Configuration
GET /api/resource/DGII Configuration/DGII Configuration
PUT /api/resource/DGII Configuration/DGII Configuration
```

#### 1.8 Simulador DGII Local
- ✅ API local completa que simula DGII
- ✅ Generación de Track IDs
- ✅ Progresión de estados temporal (RECIBIDO → ACEPTADO)
- ✅ Simulación de errores y rechazos
- ✅ Generación de XML de proveedor para pruebas

**APIs Backend:**
```python
# csf_do/integrations/dgii_simulator.py
@frappe.whitelist()
def simulate_send_ecf(xml_content)
def simulate_query_status(track_id)
def generate_supplier_ecf(supplier_data)
```

---

## 2. ESTADO ACTUAL DEL FRONTEND

### ✅ Componentes Implementados

#### 2.1 Página DGII.tsx (Nueva - Recién Creada)
**Ubicación:** `src/pages/DGII.tsx`

**Tabs Implementadas:**
1. **Reportes** ✅
   - Métricas dashboard (e-CF count, NCF disponibles, series activas)
   - Lista de e-CF recientes
   - Botones para generar reportes (sin implementación real aún)

2. **Series NCF** ✅
   - Lista de series con estado, rango, disponibles
   - Barra de progreso de uso
   - Alertas de vencimiento

3. **Configuración** ✅
   - Visualización de DGII Configuration (RNC, nombre comercial, representante legal)
   - Botón para editar (redirige a Frappe)

4. **Validaciones** ✅
   - Validar RNC/Cédula
   - Validar NCF
   - Calcular ITBIS

**Queries Implementadas:**
```typescript
useQuery(['dgii-dashboard']) → getDashboardData()
useQuery(['dgii-ncf-series']) → getNCFSeriesList()
useQuery(['dgii-recent-ecf']) → getRecentECF(10)
useQuery(['dgii-configuration']) → getConfiguration()
```

**Mutations Implementadas:**
```typescript
validateRNCMutation → validateRNC(rnc)
validateNCFMutation → validateNCF(ncf)
calculateITBISMutation → calculateITBIS(amount, rate)
```

#### 2.2 API Module (regional.ts)
**Ubicación:** `src/api/modules/regional.ts`

**Métodos Implementados:**
- ✅ getConfiguration() / updateConfiguration()
- ✅ validateRNC() / validateNCF() / calculateITBIS() / validateCustomerRNC()
- ✅ getNCFSeries() / getNCFSeriesByCompany() / getNCFSeriesByType()
- ✅ createNCFSeries() / updateNCFSeries()
- ✅ getDashboardData() / getNCFSeriesList() / getRecentECF()
- ✅ generate606() / generate607() / generate608() / runIT1Report()

---

## 3. BRECHAS IDENTIFICADAS (GAPS)

### ❌ 3.1 MÓDULO ACECFAR (Recepción e-CF) - FALTANTE COMPLETO

**Impacto:** 🔴 CRÍTICO - Es el 50% de la funcionalidad e-CF (Recepción)

**Componentes Faltantes:**

#### A. Tab "Recepción e-CF" en página DGII
- ❌ Buzón de recepción de e-CF
- ❌ Upload de XML de proveedores
- ❌ Lista de ACECFAR recibidos con estados
- ❌ Botón "Validar Firma Digital"
- ❌ Botón "Procesar e-CF" (crear Purchase Invoice)
- ❌ Botón "Enviar Acuse de Recibo"
- ❌ Botón "Aprobar/Rechazar Comercialmente"
- ❌ Visualizador de XML recibido
- ❌ Detalles del e-CF del proveedor

**APIs Backend Disponibles pero NO Consumidas:**
```python
receive_ecf_from_supplier(xml_content, source)  # ❌ No usado
validate_signature(xml_content)                  # ❌ No usado
create_purchase_invoice_from_ecf(ecf_data)       # ❌ No usado
send_acceptance(acecfar_name)                    # ❌ No usado
send_rejection(acecfar_name, reason)             # ❌ No usado
```

**Flujo Completo Faltante:**
```
1. Upload XML → 2. Validar Firma → 3. Crear PI → 4. Enviar ARECF → 5. Aprobar/Rechazar
```

---

### ❌ 3.2 EMISIÓN e-CF (Ventas) - INTEGRACIÓN PARCIAL

**Impacto:** 🟡 ALTO - Funcionalidad core de emisión no integrada

**Componentes Faltantes:**

#### A. Tab "Emisión e-CF" en página DGII
- ❌ Lista de Sales Invoices pendientes de enviar
- ❌ Botón "Generar e-CF" desde factura
- ❌ Botón "Enviar a DGII" (con indicador de modo: simulator/test/production)
- ❌ Consulta de estado de e-CF enviado
- ❌ Visualización de progresión de estados (RECIBIDO → EN_PROCESO → ACEPTADO)
- ❌ Botón "Descargar XML firmado"
- ❌ Botón "Descargar PDF e-CF"
- ❌ Historial de intentos de envío
- ❌ Manejo de errores DGII con reintentos

**APIs Backend Disponibles pero NO Consumidas:**
```python
generate_ecf_from_sales_invoice(sales_invoice_name)  # ❌ No usado
send_to_dgii(ecf_name)                                # ❌ No usado
query_ecf_status(track_id)                            # ❌ No usado
download_ecf_xml(ecf_name)                            # ❌ No usado
download_ecf_pdf(ecf_name)                            # ❌ No usado
```

---

### ❌ 3.3 GESTIÓN DE NCF SERIES - CRUD INCOMPLETO

**Impacto:** 🟡 MEDIO - Visualización OK, pero sin gestión

**Componentes Faltantes:**

#### A. Formulario de Creación de Serie NCF
- ❌ Modal para crear nueva serie
- ❌ Campos: tipo_ncf, serie, desde, hasta, fecha_vencimiento, company
- ❌ Validación de rangos (desde < hasta)
- ❌ Validación de formato de serie (Ej: B0100000001)

#### B. Edición y Eliminación
- ❌ Botón "Editar Serie"
- ❌ Botón "Desactivar/Activar Serie"
- ❌ Modal de confirmación de eliminación

**APIs Backend Disponibles pero NO Consumidas:**
```typescript
createNCFSeries(data)  # ✅ Método existe pero NO hay UI
updateNCFSeries(name, data)  # ✅ Método existe pero NO hay UI
```

---

### ❌ 3.4 REPORTES DGII - GENERACIÓN Y EXPORTACIÓN FALTANTE

**Impacto:** 🟡 MEDIO - Botones existen pero no funcionan

**Componentes Faltantes:**

#### A. Generación de Reportes 606/607/608/IT-1
- ❌ Formulario de filtros (from_date, to_date, company)
- ❌ Selector de formato de exportación (Excel/TXT)
- ❌ Indicador de progreso de generación
- ❌ Descarga automática del archivo
- ❌ Previsualización de datos antes de generar

#### B. Historial de Reportes Generados
- ❌ Lista de reportes previamente generados
- ❌ Metadatos (fecha generación, período, # registros)
- ❌ Botón "Re-descargar" reporte

**APIs Backend Disponibles pero NO Consumidas:**
```typescript
generate606(filters)  # ✅ Método existe pero NO funciona en UI
generate607(filters)  # ✅ Método existe pero NO funciona en UI
generate608(filters)  # ✅ Método existe pero NO funciona en UI
runIT1Report(filters)  # ✅ Método existe pero NO funciona en UI
```

---

### ❌ 3.5 CONFIGURACIÓN DGII - GESTIÓN CERTIFICADO Y MODO API

**Impacto:** 🔴 CRÍTICO - Sin esto no se puede cambiar de simulator a production

**Componentes Faltantes:**

#### A. Gestión de Certificado Digital
- ❌ Upload de archivo .p12 / .pfx
- ❌ Input para contraseña del certificado
- ❌ Validación de certificado (fecha vencimiento, emisor)
- ❌ Indicador de estado del certificado (válido/expirado/próximo a vencer)
- ❌ Botón "Probar Certificado"

#### B. Configuración de Modo API
- ❌ Selector de modo: simulator / test / production
- ❌ Warning al cambiar de modo (especialmente a production)
- ❌ Indicador visual del modo actual (badge destacado)

#### C. Credenciales DGII
- ❌ Input para RNC
- ❌ Input para usuario DGII
- ❌ Input para contraseña DGII (tipo password)
- ❌ Botón "Test Connection" (probar credenciales)

#### D. Información Fiscal
- ❌ Input para representante legal
- ❌ Input para teléfono de contacto
- ❌ Input para dirección fiscal
- ❌ Input para nombre comercial

**API Backend Disponible:**
```typescript
updateConfiguration(data)  # ✅ Existe pero UI solo muestra, no edita
```

---

### ❌ 3.6 SIMULADOR DGII - SIN INTERFAZ DE PRUEBAS

**Impacto:** 🟠 MEDIO - Útil para desarrollo y demos

**Componentes Faltantes:**

#### A. Tab "Simulador de Pruebas"
- ❌ Generador de XML de proveedor (para probar recepción)
- ❌ Formulario con datos del proveedor simulado
- ❌ Botón "Generar XML de Prueba"
- ❌ Descarga del XML generado
- ❌ Consola de logs del simulador
- ❌ Botón "Reset Simulador" (limpiar datos de prueba)

**API Backend Disponible:**
```python
generate_supplier_ecf(supplier_data)  # ❌ No usado
```

---

### ❌ 3.7 MONITOREO Y ALERTAS - DASHBOARD OPERATIVO FALTANTE

**Impacto:** 🟡 MEDIO - Importante para operaciones

**Componentes Faltantes:**

#### A. Tab "Monitoreo Operacional"
- ❌ Gráfico de e-CF enviados por día (últimos 30 días)
- ❌ Tasa de aceptación vs rechazo (%)
- ❌ Tiempo promedio de aprobación DGII
- ❌ Alertas de series próximas a vencer (< 30 días)
- ❌ Alertas de series próximas a agotarse (> 80% uso)
- ❌ Estado de conexión con DGII (ping test)
- ❌ Últimos errores DGII con detalles

---

### ❌ 3.8 INTEGRACIÓN CON FACTURACIÓN EXISTENTE

**Impacto:** 🔴 CRÍTICO - Sin esto el flujo es manual

**Componentes Faltantes:**

#### A. En página Facturacion.tsx
- ❌ Badge de estado e-CF en Sales Invoice (PENDIENTE/ENVIADO/ACEPTADO/RECHAZADO)
- ❌ Botón "Enviar a DGII" en cada factura
- ❌ Botón "Descargar e-CF" (XML + PDF)
- ❌ Columna "Estado DGII" en tabla de facturas
- ❌ Filtro por estado e-CF

#### B. En componentes DGII existentes
- ❌ DGIIValidationButton - está comentado en Facturacion.tsx
- ❌ DGIIStatusBadge - está comentado en Facturacion.tsx
- ❌ ECFGenerator - necesita actualización
- ❌ ECFCertificateManager - necesita implementación completa

**Ubicación:**
```typescript
// src/pages/Facturacion.tsx líneas 1501, 1634
// DGII Validation temporarily disabled
// <DGIIValidationButton ... />
```

---

## 4. PRIORIZACIÓN DE DESARROLLO

### 🔴 FASE 1 - CRÍTICO (Bloqueante para uso básico)

**Prioridad 1:** Emisión e-CF desde Sales Invoice
- [ ] Tab "Emisión e-CF" con lista de facturas
- [ ] Botón "Generar y Enviar e-CF"
- [ ] Consulta de estado con progresión
- [ ] Descarga de XML/PDF
- [ ] Integración en Facturacion.tsx (badges, botones)

**Prioridad 2:** Configuración DGII Completa
- [ ] Formulario de edición de DGII Configuration
- [ ] Upload de certificado digital
- [ ] Selector de modo API (simulator/test/production)
- [ ] Test de conexión DGII

**Prioridad 3:** Recepción e-CF (ACECFAR)
- [ ] Tab "Recepción e-CF"
- [ ] Upload de XML
- [ ] Procesamiento automático a Purchase Invoice
- [ ] Envío de acuses

---

### 🟡 FASE 2 - ALTO (Operación diaria)

**Prioridad 4:** Gestión de NCF Series
- [ ] Formulario de creación de serie
- [ ] Edición y activación/desactivación

**Prioridad 5:** Reportes DGII Funcionales
- [ ] Formularios de filtros
- [ ] Generación y descarga de 606/607/608/IT-1

---

### 🟠 FASE 3 - MEDIO (Mejoras operacionales)

**Prioridad 6:** Monitoreo y Dashboard
- [ ] Gráficos de métricas
- [ ] Alertas proactivas
- [ ] Logs de errores

**Prioridad 7:** Simulador UI
- [ ] Generador de XML de prueba
- [ ] Consola de logs

---

## 5. PLAN DE ACCIÓN INMEDIATO

### Próximos Pasos Recomendados:

1. **Completar DGII.tsx con tabs faltantes:**
   - Agregar tab "Emisión e-CF"
   - Agregar tab "Recepción e-CF"
   - Agregar tab "Monitoreo"

2. **Implementar formularios modales:**
   - Modal NCF Series (crear/editar)
   - Modal Configuración DGII (editar completo)
   - Modal Upload Certificado
   - Modal Upload XML (recepción)

3. **Integrar con Facturacion.tsx:**
   - Descomentar y actualizar DGIIValidationButton
   - Agregar columna "Estado e-CF"
   - Agregar acciones de e-CF por factura

4. **Crear componentes reutilizables:**
   - `ECFStatusBadge` - Badge con estados e-CF
   - `ECFActionButtons` - Botones de acciones e-CF
   - `NCFSeriesForm` - Formulario de serie NCF
   - `DGIIConfigForm` - Formulario configuración
   - `XMLUploader` - Componente upload XML
   - `CertificateUploader` - Componente upload certificado

5. **Actualizar API module (regional.ts):**
   - Agregar métodos ACECFAR
   - Agregar métodos emisión e-CF
   - Agregar métodos de descarga

---

## 6. ESTIMACIÓN DE ESFUERZO

| Componente | Complejidad | Esfuerzo (horas) |
|-----------|-------------|------------------|
| Tab Emisión e-CF | Alta | 8-12 |
| Tab Recepción e-CF | Alta | 10-14 |
| Configuración DGII Form | Media | 6-8 |
| NCF Series CRUD | Media | 4-6 |
| Reportes Funcionales | Media | 6-8 |
| Integración Facturacion.tsx | Media | 4-6 |
| Monitoreo Dashboard | Baja | 4-6 |
| Simulador UI | Baja | 3-4 |
| Componentes Reutilizables | Media | 6-8 |
| Testing & QA | - | 8-10 |
| **TOTAL** | - | **59-82 horas** |

---

## 7. CONCLUSIÓN

El backend del módulo `csf_do` está **100% funcional** y listo para uso en modo simulador. El frontend actual tiene una **cobertura del ~30%** de las funcionalidades disponibles.

**Para alcanzar funcionalidad completa del frontend, se requieren:**
- ✅ 8 tabs adicionales o mejoras de tabs existentes
- ✅ 15+ componentes modales y formularios
- ✅ 20+ métodos API adicionales en regional.ts
- ✅ Integración profunda con Facturacion.tsx

**Recomendación:** Implementar en 3 fases priorizadas (CRÍTICO → ALTO → MEDIO) para tener valor incremental y permitir pruebas tempranas del flujo completo de emisión y recepción de e-CF.
