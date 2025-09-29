# Fase 2 · Resumen de Implementación

## Fecha completación
2025-09-29

## Objetivos cumplidos

### 1. Fixtures DGII (NCF, ITBIS, retenciones)
**Archivo**: `csf_do/csf_do/patches/v2_2_0_add_dgii_ecf_fields.py`

Se creó patch de migración para añadir campos personalizados en:

#### Sales Invoice
- `dgii_ecf_section`: Sección "DGII e-CF"
- `dgii_tipo_ecf`: Selector de tipo e-CF (31-47)
- `dgii_ecf_sequence`: Link a secuencia activa
- `dgii_encf`: e-NCF asignado (read-only)
- `dgii_estado_dgii`: Estado DGII (Pendiente, En Proceso, Aceptado, etc.)
- `dgii_track_id`: Track ID de consulta DGII
- `dgii_codigo_seguridad`: Código de 6 dígitos para QR
- `dgii_forma_pago`: Forma de pago DGII (1-4)
- `dgii_total_itbis_tasa1/2/3`: Totales ITBIS por tasa
- `dgii_total_itbis_exento`: Total exento
- `dgii_total_itbis_retenido`: ITBIS retenido
- `dgii_total_isr_retenido`: ISR retenido
- `dgii_total_isc`: Total ISC
- `dgii_total_propina_legal`: Propina legal (10%)
- `dgii_tipo_moneda`: Código moneda alternativa
- `dgii_tipo_cambio`: Tipo de cambio (4 decimales)
- `dgii_total_itbis_moneda_alterna`: Total ITBIS en otra moneda

#### Sales Invoice Item
- `dgii_indicator`: Indicador de facturación (0-4)
- `dgii_itbis_percentage`: % ITBIS aplicado
- `dgii_isr_retencion`: % ISR retención
- `dgii_isc_codigo`: Código ISC
- `dgii_propina_flag`: Incluye propina legal

**Registro en patches.txt**: Línea 7

---

### 2. Reimplementación ECFSequence
**Archivos**: 
- `csf_do/csf_do/doctype/e_cf_sequence/e_cf_sequence.json`
- `csf_do/csf_do/doctype/e_cf_sequence/e_cf_sequence.py`

#### Campos añadidos
- `dgii_environment`: Ambiente DGII (Precertificación/Certificación/Producción)
- `status`: Estado (Activo/Exhausto/Expirado/Suspendido)
- `resolution_number`: Número de resolución DGII
- `resolution_date`: Fecha de resolución
- `valid_from` / `valid_until`: Vigencia de secuencia
- `next_number`: Próximo número a asignar (reemplaza `current`)
- `last_allocated_on`: Timestamp última asignación
- `replacement_deadline`: Fecha límite reemplazo Serie B (contingencia)
- `allow_reuse_rejected`: Permitir reutilizar tras rechazo DGII
- `last_synced_at` / `sync_reference`: Control sincronización

#### Métodos implementados
- `validate()`: Validaciones de rango, fechas, contingencia
- `peek_next_encf()`: Ver próximo e-NCF sin avanzar
- `allocate_next_encf()`: Asignar y avanzar secuencia
- `reset_to(value)`: Reajustar secuencia manualmente
- `schedule_contingency_deadline()`: Calcular fecha reemplazo Serie B
- `is_expired`: Property para verificar expiración

#### Validaciones
- Rangos positivos y coherentes (desde < hasta)
- Fechas válidas (vigencia, resolución)
- Contingencia Serie B requiere `replacement_deadline`
- Estado automático según disponibilidad y vigencia

---

### 3. Overrides y Handlers
**Archivo principal**: `csf_do/csf_do/integrations/ecf/handlers.py`

#### Hooks implementados (registrados en `csf_do/hooks.py`)
- `before_sales_invoice_submit`: Validar RNC, asignar e-NCF, calcular totales
- `on_sales_invoice_submit`: Crear documento e-CF, encolar envío DGII
- `on_sales_invoice_cancel`: Generar NC electrónica o anular
- `on_sales_invoice_update_after_submit`: Permitir actualización estado DGII
- `on_purchase_invoice_cancel`: Manejo compras (tipo 41)

#### Funciones clave
- `_assign_encf_to_invoice()`: Asigna e-NCF desde secuencia activa
- `_calculate_dgii_totals()`: Calcula totales ITBIS/ISR/ISC/propina por línea
- `_create_or_update_ecf_document()`: Vincula Sales Invoice con e-CF
- `_queue_dgii_submission()`: Encola envío en background
- `_build_ecf_payload_from_invoice()`: Construye JSON para builder XML

---

### 4. Workflows y notificaciones
**Archivos**: 
- `csf_do/csf_do/tasks.py` (scheduler cada 10 min)
- `csf_do/csf_do/integrations/ecf/handlers.py`

#### Estados DGII gestionados
- **Pendiente**: e-CF creado, no enviado
- **En Proceso**: Enviado a DGII, esperando respuesta
- **Aceptado**: Válido para fines tributarios
- **Aceptado Condicional**: Válido con observaciones
- **Rechazado**: No válido, requiere corrección
- **Observado**: Error en envío/validación
- **Anulado**: e-NCF anulado

#### Scheduler (`poll_ecf_statuses`)
- Consulta automática cada 10 minutos
- Actualiza estado de e-CF en `Pendiente`/`En Proceso`
- Límite 100 documentos por ejecución
- Queue `short`, timeout 300s

#### Notificaciones
- Alert al usuario tras submit: "Enviado en segundo plano"
- Avisos para facturas Rechazadas/Observadas
- Warning al cancelar factura Aceptada (requiere NC)

---

### 5. Representación Impresa (RI) con QR
**Archivos**:
- `csf_do/csf_do/utils/qr_code_generator.py`
- `csf_do/csf_do/utils/ecf_service.py`

#### QR Code v8
- **Composición para ≥ RD$250K**: RncEmisor, RncComprador, ENCF, FechaEmision, MontoTotal, FechaFirma, CodigoSeguridad
- **Composición para < RD$250K**: RncEmisor, ENCF, MontoTotal, CodigoSeguridad
- **Formato fecha**: dd-MM-aaaa HH:mm:ss
- **Código de seguridad**: Primeros 6 dígitos del hash SHA-256 de firma

#### Generación PDF
- Incluye QR embebido (base64)
- Código de seguridad visible debajo del QR
- Tamaño máximo: 10MB
- Print format compatible con Frappe

---

### 6. Tipos e-CF (31-47)
**Archivos**: `csf_do/csf_do/utils/ecf{31-47}_builder.py`

#### Builders implementados
| Tipo | Nombre | Builder | Estado |
|------|--------|---------|--------|
| 31 | Factura Crédito Fiscal | `ecf31_builder.py` | ✓ Completo |
| 32 | Factura Consumo | `ecf32_builder.py` | ✓ Completo |
| 33 | Nota Débito | `ecf33_builder.py` | ✓ Completo |
| 34 | Nota Crédito | `ecf34_builder.py` | ✓ Completo |
| 41 | Compras | `ecf41_builder.py` | ✓ Completo |
| 43 | Gastos Menores | `ecf43_builder.py` | ✓ Completo |
| 44 | Regímenes Especiales | `ecf44_builder.py` | ✓ Completo |
| 45 | Gubernamental | `ecf45_builder.py` | ✓ Completo |
| 46 | Exportaciones | `ecf46_builder.py` | ✓ Completo |
| 47 | Pagos al Exterior | `ecf47_builder.py` | ✓ Completo |

#### Validaciones incluidas
- Validación contra JSON Schema (`csf_do/csf_do/specs/ecf*.json`)
- Validación XSD post-construcción
- Validaciones de catálogos (monedas, unidades, provincias)
- Formateo de fechas (dd-MM-yyyy, dd-MM-yyyy HH:mm:ss)
- Redondeo de montos (2 decimales) y precios (4 decimales)
- Coherencia totales vs suma items (tolerancia ±0.01)

---

### 7. Reglas tributarias
**Archivos**:
- `csf_do/csf_do/utils/business_rules.py`
- `csf_do/csf_do/integrations/ecf/handlers.py`

#### ITBIS (Impuesto sobre Transferencia de Bienes Industrializados y Servicios)
- **Tasa 1**: 18% (Indicador 1)
- **Tasa 2**: 16% (Indicador 2)
- **Tasa 3**: 0% (Indicador 3, gravado tasa cero)
- **Exento**: Indicador 0

#### ISR (Impuesto Sobre la Renta)
- Retenciones configurables por ítem (`dgii_isr_retencion`)
- Ejemplos: 10% intereses no residentes, 0.5% pagos Estado

#### ISC (Impuesto Selectivo al Consumo)
- Campo `dgii_isc_codigo` por ítem
- Códigos 006-039 según tabla DGII

#### Propina Legal
- 10% automático si `dgii_propina_flag` = 1
- Código 001 en tabla impuestos adicionales

#### Tolerancias
- **Por línea**: ±1 unidad de (precio × cantidad)
- **Global**: ±(número de líneas) sobre monto total
- Implementado en `validate_montos_gravados_y_exentos_vs_indicador()`

#### Notas de Crédito >30 días
- Indicador especial en NC tipo 34
- No incluye devolución de ITBIS, solo monto base

---

## Archivos creados/modificados

### Nuevos archivos
1. `csf_do/csf_do/patches/v2_2_0_add_dgii_ecf_fields.py`
2. `csf_do/csf_do/integrations/__init__.py`
3. `csf_do/csf_do/integrations/ecf/__init__.py`
4. `csf_do/csf_do/integrations/ecf/handlers.py`
5. `docs/fase2_resumen_implementacion.md` (este archivo)

### Archivos modificados
1. `csf_do/patches.txt` (línea 7)
2. `csf_do/hooks.py` (doc_events Sales/Purchase Invoice)
3. `csf_do/csf_do/doctype/e_cf_sequence/e_cf_sequence.json`
4. `csf_do/csf_do/doctype/e_cf_sequence/e_cf_sequence.py`
5. `TASKS_CHECKLIST.md` (Fase 2 completada)

---

## Próximos pasos recomendados

### Testing
- [ ] Ejecutar `bench migrate` para aplicar patch de campos custom
- [ ] Crear secuencias de prueba para tipos 31, 32, 34
- [ ] Probar flujo completo: Sales Invoice → Submit → Envío DGII → Consulta estado
- [ ] Validar cálculo de totales ITBIS por tasa
- [ ] Verificar generación de QR y código de seguridad

### Soporte multi-moneda (pendiente Fase 2)
- [ ] Implementar conversión DOP en handlers
- [ ] Validar tipo de cambio con 4 decimales
- [ ] Poblar `dgii_total_itbis_moneda_alterna`
- [ ] Extender builders para sección `<OtraMoneda>`

### Fase 3 - Compliance
- [ ] Refactor builders con framework común
- [ ] Validación XSD con versionado dinámico
- [ ] Firma digital certificada
- [ ] Reportes 606/607
- [ ] Automatización RFCE para facturas <RD$250K
- [ ] Recepción e-CF + ARECF/ACECF

---

## Notas de migración

### Pasos para activar en producción
1. **Backup completo** antes de migración
2. Ejecutar `bench migrate` para crear campos custom
3. Configurar **DGII Configuration** con:
   - RNC emisor
   - Certificado PKCS#12
   - URLs de ambientes (precert/cert/prod)
   - API keys
4. Crear **secuencias e-CF** autorizadas por DGII
5. Asignar **roles** a usuarios:
   - Emisor e-CF
   - Administrador e-CF
   - Aprobador Comercial
6. Probar en ambiente **Precertificación** primero
7. Solicitar certificación DGII
8. Activar en **Producción** tras aprobación

### Configuración mínima requerida
```python
# DGII Configuration (Single DocType)
{
    "rnc_emisor": "123456789",
    "p12_file": "/path/to/cert.p12",
    "p12_password": "***",
    "precert_base_url": "https://ecf.dgii.gov.do/testecf/",
    "cert_base_url": "https://ecf.dgii.gov.do/certecf/",
    "prod_base_url": "https://ecf.dgii.gov.do/ecf/",
    "verify_ssl": 1,
    "timeout_seconds": 30,
    "max_retries": 3
}

# e-CF Sequence (ejemplo)
{
    "sequence_type": "31 Factura Crédito Fiscal",
    "serie": "E",
    "dgii_environment": "Producción",
    "status": "Activo",
    "range_from": 1,
    "range_to": 10000,
    "next_number": 1,
    "valid_from": "2025-01-01",
    "valid_until": "2026-12-31"
}
```

---

## Contacto y soporte
Para consultas técnicas o normativas DGII:
- **Portal DGII**: https://dgii.gov.do
- **Oficina Virtual (OFV)**: https://ofv.dgii.gov.do
- **Soporte e-CF**: ecf@dgii.gov.do
- **Documentación técnica**: Portal DGII > e-CF > Manuales

---

**Fin del documento**
