# Plan de Implementación - CSF_DO Production Ready

**Fecha**: 10 de Enero, 2025  
**Objetivo**: Completar funcionalidades faltantes para producción  
**Estrategia**: Usar simulador DGII para desarrollo y testing

---

## ✅ FASE 1: SIMULADOR DGII (COMPLETADO)

### Archivos Creados:
- ✅ `csf_do/csf_do/integrations/dgii_simulator.py` - Simulador completo
- ✅ `csf_do/csf_do/integrations/dgii_client.py` - Cliente unificado
- ✅ `csf_do/csf_do/doctype/dgii_simulator_config/` - Configuración UI
- ✅ `csf_do/csf_do/tests/test_dgii_simulator.py` - Tests
- ✅ `csf_do/docs/SIMULADOR_DGII.md` - Documentación

### Funcionalidades:
- ✅ Envío de e-CF simulado
- ✅ Consulta de estado con progresión temporal
- ✅ Acuse de recibo (ACECFAR)
- ✅ Generación de e-CF de proveedores
- ✅ Múltiples escenarios (éxito, errores, timeouts)
- ✅ Cambio transparente simulador ↔ API real

---

## 🔄 FASE 2: MÓDULO ACECFAR (RECEPCIÓN DE e-CF)

**Prioridad**: 🔴 CRÍTICA  
**Tiempo estimado**: 2-3 semanas  
**Estado**: Pendiente

### 2.1 Parser de XML Recibidos

**Archivo**: `csf_do/csf_do/utils/acecfar_parser.py`

**Funcionalidades**:
- Parsear XML de e-CF recibidos
- Extraer datos del emisor (RNC, nombre, dirección)
- Extraer datos del comprobante (NCF, fecha, tipo)
- Extraer ítems y totales
- Extraer impuestos (ITBIS, ISC, propinas)
- Validar estructura XML contra XSD

**Tareas**:
```python
class ACECFARParser:
    def parse_xml(self, xml_content: str) -> Dict
    def extract_header(self, xml_tree) -> Dict
    def extract_emisor(self, xml_tree) -> Dict
    def extract_items(self, xml_tree) -> List[Dict]
    def extract_totals(self, xml_tree) -> Dict
    def validate_structure(self, xml_content: str) -> bool
```

### 2.2 Validación de Firma Digital

**Archivo**: `csf_do/csf_do/utils/signature_validator.py`

**Funcionalidades**:
- Validar firma digital del emisor
- Verificar certificado del emisor
- Validar cadena de confianza
- Verificar que el XML no fue modificado

**Tareas**:
```python
class SignatureValidator:
    def validate_signature(self, xml_content: str) -> bool
    def extract_certificate(self, xml_content: str) -> Dict
    def verify_certificate_chain(self, certificate) -> bool
    def verify_xml_integrity(self, xml_content: str) -> bool
```

### 2.3 Creación Automática de Purchase Invoice

**Archivo**: `csf_do/csf_do/integrations/acecfar_processor.py`

**Funcionalidades**:
- Crear Purchase Invoice automáticamente
- Buscar/crear Supplier si no existe
- Mapear ítems a Items de ERPNext
- Calcular impuestos correctamente
- Vincular con Purchase Order (si existe)
- Manejar múltiples monedas

**Tareas**:
```python
class ACECFARProcessor:
    def process_ecf(self, xml_content: str) -> Dict
    def create_purchase_invoice(self, parsed_data: Dict) -> str
    def get_or_create_supplier(self, supplier_data: Dict) -> str
    def map_items(self, items: List[Dict]) -> List[Dict]
    def calculate_taxes(self, totals: Dict) -> List[Dict]
    def link_to_purchase_order(self, pi_name: str, supplier: str) -> bool
```

### 2.4 Workflow de Aprobación/Rechazo

**Archivo**: `csf_do/csf_do/doctype/ecf_recibido/ecf_recibido.json`

**DocType**: `e-CF Recibido`

**Campos**:
- Datos del emisor (RNC, nombre)
- NCF, fecha, tipo de e-CF
- Monto total, impuestos
- Estado (Pendiente, Aprobado, Rechazado)
- Purchase Invoice vinculada
- XML original
- Firma digital válida (check)
- Motivo de rechazo (si aplica)

**Estados**:
1. **Pendiente** - Recibido, esperando validación
2. **Validado** - Firma y estructura válidas
3. **Aprobado** - Purchase Invoice creada
4. **Rechazado** - Rechazado por usuario
5. **Acuse Enviado** - Acuse enviado a DGII

### 2.5 Envío de Acuse de Recibo

**Funcionalidades**:
- Generar XML de acuse (ACECFAR)
- Firmar acuse digitalmente
- Enviar a DGII (o simulador)
- Registrar confirmación

**Tareas**:
```python
class ACECFARSender:
    def generate_acuse_xml(self, ecf_recibido: str, estado: str) -> str
    def sign_acuse(self, xml_content: str) -> str
    def send_to_dgii(self, xml_signed: str) -> Dict
    def update_status(self, ecf_recibido: str, result: Dict)
```

### 2.6 Buzón de Recepción

**Opciones de recepción**:
1. **Email** - Recibir e-CF por email
2. **Upload Manual** - Subir XML manualmente
3. **API Endpoint** - Recibir vía API REST
4. **SFTP** - Recibir de carpeta SFTP

**Archivo**: `csf_do/csf_do/integrations/acecfar_inbox.py`

**Tareas**:
```python
class ACECFARInbox:
    def process_email_attachments(self)
    def process_uploaded_file(self, file_path: str)
    def process_api_request(self, xml_content: str)
    def process_sftp_folder(self, folder_path: str)
```

---

## 🔄 FASE 3: MEJORAS EN REPORTES 606/607

**Prioridad**: 🟡 IMPORTANTE  
**Tiempo estimado**: 1 semana  
**Estado**: Pendiente

### 3.1 Validación de RNC/Cédula

**Archivo**: `csf_do/csf_do/utils/rnc_validator.py`

**Funcionalidades**:
- Validar formato de RNC (9 dígitos)
- Validar formato de Cédula (11 dígitos con guiones)
- Calcular dígito verificador
- Validar contra lista de RNC activos (opcional)

**Tareas**:
```python
class RNCValidator:
    def validate_rnc(self, rnc: str) -> bool
    def validate_cedula(self, cedula: str) -> bool
    def calculate_check_digit(self, number: str) -> str
    def format_rnc(self, rnc: str) -> str
    def format_cedula(self, cedula: str) -> str
```

### 3.2 Validación de Montos

**Archivo**: `csf_do/csf_do/utils/amount_validator.py`

**Funcionalidades**:
- Validar límites de montos según normativa
- Validar que suma de ítems = total
- Validar cálculo de impuestos
- Detectar montos sospechosos

**Tareas**:
```python
class AmountValidator:
    def validate_limits(self, amount: float, ecf_type: str) -> bool
    def validate_totals(self, items: List, total: float) -> bool
    def validate_tax_calculation(self, base: float, tax: float, rate: float) -> bool
    def detect_suspicious_amounts(self, amount: float) -> List[str]
```

### 3.3 Detección de Duplicados

**Archivo**: `csf_do/csf_do/utils/duplicate_detector.py`

**Funcionalidades**:
- Detectar NCF duplicados en 606/607
- Detectar facturas duplicadas (mismo proveedor, monto, fecha)
- Alertar sobre posibles duplicados

**Tareas**:
```python
class DuplicateDetector:
    def check_ncf_duplicates(self, ncf: str, period: str) -> List[str]
    def check_invoice_duplicates(self, supplier: str, amount: float, date: str) -> List[str]
    def generate_duplicate_report(self, period: str) -> Dict
```

### 3.4 Reconciliación 606/607 con e-CF

**Archivo**: `csf_do/csf_do/report/reconciliacion_ecf/`

**Funcionalidades**:
- Comparar 606/607 con e-CF enviados
- Detectar discrepancias
- Generar reporte de diferencias
- Sugerir correcciones

**Tareas**:
```python
class ECFReconciliation:
    def reconcile_607_with_sent_ecf(self, period: str) -> Dict
    def reconcile_606_with_received_ecf(self, period: str) -> Dict
    def detect_discrepancies(self, report_data: List, ecf_data: List) -> List[Dict]
    def generate_reconciliation_report(self, period: str) -> str
```

### 3.5 Preview de Reportes

**Archivo**: `csf_do/csf_do/report/reporte_606/reporte_606.js`

**Funcionalidades**:
- Mostrar preview antes de generar archivo
- Permitir correcciones inline
- Validar antes de exportar
- Mostrar warnings y errores

---

## 🔄 FASE 4: AMPLIACIÓN DE TESTS

**Prioridad**: 🟡 IMPORTANTE  
**Tiempo estimado**: 2 semanas  
**Estado**: Pendiente

### 4.1 Tests de Integración con Simulador

**Archivo**: `csf_do/csf_do/tests/test_integration_ecf.py`

**Tests**:
- Flujo completo: Crear Sales Invoice → Generar e-CF → Enviar → Consultar estado
- Flujo ACECFAR: Recibir XML → Validar → Crear Purchase Invoice → Enviar acuse
- Flujo 606/607: Generar reportes → Validar → Exportar
- Manejo de errores: Timeouts, validaciones, rechazos

### 4.2 Tests End-to-End

**Archivo**: `csf_do/csf_do/tests/test_e2e.py`

**Escenarios**:
- Empresa nueva: Setup completo → Primera factura → Envío → Reporte 607
- Recepción de compra: Recibir e-CF → Aprobar → Crear PI → Reporte 606
- Notas de crédito: Crear NC → Vincular a factura → Enviar → Validar
- Múltiples tipos: Enviar 10 tipos diferentes de e-CF

### 4.3 Tests de Carga

**Archivo**: `csf_do/csf_do/tests/test_performance.py`

**Pruebas**:
- Enviar 1000 e-CF en paralelo
- Generar reporte 607 con 10,000 facturas
- Procesar 500 e-CF recibidos
- Medir tiempos de respuesta

### 4.4 Tests de Validación

**Archivo**: `csf_do/csf_do/tests/test_validators.py`

**Tests**:
- Validación RNC/Cédula (casos válidos e inválidos)
- Validación de montos (límites, cálculos)
- Validación XSD (todos los tipos de e-CF)
- Validación de firma digital

---

## 🔄 FASE 5: MONITOREO Y DASHBOARD

**Prioridad**: 🟢 MEJORA  
**Tiempo estimado**: 1 semana  
**Estado**: Pendiente

### 5.1 Dashboard de Operaciones

**Archivo**: `csf_do/csf_do/page/dgii_dashboard/`

**Widgets**:
- e-CF enviados hoy/mes
- e-CF pendientes de envío
- e-CF rechazados (últimos 7 días)
- e-CF recibidos pendientes de aprobación
- Tasa de éxito de envíos
- Tiempo promedio de procesamiento
- Alertas activas

### 5.2 Sistema de Alertas

**Archivo**: `csf_do/csf_do/utils/alert_manager.py`

**Alertas**:
- Certificado por vencer (30, 15, 7 días)
- Secuencias NCF agotándose (<100 restantes)
- e-CF rechazados (más de 5 en 1 hora)
- API DGII no disponible
- e-CF recibidos sin procesar (>24 horas)
- Discrepancias en reconciliación

### 5.3 Logs Estructurados

**Archivo**: `csf_do/csf_do/utils/logger.py`

**Funcionalidades**:
- Log de todas las operaciones DGII
- Formato estructurado (JSON)
- Niveles: DEBUG, INFO, WARNING, ERROR
- Rotación de logs
- Búsqueda y filtrado

---

## 📋 CHECKLIST DE IMPLEMENTACIÓN

### Fase 2: ACECFAR (Crítico)
- [ ] 2.1 Parser de XML recibidos
- [ ] 2.2 Validación de firma digital
- [ ] 2.3 Creación automática de Purchase Invoice
- [ ] 2.4 Workflow de aprobación/rechazo
- [ ] 2.5 Envío de acuse de recibo
- [ ] 2.6 Buzón de recepción (email, upload, API)
- [ ] Tests de ACECFAR con simulador

### Fase 3: Mejoras 606/607 (Importante)
- [ ] 3.1 Validación de RNC/Cédula
- [ ] 3.2 Validación de montos
- [ ] 3.3 Detección de duplicados
- [ ] 3.4 Reconciliación con e-CF
- [ ] 3.5 Preview de reportes
- [ ] Tests de validaciones

### Fase 4: Tests (Importante)
- [ ] 4.1 Tests de integración
- [ ] 4.2 Tests end-to-end
- [ ] 4.3 Tests de carga
- [ ] 4.4 Tests de validación
- [ ] Cobertura >80%

### Fase 5: Monitoreo (Mejora)
- [ ] 5.1 Dashboard de operaciones
- [ ] 5.2 Sistema de alertas
- [ ] 5.3 Logs estructurados
- [ ] Documentación de monitoreo

---

## 🎯 PRÓXIMOS PASOS INMEDIATOS

### 1. Probar el Simulador (HOY)
```bash
# Ejecutar tests del simulador
bench --site [site] run-tests csf_do.csf_do.tests.test_dgii_simulator

# Probar desde consola
bench --site [site] console
>>> from csf_do.csf_do.integrations.dgii_client import get_dgii_client
>>> client = get_dgii_client()
>>> result = client.enviar_ecf("<test>XML</test>", "31", "B0100000001")
>>> print(result)
```

### 2. Empezar con ACECFAR Parser (MAÑANA)
- Crear estructura de archivos
- Implementar parser básico
- Tests unitarios del parser

### 3. Continuar con Validación de Firma (DÍA 3)
- Implementar validador de firma
- Integrar con parser
- Tests de validación

### 4. Crear Purchase Invoice Automática (DÍA 4-5)
- Implementar processor
- Mapeo de datos
- Tests de creación

---

## 📊 MÉTRICAS DE ÉXITO

### Fase 2 (ACECFAR):
- ✅ Parsear correctamente 100% de e-CF válidos
- ✅ Validar firma digital con 100% de precisión
- ✅ Crear Purchase Invoice sin errores
- ✅ Enviar acuse en <5 segundos

### Fase 3 (606/607):
- ✅ Detectar 100% de RNC/Cédula inválidos
- ✅ Detectar 100% de duplicados
- ✅ Reconciliación con 0 falsos positivos

### Fase 4 (Tests):
- ✅ Cobertura de código >80%
- ✅ 0 tests fallando
- ✅ Tiempo de ejecución <5 minutos

### Fase 5 (Monitoreo):
- ✅ Dashboard carga en <2 segundos
- ✅ Alertas enviadas en <1 minuto
- ✅ Logs estructurados y buscables

---

## 🚀 CRONOGRAMA REVISADO

| Semana | Fase | Entregables |
|--------|------|-------------|
| 1 | ✅ Simulador | Simulador completo, tests, docs |
| 2-3 | ACECFAR | Parser, validador, processor |
| 4 | ACECFAR | Workflow, buzón, tests |
| 5 | 606/607 | Validaciones, reconciliación |
| 6 | Tests | Suite completa de tests |
| 7 | Monitoreo | Dashboard, alertas, logs |
| 8 | QA | Testing final, documentación |

**Total: 8 semanas para production-ready**

---

## 📝 NOTAS

- El simulador permite desarrollar todo sin conexión DGII
- Cada módulo debe tener tests antes de pasar al siguiente
- Documentar mientras se desarrolla, no al final
- Hacer commits frecuentes con mensajes descriptivos
- Revisar código antes de merge

---

**Última actualización**: 10 de Enero, 2025  
**Próxima revisión**: Fin de Semana 2
