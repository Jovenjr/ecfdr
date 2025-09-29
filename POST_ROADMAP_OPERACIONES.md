# Plan Operativo Posterior al Roadmap ECFDR

## Objetivo
Establecer las actividades de operaciones, seguridad, continuidad y soporte necesarias para sostener en producción el servicio de facturación electrónica ERPNext + DGII, una vez completadas las fases del `ROADMAP_ECFDR.md`.

---

## 1. Arquitectura de Infraestructura
- **[Topología]** Diseñar arquitectura multi-sitio (producción primario/secundario) con balanceadores y redundancia de bases de datos Frappe/ERPNext.
- **[Escalabilidad]** Definir estándares de autoescalado (Horizonte y vertical) para colas de trabajos (Redis), servidores web y workers de firma.
- **[Aislamiento]** Segmentar ambientes (DEV/STG/CERT/PROD) con controles de red y VPN para conectividad segura con DGII.
- **[Backup & Restore]** Implementar respaldos automáticos (full + incrementales) de base de datos y archivos (XML firmados, certificados). Documentar procedimientos de restauración.

## 2. Continuidad del Negocio y Recuperación de Desastres
- **[BCP/DRP]** Elaborar planes formales con RPO/RTO objetivos (ej. RPO ≤ 1h, RTO ≤ 4h) y escenarios: caída de sitio, pérdida de certificados, indisponibilidad DGII.
- **[Pruebas de contingencia]** Ejecutar simulacros trimestrales de DR: failover a sitio secundario, recuperación de datos, envío masivo post-contingencia.
- **[Modo offline]** Operacionalizar el modo contingencia descrito en `ROADMAP_ECFDR.md` con políticas de sincronización y auditoría.

## 3. Seguridad y Cumplimiento
- **[Gestión de accesos]** Configurar IAM (roles privilegiados, MFA, rotación de contraseñas) y segregación de funciones (Administrador e-CF, Firmante, Auditor).
- **[Protección de datos]** Aplicar cifrado en reposo (base de datos, FileStore) y en tránsito (TLS 1.2+). Revisar cumplimiento con Ley 172-13 de protección de datos personales.
- **[Hardening]** Mantener parches de sistema operativo, dependencias y librerías criptográficas. Implementar escaneos de vulnerabilidades periódicos.
- **[Penetration testing]** Programar pruebas anuales (internas/terceros) sobre APIs, portales internos y endpoints expuestos.
- **[Registro y monitoreo]** Centralizar logs (SIEM) con alertas de uso indebido, errores DGII, anomalías de firma y accesos sospechosos.

## 4. Operación 24/7 y Soporte
- **[SLA/SLI/SLO]** Definir métricas objetivo (disponibilidad ≥ 99.5%, latencia envíos ≤ 5 min, tasa rechazos DGII ≤ 2%) y monitorear en dashboards.
- **[Runbooks]** Crear manuales operativos para incidentes comunes (errores token, expiración certificado, rechazo masivo DGII, fallos de colas).
- **[Soporte]** Establecer turnos (NOC) y canales de escalamiento (L1/L2/L3), integrados con herramientas de ticketing.
- **[Comunicación DGII]** Mantener contacto con mesa de ayuda DGII para incidentes mayores y programar ventanas de mantenimiento.

## 5. Gestión del Cambio y Actualizaciones
- **[Proceso de despliegue]** Implementar pipelines CANARY/BLUE-GREEN para actualizaciones de ERPNext, builders XML y catálogos DGII.
- **[Gestión normativa]** Formalizar comité que revise boletines DGII e INDOTEL, actualice XSD/catálogos y planifique adaptaciones.
- **[Documentación técnica]** Mantener repositorio de decisiones (ADR), manuales versionados y checklist de release.
- **[Entrenamiento continuo]** Ofrecer capacitaciones periódicas al personal operativo y usuarios clave sobre cambios normativos y de plataforma.

## 6. Métricas y Auditoría Continua
- **[KPIs operativos]** Seguimiento de métricas: tiempo aprobación, cola de pendientes, integridad de reconciliaciones ITBIS/ISR, expiración de certificados.
- **[Auditorías externas]** Coordinar revisiones anuales con auditores fiscales/tecnológicos para validar cumplimiento DGII y seguridad.
- **[Informes regulatorios]** Generar reportes de eventos (contingencias, rechazos críticos) y archivarlos según requisitos DGII/INDOTEL.

---

## Roadmap de Implementación Post-Go-Live
1. **Mes 1:** Implementar monitoreo avanzado, respaldos automáticos y runbooks críticos.
2. **Mes 2:** Completar pruebas DR, endurecimiento de infraestructura y capacitación de soporte.
3. **Mes 3:** Ejecutar primera auditoría de seguridad, iniciar comité normativo y calendarizar pruebas de penetración.
4. **Mes 4+:** Revisiones trimestrales de KPIs, ejercicios DR semestrales, auditorías anuales y actualización continua conforme a cambios DGII.

---

## Dependencias y Responsables
- **Equipos involucrados:** Operaciones TI, Seguridad, Desarrollo ERPNext, QA, Legal/Compliance.
- **Herramientas clave:** SIEM/monitoring (Grafana/Prometheus, ELK), ticketing (Jira/ServiceDesk), repositorio Git, sistemas de backup, App Firma Digital DGII.

## Próximos Pasos
- Designar responsables por cada capítulo operativo.
- Elaborar cronograma detallado con hitos y presupuesto.
- Integrar el plan con los entregables finales de `ROADMAP_ECFDR.md` antes del go-live.
