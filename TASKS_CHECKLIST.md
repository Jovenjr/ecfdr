# Checklist de Desarrollo ECFDR

## Leyenda
## Fase 0 · Preparación
- [x] Completado — ver `docs/fase0_inventario_tecnico.md`, `docs/fase0_marco_legal.md`, `docs/fase0_entorno_pruebas.md`, `docs/fase0_matriz_pruebas.md`, `docs/fase0_checklist_dgii.md`, `docs/fase0_pipeline_ci_cd.md`

## Fase 1 · Arquitectura DGII
- [x] Rediseño doctype `DGIIConfiguration` (campos obligatorios, validaciones, UI) — ver `csf_do/csf_do/doctype/dgii_configuration/`
- [x] Reescritura `csf_do/csf_do/utils/dgii_client.py` (tokens, retries, circuit breaker)
- [x] Flujo autenticación Ley 32-23 (semilla → firma SHA-256 → token) — incluido en `dgii_client.py`
- [x] Sincronización de catálogos DGII (monedas, unidades, provincias, tipos ingresos) — ver `csf_do/csf_do/utils/catalog_sync.py`
- [x] Cumplimiento TLS y documentación de ambientes (Precert, Certificación, Producción) — validado en `dgii_configuration.py` y `dgii_client.py`

## Fase 2 · Integración ERPNext
- [x] Fixtures DGII (NCF, ITBIS, retenciones) para doctypes ERPNext claves — ver `csf_do/csf_do/patches/v2_2_0_add_dgii_ecf_fields.py`
- [x] Reimplementación `ECFSequence` (rangos, contingencia Serie B, sincronización) — ver `csf_do/csf_do/doctype/e_cf_sequence/`
- [x] Overrides/doc events con validaciones NCF/RNC + ITBIS — ver `csf_do/csf_do/integrations/ecf/handlers.py` y `csf_do/hooks.py`
- [x] Workflows y notificaciones por estados DGII — integrado en handlers y `csf_do/csf_do/tasks.py`
- [x] Hooks ERPNext completos (submit/cancel/amend) — ver `csf_do/csf_do/integrations/ecf/handlers.py`
- [x] Representación impresa (RI) PDF con QR y código de seguridad — incluido en `csf_do/csf_do/utils/ecf_service.py` y `qr_code_generator.py`
- [x] Configuración completa de tipos e-CF (31, 32, 33, 34, 41, 43, 44, 45, 46, 47) — builders en `csf_do/csf_do/utils/ecf*_builder.py`
- [x] Reglas tributarias (ITBIS, ISR, ISC, propina, tolerancias) — ver `csf_do/csf_do/utils/business_rules.py` y handlers
- [ ] Soporte multi-moneda (conversiones DOP)

## Fase 3 · Compliance y Reporting
- [x] Refactor builders `ecf*_builder.py` (framework común, reglas semánticas)
- [ ] Validación XSD avanzada (versionado dinámico, caching, reglas DGII)
- [ ] Firma digital robusta (biblioteca certificada/servicio externo)
- [ ] Reportes DGII (606, 607, nómina, formatos oficiales)
- [ ] Fortalecer `anular_encf` + contingencia Serie B
- [ ] Automatización Resumen RFCE para facturas < RD$250,000
- [ ] Recepción e-CF + generación ARECF/ACECF
- [ ] Implementación de roles DGII (Administrador, Firmante, Aprobador Comercial)

## Fase 4 · Operación y Observabilidad
- [ ] Colas dedicadas (Redis) con límites y reintentos
- [ ] Scheduler inteligente (`csf_do/csf_do/tasks.py`) con escalamiento y alertas
- [ ] Doctype `ECF Audit Log` completo + trazabilidad en `audit_log.py`
- [ ] Dashboards y alertas (tiempo aprobación, rechazos, certificados por expirar)
- [ ] Modo contingencia offline con sincronización posterior
- [ ] Auditoría de seguridad y cifrado de datos sensibles

## Fase 5 · QA y Lanzamiento
- [ ] Suite de pruebas end-to-end + escenarios de error DGII + stress tests
- [ ] Documentación técnica y guías de usuario/troubleshooting
- [ ] Piloto controlado con clientes y retroalimentación
- [ ] Plan de soporte post go-live (procedimientos y escalamiento)
- [ ] Ejecución proceso certificación DGII (FI-GDF-016, sets de prueba, declaración jurada)
- [ ] Plan de transición a producción (migraciones, capacitación)

## Operaciones Posteriores (`POST_ROADMAP_OPERACIONES.md`)
- [ ] Arquitectura multi-sitio y respaldos automáticos
- [ ] Plan BCP/DRP con pruebas trimestrales
- [ ] IAM y segregación de funciones, cumplimiento Ley 172-13
- [ ] Hardening y escaneos de vulnerabilidades periódicos
- [ ] Pen-tests y monitoreo centralizado (SIEM)
- [ ] SLA/SLI/SLO y runbooks de incidentes
- [ ] Turnos de soporte 24/7 y canales de escalamiento
- [ ] Pipelines canary/blue-green y comité normativo DGII/INDOTEL
- [ ] Documentación técnica (ADR, checklist releases)
- [ ] Entrenamiento continuo
- [ ] KPIs operativos y auditorías externas
- [ ] Informes regulatorios y repositorio de eventos

---

## Seguimiento
- [ ] Asignar responsables y fechas por tarea
- [ ] Revisiones semanales del estado del checklist
- [ ] Actualizar roadmap y plan operativo según avances y cambios normativos
