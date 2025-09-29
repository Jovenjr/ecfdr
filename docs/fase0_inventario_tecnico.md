# Fase 0 · Inventario Técnico ECFDR

## 1. Doctypes Clave (`csf_do/csf_do/doctype/`)
- **DGII Configuration** (`dgii_configuration/`): estructura actual vacía; será rediseñada para ambientes y credenciales DGII.
- **Digital Certificate** (`digital_certificate/`): controla certificados PKCS#12 y campos de vigencia.
- **e-CF** (`e_cf/`): orquesta envío, consulta y anulación de comprobantes electrónicos.
- **e-CF Sequence** (`e_cf_sequence/`): manejará rangos autorizados y contingencia Serie B.
- **ECF Audit Log / utilidades** (`e_cf_audit_log/`, `utils/audit_log.py`): registro de eventos críticos.
- **Complementos ERPNext**: doctypes adicionales para retenciones, catálogos y configuraciones tributarias.

## 2. Fixtures y Datos Referenciales
- **Custom Fields** (`csf_do/fixtures/custom_field.json`): campos personalizados requeridos para DGII (ITBIS, retenciones, datos bancarios, etc.).
- **Catálogos JSON** (`csf_do/csf_do/data/`): `unidad_medida.json`, `tipo_moneda.json`, `provincia_municipio.json`, entre otros, necesarios para validar catálogos DGII.

## 3. Utilidades y Servicios XML (`csf_do/csf_do/utils/`)
- **Generadores XML**: `ecf31_builder.py`, `ecf32_builder.py`, ..., `ecf47_builder.py` para tipos e-CF; `rfce32_builder.py` para resumen de consumo; `xml_builder.py` y `xml_utils.py` para funciones comunes.
- **Servicio DGII**: `ecf_service.py` coordina construcción, firma, envío y consulta.
- **Cliente HTTP DGII**: `dgii_client.py` (stubs a reemplazar).
- **Validadores**: `xsd_validator.py`, `field_validators.py`, `business_rules.py`.
- **Firma Digital**: `signing.py`, `xml_signer.py`, `cert_loader.py`.
- **Errores y catálogos**: `dgii_errors.py`, `dgii_mock.py` (mock DGII), `dgii_config.py` (loader).

## 4. Formatos XML Requeridos
| Formato | Etiqueta raíz | Responsable actual | Notas |
|---------|---------------|--------------------|-------|
| e-CF (Tipos 31-47) | `ECF` | `utils/ecf*_builder.py` + `utils/ecf_service.py` | Documento principal de facturación.
| Resumen Factura Consumo | `RFCE` | `utils/rfce32_builder.py` | Obligatorio para facturas tipo 32 < RD$250,000.
| Acuse de Recibo | `ARECF` | (pendiente de implementación) | Receptor debe confirmar recepción.
| Aprobación Comercial | `ACECF` | (pendiente) | Respuesta opcional de receptor.
| Anulación e-NCF | `ANECF` | `ecf_service.py::anular_encf` | Anulación de secuencias no usadas.
| Semilla/Token | `SemillaModel` | `dgii_client.py::get_seed` | Paso inicial para autenticación.

## 5. Reportes y Representaciones
- **Reportes DGII** (`csf_do/csf_do/report/`): `dgii_606/`, otros informes tributarios.
- **Representación Impresa** (`csf_do/csf_do/print_format/`): plantillas de salida PDF.
- **Docs y especificaciones** (`docs/`, `csf_do/csf_do/specs/`): referencias normativas y ejemplos.

## 6. Scripts y Herramientas
- **Tareas programadas** (`csf_do/csf_do/tasks.py`, `scheduler/`): consultas periódicas a DGII.
- **Tests existentes** (`csf_do/csf_do/tests/`, `test_ecfdr_integration.py`): base inicial para validaciones.
- **Scripts auxiliares** (`scripts/`, `run_tests.py`): ejecución y utilidades de desarrollo.

## 7. Pendientes Identificados
- Implementación real de ARECF/ACECF XML y flujo receptor.
- Actualización de `dgii_client.py` para producción.
- Normalización de catálogos y validaciones cruzadas.
- Completar fixtures para requisitos DGII (roles, secuencias, campos faltantes).
