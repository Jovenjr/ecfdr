# Guía de Instalación CSF DO - República Dominicana

## 📋 Checklist de Instalación

### ✅ Pre-requisitos
- [ ] ERPNext v13 o superior instalado
- [ ] HRMS app instalado
- [ ] Acceso de administrador al sistema
- [ ] Certificado digital válido (opcional para pruebas)

### ✅ Instalación
1. **Instalar la aplicación**
   ```bash
   bench get-app https://github.com/navariltd/navari_csf_do.git
   bench --site <tu-sitio> install-app csf_do
   ```

2. **Verificar instalación**
   - Revisar que aparezca "CSF DO" en la lista de aplicaciones
   - Verificar que se crearon los roles: "Emisor e-CF", "Aprobador Comercial", "Administrador e-CF"

### ✅ Configuración Post-Instalación

#### 1. Configuración de Empresa
- [ ] Establecer país: República Dominicana
- [ ] Configurar moneda: DOP (Peso Dominicano)
- [ ] Configurar RNC de la empresa
- [ ] Configurar dirección fiscal

#### 2. Configuración DGII
- [ ] Crear registro en "DGII Configuration"
- [ ] Configurar URLs de ambiente (pre-certificación/certificación/producción)
- [ ] Configurar credenciales de API

#### 3. Certificado Digital
- [ ] Subir archivo .p12/.pfx del certificado
- [ ] Configurar contraseña del certificado
- [ ] Verificar vigencia del certificado

#### 4. Almacenes
- [ ] Verificar que existe "Almacén Principal - RD"
- [ ] Crear almacenes adicionales según necesidades

#### 5. Usuarios y Roles
- [ ] Asignar roles específicos a usuarios
- [ ] Configurar permisos por módulo

### ✅ Validación Final
- [ ] Ejecutar reporte de prueba
- [ ] Crear factura de prueba
- [ ] Verificar campos NCF
- [ ] Probar validaciones de RNC

## 🔧 Troubleshooting

### Problemas Comunes
1. **Error de versión**: Verificar que ERPNext sea v13+
2. **Roles no creados**: Ejecutar migración manual
3. **Certificado no válido**: Verificar formato y contraseña
4. **Campos NCF no aparecen**: Verificar instalación de fixtures

### Comandos de Diagnóstico
```bash
# Verificar estado de la aplicación
bench --site <sitio> console
>>> frappe.get_installed_apps()

# Verificar roles creados
>>> frappe.get_all("Role", filters={"is_custom": 1})

# Verificar configuración DGII
>>> frappe.get_all("DGII Configuration")
```

## 📞 Soporte
Para soporte técnico, contactar a: support@navari.co.ke
