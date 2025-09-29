# e-CF 43 - Gastos Menores Electrónico

## Descripción
El e-CF 43 es un comprobante fiscal electrónico para gastos menores en República Dominicana.

## Estructura de Campos

### Campos Requeridos

#### Encabezado
- **Version**: Versión del e-CF (debe ser "1.0")
- **IdDoc**: Información del documento
  - **TipoeCF**: Tipo de e-CF (debe ser 43)
  - **eNCF**: Número de Comprobante Fiscal (13 caracteres alfanuméricos)
  - **FechaVencimientoSecuencia**: Fecha de vencimiento (DD-MM-YYYY)
  - **TipoPago**: Tipo de pago (1=Contado, 2=Crédito, 3=Gratuito) - Opcional
- **Emisor**: Información del emisor
  - **RNCEmisor**: RNC del emisor (9 o 11 dígitos)
  - **RazonSocialEmisor**: Razón social (1-150 caracteres)
  - **DireccionEmisor**: Dirección (1-100 caracteres)
  - **FechaEmision**: Fecha de emisión (DD-MM-YYYY)
- **Totales**: Totales del documento
  - **MontoTotal**: Monto total (decimal >= 0)

#### DetallesItems
- **Item**: Lista de items (máximo 1000)
  - **NumeroLinea**: Número de línea (1-1000)
  - **IndicadorFacturacion**: Indicador de facturación (0-4)
  - **NombreItem**: Nombre del item (1-80 caracteres)
  - **IndicadorBienoServicio**: Tipo de item (1=Bien, 2=Servicio)
  - **CantidadItem**: Cantidad (decimal > 0)
  - **PrecioUnitarioItem**: Precio unitario (decimal >= 0)
  - **MontoItem**: Monto del item (decimal >= 0)

### Campos Opcionales

#### Subtotales
- **Subtotal**: Lista de subtotales (máximo 20)
  - **NumeroSubTotal**: Número del subtotal (1-99)
  - **DescripcionSubtotal**: Descripción (1-40 caracteres)
  - **Orden**: Orden del subtotal (1-99)
  - **SubTotalExento**: Subtotal exento (decimal >= 0)
  - **MontoSubTotal**: Monto del subtotal (decimal >= 0)
  - **Lineas**: Número de líneas (1-99)

#### Paginación
- **Pagina**: Lista de páginas (máximo 1000)
  - **PaginaNo**: Número de página (1-1000)
  - **NoLineaDesde**: Línea desde (1-1000)
  - **NoLineaHasta**: Línea hasta (1-1000)
  - **SubtotalExentoPagina**: Subtotal exento de la página (decimal >= 0)
  - **MontoSubtotalPagina**: Monto subtotal de la página (decimal >= 0)

#### Información de Referencia
- **NCFModificado**: NCF modificado (11-19 caracteres)
- **RNCOtroContribuyente**: RNC de otro contribuyente (9 o 11 dígitos)
- **FechaNCFModificado**: Fecha del NCF modificado (DD-MM-YYYY)
- **CodigoModificacion**: Código de modificación (1-5)

## Validaciones

### Formatos de Datos
- **eNCF**: 13 caracteres alfanuméricos
- **RNC**: 9 o 11 dígitos
- **Fecha**: DD-MM-YYYY
- **Email**: Formato válido de email (máximo 80 caracteres)
- **Teléfono**: XXX-XXX-XXXX

### Reglas de Negocio
- MontoItem debe ser igual a CantidadItem × PrecioUnitarioItem
- MontoTotal debe ser la suma de todos los MontoItem
- TipoeCF debe ser 43 para Gastos Menores
- Máximo 1000 items por documento
- Máximo 20 subtotales
- Máximo 1000 páginas

## Archivos Generados

1. **extractor_ecf43.py**: Script para extraer campos del XSD
2. **validador_ecf43.py**: Validador completo del e-CF 43
3. **plantilla_ecf43_basica.xml**: Plantilla XML básica
4. **plantilla_ecf43_basica.json**: Plantilla JSON básica
5. **ecf43_campos.json**: Campos extraídos en formato JSON
6. **documentacion_ecf43.md**: Esta documentación

## Uso

### Validar un e-CF 43
```python
from validador_ecf43 import ValidadorECF43

validador = ValidadorECF43()
es_valido, errores, advertencias = validador.validar_ecf43(datos_ecf43)
```

### Generar plantilla
```python
from generador_ecf43_completo import GeneradorECF43Completo

generador = GeneradorECF43Completo()
generador.generar_documentacion_completa()
```

## Notas Importantes

- El e-CF 43 es específico para gastos menores
- Todos los campos requeridos deben estar presentes
- Los campos opcionales pueden omitirse
- Las validaciones siguen el esquema XSD oficial
- Los montos deben ser coherentes entre sí
