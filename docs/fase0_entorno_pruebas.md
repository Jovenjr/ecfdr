# Fase 0 · Entorno ERPNext Staging y DGII TesteCF

## 1. Requisitos Previos
- **Credenciales DGII**: Solicitar y recibir usuario/clave del portal TesteCF tras enviar formulario FI-GDF-016.
- **Certificado Digital**: Instalar certificado INDOTEL (PKCS#12) en servidor de staging con almacenamiento seguro.
- **ERPNext Staging**: Instancia aislada (subdominio o sitio) alineada a versión de producción.

## 2. Configuración de ERPNext
- **Sitio**: `stg-ecfdr.local` (ejemplo) con base de datos independiente.
- **Apps instaladas**: `frappe`, `erpnext`, `csf_do`.
- **Variables env** (`.env`): rutas a certificados, flags de ambiente `PRECERT`.
- **DGII Configuration**: Registrar base URLs del ambiente TesteCF y credenciales temporales.

## 3. URLs DGII Pre-certificación
| Servicio | Descripción | URL base |
|----------|-------------|----------|
| Autenticación | Obtener token (validez ~1h) | `https://ecf.dgii.gov.do/testecf/autenticacion` |
| Recepción e-CF | Envío de e-CF firmados (TrackId) | `https://ecf.dgii.gov.do/testecf/recepcion` |
| Recepción RFCE | Envío resumen facturas consumo < RD$250k | `https://fc.dgii.gov.do/testecf/recepcionfc/` |
| Consulta Directorio | Directorio de contribuyentes simulados | `https://ecf.dgii.gov.do/testecf/consultadirectorio` |
| Consulta Resultado | Estado por TrackId | `https://ecf.dgii.gov.do/testecf/consultaresultado` |
| Consulta Estado | Estado resumido | `https://ecf.dgii.gov.do/testecf/consultaestado` |

## 4. Seguridad del Entorno
- **TLS**: Validar certificados DGII y habilitar verificación (`verify_ssl=True`).
- **Segregación**: Acceso restringido via VPN/whitelist.
- **Logs**: Centralizar logs de requests/responses para auditoría.

## 5. Procedimientos Operativos
- **Rotación de credenciales**: Cambio cada 90 días o según DGII.
- **Sincronización**: Depurar datos del sitio staging periódicamente.
- **Backup**: Respaldos diarios de DB y archivos XML.

## 6. Checklist de Puesta en Marcha
- [ ] Instancia ERPNext staging creada.
- [ ] Certificado digital instalado y protegido.
- [ ] URLs TesteCF registradas en `DGIIConfiguration`.
- [ ] Credenciales TesteCF almacenadas en vault seguro.
- [ ] Logging y monitoreo habilitados.
- [ ] Procedimientos de backup documentados.
