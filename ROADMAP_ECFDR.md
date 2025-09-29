# Roadmap ECFDR → ERPNext + DGII

## Objetivo General
Estabilizar y certificar el módulo `ECFDR` para su uso productivo con ERPNext cumpliendo los requisitos de la Dirección General de Impuestos Internos (DGII) de República Dominicana. El roadmap contempla reingeniería del 60‑70% del código existente, fortaleciendo arquitectura, seguridad, compliance, y experiencia de usuario.

---

## Resumen de Fases
- **Fase 0 · Preparación (0‑2 semanas)**
- **Fase 1 · Arquitectura DGII (3‑6 semanas)**
- **Fase 2 · Integración ERPNext (6‑10 semanas)**
- **Fase 3 · Compliance y Reporting (10‑14 semanas)**
- **Fase 4 · Operación & Observabilidad (14‑18 semanas)**
- **Fase 5 · QA y Lanzamiento (18‑22 semanas)**
- **Seguimiento continuo**

---

## Fase 0 · Preparación (0‑2 semanas)
- **[Auditoría técnica]** Levantar inventario de doctypes, fixtures, reportes y scripts en `csf_do/csf_do/`.
- **[Marco legal y gobernanza]** Elaborar documento de referencia de la Ley 32-23 y normativas DGII vigentes (manuales e-CF, guías de RI, catálogos oficiales) que defina responsabilidades internas (Administrador e-CF, Firmante, Receptor) y políticas de conservación de comprobantes.
- **[Entorno de pruebas]** Provisionar sitio ERPNext de staging con credenciales DGII sandbox y certificados dummy.
- **[Planificación QA]** Definir matriz de casos DGII (envío, contingencia, anulación, recepción) y criterios de aceptación.
- **[Certificación preliminar]** Preparar checklist de requisitos previos DGII (RNC activo, OFV habilitada, Alta NCF, designación de Usuario Administrador e-CF, certificados digitales INDOTEL) y recopilar evidencias.
- **[CI/CD mínimo]** Configurar pipeline con lint, tests básicos y validación de fixtures.
- **Entregables:** Documento de auditoría, entorno listo, plan de pruebas y pipeline operativa.

## Fase 1 · Arquitectura DGII (3‑6 semanas)
- **[DGII Configuration]** Rediseñar doctype `DGIIConfiguration` con campos obligatorios, validaciones, controles de ambiente y UI amigable.
- **[Cliente HTTP]** Reescribir `csf_do/csf_do/utils/dgii_client.py` con:
  - Manejo de tokens, expiración y cacheo.
  - Retries exponenciales con clasificación de errores (HTTP, negocio DGII, rate limiting).
  - Timeouts configurables y circuit breaker.
  - Logging estructurado y telemetría.
- **[Autenticación Ley 32-23]** Implementar el flujo completo de semilla → firma SHA-256 (sin preservación de espacios) → intercambio de token, asegurando que el SN del certificado coincida con el RNC/Cédula/Pasaporte del contribuyente y que los archivos se nombren `RNCEmisor+eNCF.xml`.
- **[Gestión de certificados]** Fortalecer `DigitalCertificate` y `cert_loader` con validación PKCS#12, verificación de vigencia, cifrado de almacenamiento, rotación automática y respaldos.
- **[Catálogos dinámicos]** Sincronizar catálogos DGII (monedas, unidades, provincias, tipos de ingreso) y exponer comandos scheduler para refresco.
- **[Cumplimiento de canal seguro]** Forzar HTTPS/TLS en todas las llamadas salientes y validar certificados DGII; documentar manejo de ambientes Pre-Certificación, Certificación y Producción.
- **Dependencias:** Librerías criptográficas validadas, tablas DGII.
- **Riesgos:** Integración con servicios DGII reales, seguridad de certificados.

## Fase 2 · Integración ERPNext (6‑10 semanas)
- **[Fixtures]** Completar `csf_do/fixtures/` con campos custom requeridos (NCF, ITBIS, retenciones) en `Sales Invoice`, `Purchase Invoice`, `Journal Entry`, `Payment Entry`, etc.
- **[Secuencias NCF]** Reescribir `ECFSequence` para consumir rangos DGII, manejar contingencia (Serie B), bloqueos por agotamiento y sincronización automática.
- **[Overrides y doc events]** Extender `csf_do/csf_do/overrides/` con validaciones automáticas de RNC/NCF, controles de ITBIS y conciliaciones con DGII.
- **[Workflows]** Normalizar estados DGII, construir workflows ERPNext y notificaciones para eventos clave.
- **[Hooks ERPNext]** Revisar `hooks.py` para asegurar triggers en todo el ciclo (submit, cancel, amend).
- **[Representación impresa (RI)]** Generar RI PDF conforme a DGII (orden y contenido mínimo, código QR con parámetros oficiales, código de seguridad derivado de la firma, fechas de emisión/firma) y permitir configuración multilingüe.
- **[Catálogo de e-CF]** Configurar plantillas XML y lógicas de negocio para los tipos 31, 32, 33, 34, 41, 43, 44, 45, 46 y 47, incluyendo reglas de obligatoriedad de campos, límites de repetición e indicadores especiales.
- **[Gestión tributaria]** Implementar reglas de ITBIS (tasas 18/16/0, retenciones, notas de crédito >30 días), ISR (retenciones locales y pagos al exterior), ISC (específico/ad valorem), propina legal y tolerancias de cuadratura ±1 por línea y global.
- **[Moneda y conversión]** Soportar facturación en monedas extranjeras con cálculo automático en DOP y tipo de cambio según DGII.

## Fase 3 · Compliance y Reporting (10‑14 semanas)
- **[Constructores XML]** Refactorizar `ecf*_builder.py` hacia framework reutilizable, centralizando validaciones, formateo decimal y normalización de catálogos.
- **[Validación avanzada]** Ampliar `xsd_validator.py` para soportar versiones dinámicas, caching y validación semántica (reglas DGII).
- **[Firma digital]** Implementar flujo de firma robusto (librería certificada o servicio externo), con manejo de errores y fallback controlado.
- **[Reportes]** Completar 606/607, anexos de nómina y otros formatos DGII, incluyendo generación CSV/TXT y validaciones previas.
- **[Anulación/contingencia]** Fortalecer `anular_encf` y manejo de Serie B, integrando procesos manuales y automáticos.
- **[Resumen RFCE]** Automatizar envío RFCE para facturas de consumo < RD$250,000, acumulando por período y verificando respuestas de DGII.
- **[Recepción y ARECF/ACECF]** Desarrollar endpoints y flujos internos para consumir e-CF entrantes, emitir Acuses de Recibo (ARECF) y gestionar Aprobaciones/Rechazos Comerciales (ACECF) conforme a formatos oficiales.
- **[Delegaciones y roles]** Modelar roles DGII (Administrador, Firmante, Aprobador Comercial) en ERPNext, asegurando que solo el firmante autorizado pueda firmar y enviar documentos.

## Fase 4 · Operación y Observabilidad (14‑18 semanas)
- **[Colas y rendimiento]** Implementar colas dedicadas (Redis) para envío masivo, con límites de concurrencia y reintentos.
- **[Scheduler inteligente]** Ajustar `csf_do/csf_do/tasks.py` para polling adaptativo, escalamiento automático y alertas en pendientes.
- **[Auditoría]** Diseñar doctype `ECF Audit Log` completo, registrar payloads hashados, estados y errores. Incorporar trazabilidad en `audit_log.py`.
- **[Monitoreo]** Integrar dashboards y alertas (email, Slack) con métricas clave (tiempo aprobación, tasa rechazos, vencimientos certificados).
- **[Manejo de contingencia]** Implementar modo offline (Ley 32-23) para capturar e-CF cuando no haya conectividad, con posterior sincronización y bitácora de incidentes.
- **[Seguridad y cifrado]** Auditar almacenamiento de XML firmados, tokens y certificados; aplicar cifrado en reposo y políticas de retención exigidas por DGII.

## Fase 5 · QA y Lanzamiento (18‑22 semanas)
- **[Pruebas]** Construir suites end-to-end, escenarios de error DGII, stress tests y validaciones de seguridad.
- **[Documentación]** Desarrollar manuales técnicos (API, webhooks, configuración), guías de troubleshooting y manual de usuario final.
- **[Pilotaje]** Ejecutar piloto controlado con clientes iniciales, medir KPIs y corregir desviaciones.
- **[Plan de soporte]** Establecer protocolos de soporte post go-live, escalamiento y mantenimiento.
- **[Proceso de certificación DGII]** Ejecutar las tres etapas oficiales:
  - *Etapa 1 (Solicitud):* Enviar formulario FI-GDF-016 con evidencias y designación de Usuario Administrador e-CF.
  - *Etapa 2 (Sets de pruebas):* Publicar URLs de recepción/aprobación/autenticación, generar sets de datos y simulaciones, enviar RI PDF con QR y completar ARECF/ACECF.
  - *Etapa 3 (Certificación):* Firmar y remitir Declaración Jurada, validar URLs productivas y obtener habilitación del menú de facturación electrónica en la OFV.
- **[Plan de transición]** Definir estrategia de migración de e-CF heredados, capacitación de usuarios y checklist de salida a producción.

---

## Seguimiento Continuo
- **[Gobernanza de versiones]** Mantener catálogos y XSD actualizados; revisar semestralmente cambios DGII.
- **[Post go-live]** Revisiones trimestrales de compliance, auditorías de seguridad y ajustes según incidentes.
- **[Backlog Evolutivo]** Integrar funcionalidades futuras (recepción masiva, analítica tributaria, automatización de declaraciones) basadas en retroalimentación.
- **[Relación con DGII]** Establecer canal formal con DGII para notificaciones de cambios normativos, actualizaciones de esquemas y solicitudes de soporte.

## Consideraciones de Gestión
- **Recursos:** Equipo multidisciplinario (backend, ERPNext, QA, seguridad, DevOps).
- **Riesgos clave:** Cambios normativos DGII, disponibilidad de sandbox, seguridad de certificados, dependencia de terceros.
- **KPIs:** Tiempo promedio de aprobación DGII, tasa de rechazos, cumplimiento 606/607, cobertura de tests, disponibilidad del servicio.

---

## Próximos Pasos Inmediatos
1. Conformar equipo técnico y asignar responsables por fase.
2. Aprobar presupuesto y cronograma detallado (Gantt/OKRs trimestrales).
3. Iniciar Fase 0 con auditoría profunda del repositorio y configuración del entorno de pruebas.

---

## Anexo A · Tipos de Comprobantes Electrónicos (e-CF)
- **[31 – Factura de Crédito Fiscal]** Obligatoria para operaciones B2B con plena deducibilidad; requiere detalle de ITBIS, retenciones ISR/ITBIS e identificación del comprador.
- **[32 – Factura de Consumo]** Diferenciar montos ≥ RD$250,000 (envío completo) y < RD$250,000 (incluir en resumen RFCE). Manejar consumidor final y montos en efectivo.
- **[33 – Nota de Débito]** Ajustes positivos sobre facturas emitidas; debe referenciar e-NCF afectado y recalcular impuestos.
- **[34 – Nota de Crédito]** Ajustes negativos; validar reglas de ITBIS según ventana de 30 días y controlar devoluciones parciales.
- **[41 – Comprobante de Compras]** Para adquisiciones a proveedores informales; requiere campos de identificación del vendedor y retenciones.
- **[43 – Gastos Menores]** Sustento de gastos corporativos menores; asegurar límites y documentación soporte.
- **[44 – Regímenes Especiales]** Para transacciones exentas; marcar indicadores de exención y anexar sustentos.
- **[45 – Gubernamental]** Transacciones con el Estado; incluir campos específicos solicitados por entidades públicas.
- **[46 – Exportaciones]** Reportar ventas fuera del territorio; manejar divisas y exenciones de impuestos indirectos.
- **[47 – Pagos al Exterior]** Retenciones totales de ISR a no residentes; considerar tasas diferenciadas para dividendos, intereses y servicios.

## Anexo B · Impuestos y Reglas Tributarias Clave
- **[ITBIS]** Calcular tasas 18/16/0%, diferenciar gravado/exento, gestionar retenciones y base imponible; reflejar en XML encabezado y detalle.
- **[ISR]** Retenciones a residentes y no residentes; tasas estándar 10% dividendos, 27%/29% servicios; incluir campos `TotalISRRetencion`.
- **[ISC]** Manejar impuestos específicos/ad valorem (alcohol, tabaco, combustibles) con códigos DGII.
- **[Propina legal]** Aplicar código 001 al 10% cuando aplique.
- **[Cuadratura]** Validar tolerancia ±1 por línea y global; abortar envío si excede.
- **[Contingencia]** Registrar motivo y serie B; sincronizar e-CF diferidos al restablecer comunicación.

## Anexo C · Proceso de Certificación DGII (Resumen Operativo)
- **[Requisitos previos]** RNC activo, Alta NCF, OFV habilitada, certificados INDOTEL vigentes, software en producción interna.
- **[Postulación y URLs]** Registro de endpoints de recepción (`/recepcion`), aprobación (`/aprobacion`), autenticación (opcional) y políticas SLA.
- **[Sets de pruebas]** Generar XML según matrices DGII, enviar ARECF/ACECF y RI con QR y código de seguridad.
- **[Declaración Jurada y Go-Live]** Firmar XML con App Firma Digital, enviar a DGII y documentar fechas de paso a producción.
