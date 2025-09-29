# Fase 0 · Matriz de Pruebas DGII

## Escenarios principales
| # | Escenario | Rol | Descripción | Servicios DGII involucrados | Resultado esperado |
|---|-----------|-----|-------------|------------------------------|--------------------|
| 1 | Envío normal e-CF | Emisor | Generar e-CF tipo 31 firmado y enviarlo | `/autenticacion`, `/recepcion`, `/consultaresultado` | TrackId válido y estado `Aceptado` o `Aceptado Condicional` |
| 2 | Envío e-CF con error de negocio | Emisor | Enviar e-CF con datos inconsistentes | `/recepcion`, `/consultaresultado` | Estado `Rechazado` con códigos y mensajes específicos |
| 3 | Recepción e-CF | Receptor | Recibir e-CF y registrar en ERPNext | `/consultadirectorio` (para emulador) | Documento recibido y almacenado |
| 4 | Acuse de Recibo (ARECF) | Receptor | Generar y enviar ARECF firmado | `/recepcion` (endpoint emisor simulado) | Confirmación de recepción registrada |
| 5 | Aprobación Comercial (ACECF) | Receptor | Enviar aceptación/rechazo comercial | `/recepcion` / `/aprobacion` | Respuesta registrada en DGII |
| 6 | Resumen RFCE | Emisor | Agregar facturas tipo 32 < RD$250k y enviar resumen | `/recepcionfc/` | TrackId RFCE y estado `Aceptado` |
| 7 | Anulación e-NCF (ANECF) | Emisor | Anular secuencia no usada / e-CF no enviado | `/anulacion` | TrackId ANECF y confirmación |
| 8 | Nota de Crédito (Tipo 34) | Emisor | Anular e-CF enviado | `/recepcion`, `/consultaresultado` | Estado `Aceptado` y relación con e-CF original |
| 9 | Contingencia offline | Emisor | Generar e-CF sin conexión y enviar < 72h después | `/recepcion` (diferido) | Registro de contingencia y aceptación |
| 10 | Contingencia Serie B | Emisor | Emitir NCF físico y sustituir por e-CF en <30 días | `/recepcion` | e-CF sustituto aceptado y bitácora actualizada |

## Datos de prueba
- **Catálogos**: usar valores vigentes DGII (monedas, unidades, provincias).
- **Rangos e-NCF**: registrar rangos autorizados por tipo.
- **Certificados**: firmas PKCS#12 sandbox con password controlada.
- **Contrapartes**: usar directorio DGII de contribuyentes simulados.

## Evidencias requeridas
- XML enviado y respuesta DGII (TrackId, estado).
- Logs de firma (hash, SN certificado).
- Capturas o registros de RI PDF generada.
- Bitácora de contingencia (fecha, motivo, resolución).

## Calendario sugerido
- Semana 1: Escenarios 1,2,6.
- Semana 2: Escenarios 3-5.
- Semana 3: Escenarios 7-10.

## Criterios de aceptación
- 0 errores críticos sin plan de acción.
- Validaciones XSD superadas en 100% de escenarios.
- ARECF/ACECF implementados y firmados.
- Contingencia documentada con tiempos < umbrales legales.
