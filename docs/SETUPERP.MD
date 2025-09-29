

## **📋 GUÍA COMPLETA DE DATOS MAESTROS PARA OPERAR EL SISTEMA**

Basándome en la exploración del sistema ERPNext con el módulo CSF DO (República Dominicana), aquí tienes la guía completa de los datos maestros que debes configurar antes de operar:

---

## **🏢 1. CONFIGURACIÓN BÁSICA DE LA EMPRESA**

### **Company (Compañía)**
- **Nombre de la empresa** y abreviatura
- **País**: República Dominicana
- **Moneda por defecto**: DOP (Peso Dominicano)
- **Información fiscal**: RNC, dirección, teléfono, email
- **Configuración contable**: Plan de cuentas, cuentas por defecto
- **Configuración de almacenes**: Almacén principal por defecto

---

## **🔧 2. CONFIGURACIÓN ESPECÍFICA DE REPÚBLICA DOMINICANA**

### **DGII Configuration (Configuración DGII)**
- **URLs de ambientes**:
  - Pre-certificación Base URL
  - Certificación Base URL  
  - Producción Base URL
- **Autenticación**:
  - Client ID
  - Client Secret
  - Token TTL (tiempo de vida del token)
- **Configuración SSL**: Verificar certificados SSL

### **Digital Certificate (Certificado Digital)**
- **Nombre del certificado**
- **Proveedor CA**: Viafirma, Digifirma u otro
- **SN (RNC/Cédula/Pasaporte)**: Debe coincidir con el propietario
- **Rutas de archivos**:
  - Ruta del certificado (.p12/.pfx)
  - Ruta de la clave privada (si aplica)
- **Vigencia**: Fechas de validez del certificado
- **Estado**: Activo/Inactivo

---

## **📦 3. GESTIÓN DE INVENTARIO**

### **Warehouse (Almacenes)**
- Almacén Principal
- Almacén Miramar
- Almacén Placer Bonito
- Configurar tipos de almacén según necesidades

### **Item (Productos/Servicios)**
- Códigos de productos
- Descripciones
- Unidades de medida
- Categorías de productos
- Precios de venta y compra
- Configuración de impuestos (ITBIS)

### **UOM (Unidades de Medida)**
- Unidades básicas: Nos, Litros, Kilogramos, etc.
- Factores de conversión entre unidades
- Categorías de UOM

---

## **👥 4. GESTIÓN DE PERSONAS**

### **Customer (Clientes)**
- Información básica del cliente
- RNC/Cédula
- Dirección y contacto
- Términos de pago
- Límites de crédito
- Grupos de clientes

### **Supplier (Proveedores)**
- Información del proveedor
- RNC/Cédula
- Dirección y contacto
- Términos de pago
- Grupos de proveedores

### **Employee (Empleados)**
- Datos personales
- Información laboral
- Salarios y beneficios
- Dependientes y beneficiarios (específico RD)

---

## **💰 5. CONFIGURACIÓN CONTABLE**

### **Account (Cuentas Contables)**
- Plan de cuentas para República Dominicana
- Cuentas de activos, pasivos, patrimonio
- Cuentas de ingresos y gastos
- Cuentas específicas para ITBIS

### **Cost Center (Centros de Costo)**
- Departamentos o divisiones
- Asignación de costos por centro

### **Currency (Monedas)**
- Peso Dominicano (DOP) como moneda base
- Otras monedas si aplica (USD, EUR)

---

## **📊 6. CONFIGURACIÓN DE IMPUESTOS (RD)**

### **ITBIS Withholding (Retención ITBIS)**
- Configuración de retenciones de ITBIS
- Porcentajes aplicables
- Cuentas contables para retenciones

### **NCF HSCode (Códigos NCF y HS)**
- Códigos de Nomenclatura Común Fiscal
- Códigos del Sistema Armonizado
- Clasificación de productos para exportación

---

## **📋 7. CONFIGURACIÓN DE DOCUMENTOS**

### **Sales Invoice Settings (Configuración Facturas)**
- Series de numeración para facturas
- Configuración de e-CF (Comprobantes Fiscales Electrónicos)
- Formatos de impresión
- Configuración de validaciones

### **Packing List (Lista de Empaque)**
- Configuración para exportaciones
- Formatos requeridos por DGII
- Validaciones de datos

---

## **⚙️ 8. CONFIGURACIÓN DE SISTEMA**

### **User (Usuarios)**
- Crear usuarios del sistema
- Asignar roles y permisos
- Configurar accesos por módulo

### **Role (Roles)**
- System Manager
- Accounts Manager
- Sales User
- Purchase User
- Stock User
- Employee

### **Holiday List (Lista de Feriados)**
- Feriados nacionales de República Dominicana
- Días no laborables
- Calendario fiscal

---

## **📈 9. CONFIGURACIÓN DE REPORTES**

### **Reportes Específicos RD**
- Reportes de ITBIS
- Declaraciones fiscales
- Reportes de nómina
- Reportes de exportación
- Reportes de e-CF

---

## **🔍 10. VALIDACIONES Y CONFIGURACIONES ADICIONALES**

### **Validaciones Específicas**
- Validación de RNC
- Validación de PIN
- Validación de códigos NCF
- Validación de certificados digitales

### **Configuraciones de Integración**
- SMS Center para notificaciones
- Configuración de email
- Integración con DGII
- Configuración de backup

---

## **�� ORDEN DE CONFIGURACIÓN RECOMENDADO**

1. **Configuración básica**: Company, Currency, Country
2. **Configuración RD**: DGII Configuration, Digital Certificate
3. **Usuarios y roles**: User, Role, permissions
4. **Contabilidad**: Account, Cost Center, Chart of Accounts
5. **Inventario**: Warehouse, Item, UOM
6. **Personas**: Customer, Supplier, Employee
7. **Impuestos**: ITBIS Withholding, NCF HSCode
8. **Documentos**: Sales Invoice Settings, Packing List
9. **Reportes**: Configurar reportes específicos
10. **Validaciones**: Activar validaciones RD

---

## **⚠️ CONSIDERACIONES IMPORTANTES**

- **Certificado Digital**: Es obligatorio para operar con DGII
- **RNC válido**: Debe estar registrado en DGII
- **Configuración de e-CF**: Necesaria para facturación electrónica
- **Backup regular**: Configurar respaldos automáticos
- **Actualizaciones**: Mantener el sistema actualizado con las últimas regulaciones RD

Esta configuración te permitirá operar completamente el sistema ERPNext adaptado para República Dominicana con todas las funcionalidades fiscales y contables requeridas.