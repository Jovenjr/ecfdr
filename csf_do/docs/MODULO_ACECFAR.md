# Módulo ACECFAR - Recepción de e-CF

## Descripción

El **Módulo ACECFAR** permite recibir, validar y procesar e-CF (Comprobantes Fiscales Electrónicos) de proveedores, creando automáticamente Purchase Invoices en ERPNext.

**ACECFAR** = Acuse de Recibo de Comprobante Fiscal

---

## Características

✅ **Recepción de e-CF** de proveedores  
✅ **Parseo completo de XML** según estándar DGII  
✅ **Validación de firma digital** XMLDSig  
✅ **Validación de certificados** X.509  
✅ **Creación automática** de Purchase Invoice  
✅ **Creación automática** de Suppliers  
✅ **Creación automática** de Items  
✅ **Envío de acuse de recibo** a DGII  
✅ **Workflow de aprobación/rechazo**  
✅ **Múltiples métodos de recepción** (email, upload, API)  

---

## Arquitectura

```
e-CF XML (Proveedor)
        ↓
   Parser XML
        ↓
Validador de Firma
        ↓
  e-CF Recibido (DocType)
        ↓
    Procesador
        ↓
   ┌────┴────┐
   ↓         ↓
Supplier  Purchase Invoice
   ↓
Acuse de Recibo → DGII
```

---

## Componentes

### 1. Parser de XML (`acecfar_parser.py`)

Parsea el XML del e-CF y extrae toda la información:

```python
from csf_do.csf_do.utils.acecfar_parser import parse_ecf_xml

# Parsear XML
parsed_data = parse_ecf_xml(xml_content)

# Resultado:
{
    'header': {
        'tipo_ecf': '31',
        'encf': 'B0100000001',
        'fecha_emision': '2025-01-10',
        ...
    },
    'emisor': {
        'rnc': '131793916',
        'razon_social': 'Proveedor S.A.',
        ...
    },
    'items': [
        {
            'descripcion_item': 'Producto X',
            'cantidad_item': 10,
            'precio_unitario': 1000,
            ...
        }
    ],
    'totales': {
        'monto_total': 11800,
        'total_itbis': 1800,
        ...
    }
}
```

**Datos extraídos:**
- Encabezado (tipo, NCF, fechas)
- Emisor (RNC, nombre, dirección, contacto)
- Comprador (nuestra empresa)
- Ítems (descripción, cantidad, precio, impuestos)
- Totales (monto total, ITBIS, exentos)
- Información adicional
- Firma digital

### 2. Validador de Firma (`signature_validator.py`)

Valida la firma digital XMLDSig del e-CF:

```python
from csf_do.csf_do.utils.signature_validator import validate_ecf_signature

# Validar firma
result = validate_ecf_signature(xml_content)

# Resultado:
{
    'valid': True,
    'signature_present': True,
    'certificate_valid': True,
    'signature_verified': True,
    'certificate_info': {
        'subject': 'CN=Proveedor, O=Empresa',
        'issuer': 'CN=DGII CA',
        'not_valid_before': '2024-01-01',
        'not_valid_after': '2026-01-01'
    },
    'errors': []
}
```

**Validaciones:**
- ✅ Presencia de firma digital
- ✅ Validez del certificado (fechas)
- ✅ Propósito del certificado (firma digital)
- ✅ Integridad del XML (no modificado)
- ⏳ Cadena de confianza (TODO)
- ⏳ Revocación (CRL/OCSP) (TODO)

**Modo Simulador:**
En modo desarrollo, el validador acepta cualquier firma como válida para facilitar testing.

### 3. Procesador (`acecfar_processor.py`)

Procesa el e-CF y crea Purchase Invoice:

```python
from csf_do.csf_do.integrations.acecfar_processor import process_ecf_from_xml

# Procesar e-CF
result = process_ecf_from_xml(xml_content, validate_signature=True)

# Resultado:
{
    'success': True,
    'purchase_invoice': 'PINV-2025-00001',
    'ecf_recibido': 'ECF-REC-2025-00001',
    'errors': [],
    'warnings': []
}
```

**Proceso:**
1. Parsea el XML
2. Valida la firma digital (opcional)
3. Crea registro "e-CF Recibido"
4. Verifica si ya existe PI para este e-CF
5. Obtiene o crea Supplier
6. Crea Purchase Invoice
7. Mapea ítems y totales
8. Actualiza estado del e-CF Recibido

### 4. DocType "e-CF Recibido"

Registro de e-CF recibidos de proveedores.

**Campos principales:**
- e-NCF (único)
- Tipo de e-CF
- Fecha de emisión
- Estado (Pendiente, Validado, Procesado, Rechazado)
- RNC y Razón Social del emisor
- Montos (total, gravado, ITBIS, exento)
- Firma válida (check)
- Purchase Invoice vinculada
- XML original
- Acuse enviado

**Estados:**
- **Pendiente**: Recibido, esperando procesamiento
- **Validado**: Firma y estructura válidas
- **Procesado**: Purchase Invoice creada
- **Rechazado**: Rechazado por usuario
- **Duplicado**: Ya existe PI para este e-CF
- **Error**: Error en procesamiento

---

## Uso

### Recibir e-CF Manualmente

1. Ir a **e-CF Recibido** → **Nuevo**
2. Subir archivo XML o pegar contenido
3. Click en **Procesar**
4. Sistema crea automáticamente:
   - Supplier (si no existe)
   - Items (si no existen)
   - Purchase Invoice

### Recibir e-CF por API

```python
import frappe

@frappe.whitelist(allow_guest=True)
def recibir_ecf_api(xml_content: str, api_key: str):
    """Endpoint para recibir e-CF vía API"""
    
    # Validar API key
    if not validate_api_key(api_key):
        return {'success': False, 'error': 'API key inválida'}
    
    # Procesar e-CF
    from csf_do.csf_do.integrations.acecfar_processor import process_ecf_from_xml
    
    result = process_ecf_from_xml(xml_content)
    return result
```

### Recibir e-CF por Email

Configurar regla de email:

1. Ir a **Email Rule** → **Nuevo**
2. Configurar:
   - **Email Account**: Cuenta de recepción
   - **Condition**: Asunto contiene "e-CF" o "Factura Electrónica"
   - **Action**: Ejecutar script Python

```python
# Script de Email Rule
from csf_do.csf_do.integrations.acecfar_processor import process_ecf_from_xml

# Buscar adjuntos XML
for attachment in email.attachments:
    if attachment.file_name.endswith('.xml'):
        xml_content = attachment.get_content()
        
        # Procesar
        result = process_ecf_from_xml(xml_content)
        
        if result.get('success'):
            frappe.sendmail(
                recipients=[email.from_email],
                subject="Acuse de Recibo - " + result.get('ecf_recibido'),
                message="Su e-CF ha sido recibido y procesado correctamente."
            )
```

### Validar Firma Digital

```python
# Desde el DocType e-CF Recibido
frappe.call({
    method: 'csf_do.csf_do.doctype.ecf_recibido.ecf_recibido.validar_firma',
    args: {
        name: 'ECF-REC-2025-00001'
    },
    callback: function(r) {
        if (r.message.valid) {
            frappe.msgprint('Firma válida');
        } else {
            frappe.msgprint('Firma inválida: ' + r.message.errors.join(', '));
        }
    }
});
```

### Enviar Acuse de Recibo

```python
# Desde el DocType e-CF Recibido
frappe.call({
    method: 'csf_do.csf_do.doctype.ecf_recibido.ecf_recibido.enviar_acuse',
    args: {
        name: 'ECF-REC-2025-00001',
        estado: 'ACEPTADO',  // o 'RECHAZADO'
        motivo: ''  // Solo si es rechazado
    },
    callback: function(r) {
        if (r.message.success) {
            frappe.msgprint('Acuse enviado exitosamente');
        }
    }
});
```

---

## Workflow Recomendado

### Flujo Automático (Recomendado)

1. **Recepción**: e-CF llega por email/API
2. **Parseo**: Sistema parsea XML automáticamente
3. **Validación**: Valida firma digital
4. **Creación**: Crea PI automáticamente
5. **Notificación**: Notifica a Accounts User
6. **Revisión**: Usuario revisa PI
7. **Aprobación**: Usuario aprueba/rechaza
8. **Acuse**: Sistema envía acuse a DGII

### Flujo Manual (Control Total)

1. **Recepción**: Usuario sube XML manualmente
2. **Registro**: Se crea e-CF Recibido en estado "Pendiente"
3. **Validación**: Usuario valida firma
4. **Revisión**: Usuario revisa datos parseados
5. **Procesamiento**: Usuario click en "Procesar"
6. **Creación**: Sistema crea PI
7. **Ajustes**: Usuario ajusta PI si necesario
8. **Aprobación**: Usuario aprueba PI
9. **Acuse**: Usuario envía acuse

---

## Mapeo de Datos

### Supplier

| e-CF | ERPNext Supplier |
|------|------------------|
| RNC Emisor | Tax ID |
| Razón Social | Supplier Name |
| Dirección | Address |
| Teléfono | Phone |
| Correo | Email |

### Purchase Invoice

| e-CF | ERPNext PI |
|------|------------|
| e-NCF | NCF |
| Tipo e-CF | NCF Type |
| Fecha Emisión | Posting Date |
| Fecha Vencimiento | Due Date |
| Monto Total | Grand Total |

### Items

| e-CF | ERPNext Item |
|------|--------------|
| Código Producto | Item Code |
| Descripción | Item Name |
| Cantidad | Qty |
| Precio Unitario | Rate |
| Monto | Amount |

---

## Testing con Simulador

El simulador DGII puede generar e-CF de prueba:

```python
from csf_do.csf_do.integrations.dgii_simulator import DGIISimulator

simulator = DGIISimulator()

# Generar e-CF de proveedor
xml = simulator.generar_ecf_proveedor(
    supplier_rnc="131793916",
    amount=11800.00
)

# Procesar
from csf_do.csf_do.integrations.acecfar_processor import process_ecf_from_xml

result = process_ecf_from_xml(xml, validate_signature=False)

print(f"Purchase Invoice: {result['purchase_invoice']}")
```

---

## Configuración

### Habilitar Recepción Automática

1. Ir a **DGII Settings**
2. Sección "ACECFAR"
3. Habilitar "Auto Process Received e-CF"
4. Configurar email de recepción
5. Guardar

### Configurar Validación de Firma

1. Ir a **DGII Settings**
2. Sección "ACECFAR"
3. Habilitar "Validate Signature"
4. En modo simulador, siempre válida
5. En producción, valida con certificados reales

---

## Troubleshooting

### Error: "RNC del emisor no encontrado"

**Causa**: XML no contiene RNC del emisor  
**Solución**: Verificar que el XML sea válido

### Error: "Ya existe Purchase Invoice para este e-CF"

**Causa**: e-CF ya fue procesado anteriormente  
**Solución**: Verificar en Purchase Invoice list

### Warning: "Firma digital no válida"

**Causa**: Certificado expirado o firma incorrecta  
**Solución**: 
- En desarrollo: Usar modo simulador
- En producción: Contactar al proveedor

### Error: "Monto total difiere"

**Causa**: Diferencia en cálculo de totales  
**Solución**: Revisar mapeo de impuestos

---

## Próximas Mejoras

- [ ] Buzón SFTP para recepción masiva
- [ ] Validación de cadena de confianza de certificados
- [ ] Verificación de revocación (CRL/OCSP)
- [ ] Reconciliación automática con Purchase Orders
- [ ] Detección de duplicados inteligente
- [ ] Dashboard de e-CF recibidos
- [ ] Reportes de recepción

---

## API Reference

### Funciones Públicas

```python
# Parser
parse_ecf_xml(xml_content: str) -> Dict

# Validador
validate_ecf_signature(xml_content: str, use_simulator: bool) -> Dict
get_certificate_info(xml_content: str) -> Dict

# Procesador
process_ecf_from_xml(xml_content: str, validate_signature: bool) -> Dict
process_ecf_from_file(file_url: str) -> Dict
reprocess_ecf_recibido(ecf_recibido_name: str) -> Dict

# DocType
procesar_ecf(name: str) -> Dict
enviar_acuse(name: str, estado: str, motivo: str) -> Dict
validar_firma(name: str) -> Dict
```

---

**Última actualización**: 10 de Enero, 2025  
**Versión**: 1.0.0  
**Estado**: ✅ Implementado y funcional
