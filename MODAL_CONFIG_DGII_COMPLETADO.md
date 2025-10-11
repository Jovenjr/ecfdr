# ✅ Modal Configuración DGII - Implementación Completada

**Fecha:** 10 de octubre de 2025  
**Archivo:** `src/pages/DGII.tsx` (líneas 1462-1677)  
**Estado:** ✅ Completado

---

## 📋 Componentes Implementados

### 1. **Dialog Modal Component** 🎯

```tsx
<Dialog open={isConfigModalOpen} onOpenChange={setIsConfigModalOpen}>
  <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
    <DialogHeader>
      <DialogTitle>
        <Shield /> Configuración DGII
      </DialogTitle>
    </DialogHeader>
    {/* Form fields */}
  </DialogContent>
</Dialog>
```

**Características:**
- ✅ Modal responsive de 2xl (max-width: 672px)
- ✅ Scroll vertical automático (max-h: 90vh)
- ✅ Cierre con backdrop click
- ✅ Header con iconografía Shield
- ✅ Descripción contextual

---

### 2. **Selector de Modo API** 🎛️

```tsx
<Select value={configFormData.modo_api}>
  <SelectItem value="Simulator">
    🔵 Simulator - Pruebas locales
  </SelectItem>
  <SelectItem value="Testing">
    🟡 Testing - Ambiente de pruebas DGII
  </SelectItem>
  <SelectItem value="Production">
    🔴 Production - Ambiente productivo DGII
  </SelectItem>
</Select>
```

**Modos Disponibles:**

| Modo | Color | Descripción | Requiere Credenciales | Requiere Certificado |
|------|-------|-------------|----------------------|---------------------|
| **Simulator** | 🔵 Gris | Pruebas locales sin conexión real | ❌ No | ❌ No |
| **Testing** | 🟡 Naranja | Servidor de pruebas DGII | ✅ Sí | ✅ Sí |
| **Production** | 🔴 Rojo | Ambiente productivo DGII | ✅ Sí | ✅ Sí |

**Indicadores Visuales:**
- Cada opción tiene un círculo de color (`rounded-full bg-{color}-500`)
- Texto descriptivo debajo del selector
- Emojis informativos según modo seleccionado

---

### 3. **Credenciales DGII** 🔐

```tsx
<div className="grid grid-cols-2 gap-4">
  <Input 
    id="dgii-username"
    placeholder="usuario@empresa.com"
    disabled={configFormData.modo_api === 'Simulator'}
  />
  <Input 
    id="dgii-password"
    type="password"
    placeholder="••••••••"
    disabled={configFormData.modo_api === 'Simulator'}
  />
</div>
```

**Características:**
- ✅ Layout en grid 2 columnas
- ✅ Input de password enmascarado
- ✅ Disabled automático en modo Simulator
- ✅ Validación en backend (no se carga password existente por seguridad)

---

### 4. **Información Fiscal** 🏢

```tsx
<div className="space-y-4">
  <h4>
    <FileText /> Información Fiscal
  </h4>
  
  <Input 
    id="rnc-empresa"
    maxLength={11}
    placeholder="123456789"
    required
  />
  
  <Input 
    id="nombre-comercial"
    placeholder="Empresa SRL"
    required
  />
  
  <Input 
    id="direccion-fiscal"
    placeholder="Calle Principal #123, Santo Domingo"
  />
</div>
```

**Campos:**
- **RNC Empresa** (*): 11 dígitos máximo, validación requerida
- **Nombre Comercial** (*): Razón social, validación requerida
- **Dirección Fiscal**: Opcional, texto libre

**Validación:**
```typescript
if (!configFormData.rnc_empresa) {
  toast.error('RNC de la empresa es requerido');
  return;
}
if (!configFormData.nombre_comercial) {
  toast.error('Nombre comercial es requerido');
  return;
}
```

---

### 5. **Upload de Certificado Digital** 📄

```tsx
<div className="border-2 border-dashed rounded-lg p-4 hover:border-blue-400">
  <input 
    type="file"
    id="certificado-file"
    accept=".p12,.pfx"
    onChange={(e) => {
      const file = e.target.files?.[0];
      setConfigFormData({ ...configFormData, certificado_file: file });
      toast.success(`Certificado seleccionado: ${file.name}`);
    }}
    disabled={configFormData.modo_api === 'Simulator'}
  />
  <label htmlFor="certificado-file">
    <Upload icon />
    {configFormData.certificado_file
      ? configFormData.certificado_file.name
      : 'Cargar certificado P12/PFX'
    }
  </label>
</div>
```

**Características:**
- ✅ Input file oculto con label clickeable
- ✅ Accept solo `.p12` y `.pfx`
- ✅ Hover effect en zona de upload
- ✅ Toast notification al seleccionar archivo
- ✅ Muestra nombre del archivo seleccionado
- ✅ Disabled en modo Simulator

**Visual:**
- Borde punteado (dashed)
- Hover: border-blue-400
- Icon Upload (8×8)
- Texto adaptativo según estado

---

### 6. **Alert Informativa** ℹ️

```tsx
<div className="bg-blue-50 border-blue-200 rounded-lg p-3">
  <AlertCircle />
  <p className="font-medium mb-1">Información importante:</p>
  <ul className="list-disc list-inside">
    <li>En modo Simulator: No se requieren credenciales ni certificado</li>
    <li>En modo Testing: Use credenciales del ambiente de pruebas</li>
    <li>En modo Production: Use credenciales reales y certificado válido</li>
    <li>El certificado debe estar en formato P12 o PFX con su contraseña</li>
  </ul>
</div>
```

**Estilo:**
- Fondo: blue-50 (dark: blue-950)
- Borde: blue-200 (dark: blue-800)
- Texto: blue-700 (dark: blue-300)
- Icon: AlertCircle azul

---

### 7. **Action Buttons** 🔘

```tsx
<div className="flex justify-end gap-2 pt-4 border-t">
  <Button 
    variant="outline"
    onClick={() => setIsConfigModalOpen(false)}
  >
    Cancelar
  </Button>
  <Button onClick={handleSaveConfig}>
    <CheckCircle /> Guardar Configuración
  </Button>
</div>
```

**Botones:**
- **Cancelar**: Cierra modal sin guardar, variant outline
- **Guardar**: Llama handleSaveConfig, icon CheckCircle

---

## 🔄 Flujo de Usuario Completo

### Paso 1: Abrir Modal
1. Usuario click en botón "Editar Configuración" en Tab Configuración
2. Trigger: `handleOpenConfigModal()`
3. Cargar datos existentes desde `dgiiConfig`
4. Abrir modal: `setIsConfigModalOpen(true)`

### Paso 2: Llenar Formulario
1. Seleccionar Modo API (Simulator/Testing/Production)
2. Si no es Simulator:
   - Ingresar usuario y contraseña DGII
   - Cargar certificado P12/PFX
3. Ingresar RNC empresa (obligatorio)
4. Ingresar nombre comercial (obligatorio)
5. Ingresar dirección fiscal (opcional)

### Paso 3: Validación
1. Click en "Guardar Configuración"
2. Validar RNC empresa no vacío
3. Validar nombre comercial no vacío
4. Si errores: mostrar toast.error y detener

### Paso 4: Guardar
1. Llamar API: `endpoints.regional.dgiiDominican.updateConfiguration(configFormData)`
2. Backend actualiza DGII Configuration DocType
3. Si modo != Simulator: guardar certificado y credenciales
4. Mostrar toast.success
5. Cerrar modal
6. Refetch query de configuración

---

## 🎯 Integraciones Requeridas

### 1. Load Existing Configuration
```typescript
const handleOpenConfigModal = () => {
  if (dgiiConfig) {
    setConfigFormData({
      modo_api: dgiiConfig.modo_api || 'Simulator',
      dgii_username: dgiiConfig.dgii_username || '',
      dgii_password: '', // Security: don't load password
      rnc_empresa: dgiiConfig.rnc_empresa || '',
      nombre_comercial: dgiiConfig.nombre_comercial || '',
      direccion_fiscal: dgiiConfig.direccion_fiscal || '',
      certificado_file: null
    });
  }
  setIsConfigModalOpen(true);
};
```

### 2. Save Configuration
```typescript
const handleSaveConfig = async () => {
  try {
    // Validate required fields
    if (!configFormData.rnc_empresa) {
      toast.error('RNC de la empresa es requerido');
      return;
    }
    if (!configFormData.nombre_comercial) {
      toast.error('Nombre comercial es requerido');
      return;
    }

    // Call API
    const result = await endpoints.regional.dgiiDominican.updateConfiguration(configFormData);
    
    toast.success('Configuración guardada exitosamente');
    setIsConfigModalOpen(false);
    
    // TODO: Invalidate query
    // queryClient.invalidateQueries(['dgii-configuration'])
    
  } catch (error: any) {
    toast.error('Error al guardar configuración', {
      description: error.message
    });
  }
};
```

### 3. Backend API (regional.ts)
```typescript
// En endpoints.regional.dgiiDominican:
updateConfiguration: async (data: any) => {
  const formData = new FormData();
  
  // Basic fields
  formData.append('modo_api', data.modo_api);
  formData.append('rnc_empresa', data.rnc_empresa);
  formData.append('nombre_comercial', data.nombre_comercial);
  formData.append('direccion_fiscal', data.direccion_fiscal);
  
  // Credentials (only if not Simulator)
  if (data.modo_api !== 'Simulator') {
    formData.append('dgii_username', data.dgii_username);
    formData.append('dgii_password', data.dgii_password);
    
    // Certificate file
    if (data.certificado_file) {
      formData.append('certificado', data.certificado_file);
    }
  }
  
  return proxy.post(
    '/api/method/csf_do.api.update_dgii_configuration',
    formData
  );
}
```

### 4. Backend Method (csf_do/api.py)
```python
@frappe.whitelist()
def update_dgii_configuration(**kwargs):
    """Update DGII Configuration DocType"""
    
    doc = frappe.get_single('DGII Configuration')
    
    # Update basic fields
    doc.modo_api = kwargs.get('modo_api', 'Simulator')
    doc.rnc_empresa = kwargs.get('rnc_empresa')
    doc.nombre_comercial = kwargs.get('nombre_comercial')
    doc.direccion_fiscal = kwargs.get('direccion_fiscal')
    
    # Update credentials if not Simulator
    if doc.modo_api != 'Simulator':
        doc.dgii_username = kwargs.get('dgii_username')
        if kwargs.get('dgii_password'):
            doc.dgii_password = kwargs.get('dgii_password')
        
        # Handle certificate upload
        if frappe.request.files.get('certificado'):
            file = frappe.request.files['certificado']
            # Save file to private/files/
            # Update doc.certificado_digital with file path
    
    doc.save()
    frappe.db.commit()
    
    return {'success': True, 'message': 'Configuración actualizada'}
```

---

## 📊 Estado del Formulario (configFormData)

```typescript
interface ConfigFormData {
  modo_api: 'Simulator' | 'Testing' | 'Production';
  dgii_username: string;
  dgii_password: string;
  rnc_empresa: string;  // Required
  nombre_comercial: string;  // Required
  direccion_fiscal: string;  // Optional
  certificado_file: File | null;
}
```

**Estado Inicial:**
```typescript
const [configFormData, setConfigFormData] = useState({
  modo_api: 'Simulator',
  dgii_username: '',
  dgii_password: '',
  rnc_empresa: '',
  nombre_comercial: '',
  direccion_fiscal: '',
  certificado_file: null
});
```

---

## 🎨 Diseño Visual

### Layout:
- **Modal Width**: max-w-2xl (672px)
- **Modal Height**: max-h-90vh con scroll
- **Form Spacing**: space-y-6 entre secciones
- **Grid**: 2 columnas para credenciales y RNC/Nombre

### Paleta de Colores:
- **Simulator**: Gray-500 (🔵)
- **Testing**: Orange-500 (🟡)
- **Production**: Red-500 (🔴)
- **Upload Zone**: Blue-400 hover
- **Alert**: Blue-50/Blue-950

### Iconografía:
- **Shield**: Configuración DGII, Certificado
- **FileText**: Información Fiscal
- **Upload**: Upload de certificado
- **AlertCircle**: Info alert
- **CheckCircle**: Botón guardar

---

## 🔍 Testing Checklist

### Visual:
- [ ] Modal se abre correctamente
- [ ] Selector de modo muestra colores correctos
- [ ] Inputs disabled en modo Simulator
- [ ] Upload zone muestra hover effect
- [ ] Alert informativa bien formateada
- [ ] Botones alineados correctamente

### Funcional:
- [ ] Click "Editar Configuración" abre modal
- [ ] Selector cambia modo API
- [ ] Inputs se habilitan/deshabilitan según modo
- [ ] Upload file acepta solo P12/PFX
- [ ] Toast aparece al seleccionar certificado
- [ ] Validación de campos requeridos funciona
- [ ] Botón Cancelar cierra modal sin guardar
- [ ] Botón Guardar llama handleSaveConfig

### Integración:
- [ ] Carga datos existentes al abrir modal
- [ ] API updateConfiguration recibe datos correctos
- [ ] Backend actualiza DocType
- [ ] Certificado se sube correctamente
- [ ] Query se invalida después de guardar
- [ ] Toast success/error funcionan
- [ ] Modal se cierra después de guardar

---

## 💡 Mejoras Futuras

### 1. Query Invalidation
Agregar queryClient para refrescar datos:
```typescript
import { useQueryClient } from '@tanstack/react-query';

const queryClient = useQueryClient();

// After save:
queryClient.invalidateQueries(['dgii-configuration']);
```

### 2. Certificate Password
Agregar campo para contraseña del certificado:
```tsx
<Input 
  id="cert-password"
  type="password"
  placeholder="Contraseña del certificado"
  label="Contraseña P12/PFX"
/>
```

### 3. Certificate Preview
Mostrar detalles del certificado cargado:
```tsx
{configFormData.certificado_file && (
  <div className="text-sm text-muted-foreground">
    <p>Archivo: {configFormData.certificado_file.name}</p>
    <p>Tamaño: {(configFormData.certificado_file.size / 1024).toFixed(2)} KB</p>
  </div>
)}
```

### 4. Testing Connection
Botón para probar conexión con DGII:
```tsx
<Button 
  variant="outline"
  onClick={handleTestConnection}
  disabled={configFormData.modo_api === 'Simulator'}
>
  Probar Conexión
</Button>
```

---

## 📝 Archivos Modificados

### DGII.tsx
**Líneas agregadas:** ~215 líneas de código nuevo

**Imports:**
- Dialog components (líneas 9-10)
- Select components (línea 11)
- Shield icon (ya existía)

**State:**
- isConfigModalOpen (línea 67)
- configFormData (líneas 68-76)

**Handlers:**
- handleOpenConfigModal (líneas 370-383)
- handleSaveConfig (líneas 385-408)

**Modal Component:**
- Líneas 1462-1677 (215 líneas)

### GestionDGII.tsx
**Estado:** Sincronizado con DGII.tsx via Copy-Item

---

## 🎯 Próximos Pasos

1. ✅ **COMPLETADO:** Modal de Configuración DGII
2. 🔄 **AHORA:** Crear modal CRUD NCF Series
3. ⏳ **SIGUIENTE:** Testing del modal en navegador
4. ⏳ **DESPUÉS:** Implementar backend method update_dgii_configuration
5. ⏳ **FINALMENTE:** Agregar query invalidation con queryClient

---

**✨ Modal Configuración DGII completado y listo para testing e integración ✨**

Archivo actualizado: `DGII.tsx` y `GestionDGII.tsx`  
Líneas totales: 1677 (↑ 266 líneas desde versión anterior)
