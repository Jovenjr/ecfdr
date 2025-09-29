# Fase 0 · Marco Legal y Normativo

## 1. Legislación Principal
- **Ley 32-23 de Facturación Electrónica**
  - Uso obligatorio del e-CF para personas físicas, jurídicas y entes sin personalidad jurídica en RD.
  - Establece el sistema fiscal de facturación electrónica, plazos de adopción y manejo de contingencias.
- **Decreto 587-24**
  - Reglamento de aplicación de la Ley 32-23.
  - Detalla plazos, fases de incorporación y obligaciones operativas.

## 2. Documentación Técnica DGII
- **Informe Técnico e-CF**: especificaciones de servicios web, estructuras XML/XSD y procesos de certificación.
- **Descripción Técnica de Facturación Electrónica**: lineamientos de implementación, seguridad y control tributario.
- **Guías de Representación Impresa (RI)**: requisitos de contenido mínimo, orden, código QR y código de seguridad.

## 3. Roles e-CF (Delegaciones)
- **Usuario Administrador e-CF**
  - Gestiona el registro de signatarios en la DGII (OFV).
  - Requiere certificado digital para procedimientos tributarios.
- **Firmante**
  - Persona física autorizada para firmar digitalmente los e-CF.
  - El número de serie (SN) del certificado debe corresponder a RNC/Cédula/Pasaporte.
- **Aprobador Comercial**
  - Gestiona aprobaciones/rechazos comerciales (ACECF).

## 4. Requisitos Previos DGII
1. Inscripción en el **Registro Nacional de Contribuyentes (RNC)**.
2. Acceso activo a la **Oficina Virtual (OFV)**.
3. **Alta de NCF** autorizada.
4. Certificado digital emitido por prestadora autorizada INDOTEL (ej. Viafirma, Digifirma).
5. Cumplimiento tributario al día.
6. Software de emisión disponible (ERPNext + módulo ECFDR).

## 5. Certificación DGII (Resumen)
- Completar formulario **FI-GDF-016** para solicitar registro como Emisor Electrónico.
- Acceder al portal de certificación con credenciales enviadas por DGII.
- Superar las etapas:
  - **Sets de Prueba** (datos, simulación, comunicación).
  - **Representación Impresa (RI)** en PDF ≤ 10MB.
  - **Declaración Jurada** firmada con App Firma Digital.
- Obtener habilitación de facturación electrónica en OFV (go-live).

## 6. Obligaciones de Conservación
- Almacenar e-CF y RI según plazos legales.
- Mantener bitácoras de contingencias (Serie B, envíos diferidos).
- Asegurar disponibilidad para auditorías DGII/INDOTEL.
