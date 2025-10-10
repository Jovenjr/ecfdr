# ✅ Checklist Post-Instalación - Nuevas Características DGII

**Fecha**: _______________  
**Instalador**: _______________  
**Sitio**: _______________  

---

## 📋 Pasos de Instalación

### 1. ⚙️ Preparación

- [ ] **Backup de la base de datos**
  ```bash
  bench --site [sitio] backup
  ```

- [ ] **Verificar versión de csf_do**
  ```bash
  bench version
  # csf_do debe estar en v2.1.5+
  ```

- [ ] **Detener procesos**
  ```bash
  bench --site [sitio] scheduler disable
  ```

---

### 2. 🔄 Migración

- [ ] **Ejecutar migraciones**
  ```bash
  bench --site [sitio] migrate
  ```
  
- [ ] **Verificar sin errores**
  - Revisar output de migrate
  - No debe haber errores rojos
  - Warnings amarillos son aceptables

- [ ] **Reiniciar bench**
  ```bash
  bench restart
  ```

---

### 3. 📝 Custom Fields de ITBIS

- [ ] **Abrir consola de Frappe**
  ```bash
  bench --site [sitio] console
  ```

- [ ] **Ejecutar script**
  ```python
  from csf_do.install.setup_itbis_fields import create_itbis_validation_fields
  create_itbis_validation_fields()
  exit()
  ```

- [ ] **Verificar creación**
  - Ir a: Customize Form → Sales Invoice
  - Buscar sección "Validación ITBIS"
  - Debe tener campos: custom_itbis_validado, custom_itbis_rate, custom_itbis_amount
  
  - Repetir para Purchase Invoice

---

### 4. 🏢 Configurar DGII Configuration

- [ ] **Abrir DGII Configuration**
  - Inicio → DGII Configuration

- [ ] **Completar Información de la Empresa** (nueva sección)
  - [ ] Logo Empresa: Subir imagen PNG/JPG
  - [ ] Representante Legal: Nombre completo
  - [ ] Dirección Fiscal: Dirección completa
  - [ ] Teléfono Contacto: (809) 555-1234
  - [ ] Email Contacto: email@empresa.com

- [ ] **Guardar cambios**

---

### 5. 📄 Crear Series NCF

#### Serie B01 - Facturas de Crédito Fiscal

- [ ] **Crear nueva serie**
  - Inicio → NCF Series → New

- [ ] **Completar campos**:
  - Tipo NCF: `B01`
  - Serie: `A` (producción) o `B` (contingencia)
  - Compañía: Seleccionar compañía
  - Desde: `00000001`
  - Hasta: `01000000` (ejemplo 1 millón)
  - Fecha Autorización: Fecha de aprobación DGII
  - Fecha Vencimiento: Según autorización DGII

- [ ] **Guardar y verificar**
  - Estado debe ser "Activo"
  - Disponibles debe calcularse automáticamente

#### Serie B02 - Facturas de Consumo

- [ ] **Repetir proceso** con:
  - Tipo NCF: `B02`
  - Ajustar rango según necesidad

#### Otras Series (según necesidad)

- [ ] B03 - Notas de Débito
- [ ] B04 - Notas de Crédito
- [ ] B11 - Proveedores Informales
- [ ] B13 - Gastos Menores
- [ ] B14 - Régimen Especial
- [ ] B15 - Gubernamental
- [ ] B16 - Exportaciones

---

### 6. 📊 Verificar Dashboard DGII

- [ ] **Abrir Dashboard**
  - Inicio → Dashboard DGII

- [ ] **Verificar Tab Reportes**
  - [ ] Métricas cargan correctamente
  - [ ] e-CF Emitidos muestra número
  - [ ] Series NCF Activas muestra número
  - [ ] Tabla de e-CF recientes carga

- [ ] **Verificar Tab Series NCF**
  - [ ] Tabla muestra las series creadas
  - [ ] Columnas se visualizan correctamente
  - [ ] Estados tienen colores (Activo=verde, Vencido=rojo)

- [ ] **Verificar Tab Validaciones**
  - [ ] **Validador RNC**:
    - Probar con RNC: `123456789` (9 dígitos)
    - Debe mostrar resultado de validación
  
  - [ ] **Validador NCF**:
    - Probar con NCF: `B0100000001`
    - Debe desglosar: Serie, Tipo, Secuencia
  
  - [ ] **Calculadora ITBIS**:
    - Ingresar: `1000.00`
    - Debe calcular: Base=1000, ITBIS=180, Total=1180

---

### 7. 📑 Verificar Reporte IT-1

- [ ] **Abrir reporte**
  - Reportes → IT-1 Declaracion Jurada

- [ ] **Probar filtros**
  - Fecha Desde: Primer día del mes
  - Fecha Hasta: Último día del mes
  - Click "Mostrar"

- [ ] **Verificar funcionalidad**
  - [ ] Reporte se genera sin errores
  - [ ] Columnas se muestran correctamente
  - [ ] Botón "Export to Excel" aparece
  - [ ] Botón "Show Summary" aparece

- [ ] **Probar exportación**
  - Click "Export to Excel"
  - Archivo descarga correctamente
  - Abrir Excel y verificar formato

---

### 8. 🧪 Pruebas de Integración

#### Validación ITBIS en Factura

- [ ] **Crear Sales Invoice de prueba**
  - Cliente: Cualquiera
  - Item: Cualquiera
  - Cantidad: 1
  - Rate: 1000

- [ ] **Agregar ITBIS**
  - En Taxes, agregar "ITBIS - 18%"
  - Verificar que calcula 180

- [ ] **Submit factura**
  - No debe dar error
  - Si hay diferencia > 0.02, debe mostrar advertencia naranja
  - Verificar que sección "Validación ITBIS" se llenó:
    - ITBIS Validado: ✓
    - Tasa ITBIS: 18%
    - Monto ITBIS: 180.00

#### Generación de NCF

- [ ] **Probar API get_ncf_for_invoice**
  ```bash
  bench --site [sitio] console
  ```
  ```python
  from csf_do.csf_do.doctype.ncf_series.ncf_series import get_ncf_for_invoice
  ncf = get_ncf_for_invoice("B01", "Tu Compañía")
  print(ncf)  # Debe retornar: B0100000001 (o siguiente disponible)
  ```

- [ ] **Verificar incremento**
  - Llamar nuevamente get_ncf_for_invoice
  - Debe retornar siguiente número: B0100000002

---

### 9. 🔍 Verificación de Permisos

- [ ] **Roles con acceso**
  - [ ] System Manager: Acceso total
  - [ ] Accounts Manager: Acceso total
  - [ ] Accounts User: Acceso lectura
  - [ ] Emisor e-CF: Acceso NCF Series
  - [ ] Administrador e-CF: Acceso completo

- [ ] **Probar con usuario no privilegiado**
  - Logout
  - Login como Accounts User
  - Verificar que puede ver pero no modificar

---

### 10. 📧 Pruebas de Alertas

- [ ] **Alerta de vencimiento**
  - Crear serie NCF con fecha vencimiento en 15 días
  - Campo "alerta_vencimiento" debe marcarse automáticamente
  - En Dashboard, "Próximas a Vencer" debe incrementar

- [ ] **Serie agotada**
  - Crear serie con Desde=1, Hasta=5
  - Llamar get_ncf_for_invoice 5 veces
  - Estado debe cambiar a "Agotado"
  - Intentar obtener NCF #6 debe dar error

---

### 11. 🎨 Verificación de UI

- [ ] **Dashboard responsive**
  - Probar en diferentes tamaños de pantalla
  - Tabs funcionan correctamente
  - Métricas se alinean bien

- [ ] **Validadores interactivos**
  - Inputs aceptan texto
  - Botones responden al click
  - Resultados se muestran con colores correctos

---

### 12. 📊 Monitoreo Post-Instalación

- [ ] **Habilitar scheduler**
  ```bash
  bench --site [sitio] scheduler enable
  ```

- [ ] **Verificar logs**
  ```bash
  tail -f logs/[sitio].log
  ```
  - No debe haber errores relacionados con NCF Series
  - No debe haber errores en validadores

- [ ] **Crear test automatizado** (opcional)
  ```bash
  bench --site [sitio] run-tests --module csf_do
  ```

---

## 📝 Notas y Observaciones

### Problemas Encontrados

```
Fecha: ___________
Problema: _____________________________________________
Solución: _____________________________________________
```

### Configuraciones Personalizadas

```
- Serie NCF creadas: ___________
- Rangos asignados: ___________
- Modo API: simulator / test / production
```

---

## ✅ Checklist Final

- [ ] Todas las migraciones ejecutadas sin errores
- [ ] Custom fields de ITBIS creados
- [ ] DGII Configuration completada
- [ ] Al menos 2 series NCF creadas (B01, B02)
- [ ] Dashboard DGII accesible
- [ ] Todas las validaciones funcionando
- [ ] Reporte IT-1 generando correctamente
- [ ] Prueba de factura con ITBIS exitosa
- [ ] Generación de NCF probada
- [ ] Permisos verificados
- [ ] Scheduler habilitado
- [ ] Logs sin errores

---

## 📞 Soporte

En caso de problemas:

1. **Revisar logs**:
   ```bash
   tail -f logs/[sitio].log
   bench console
   ```

2. **Verificar configuración**:
   - DGII Configuration completa
   - Series NCF con fechas válidas
   - Permisos de roles correctos

3. **Re-migrar si es necesario**:
   ```bash
   bench --site [sitio] migrate --skip-failing
   ```

4. **Contactar soporte**:
   - Documentación: `IMPLEMENTACION_DGII_FEATURES.md`
   - Pruebas: `PRUEBA_FRAPPE_MCP_EXITOSA.md`

---

**Instalación Completada**: [ ] Sí  [ ] No  
**Fecha**: _______________  
**Firma**: _______________

---

**Versión**: csf_do v2.1.5+  
**Checklist v1.0** - 10 de octubre, 2025
