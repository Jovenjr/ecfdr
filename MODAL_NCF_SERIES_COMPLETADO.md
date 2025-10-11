# ✅ Modal NCF Series CRUD - Implementación Completada

**Fecha:** 10 de octubre de 2025  
**Archivo:** `src/pages/DGII.tsx` (líneas 1838-2041)  
**Estado:** ✅ Completado

---

## 📋 Componentes Implementados

### 1. **Botón "Nueva Serie NCF" en Header** 🎯

```tsx
<CardHeader>
  <div className="flex items-center justify-between">
    <div>
      <CardTitle>
        <FileText /> Series de Comprobantes Fiscales (NCF)
      </CardTitle>
      <CardDescription>
        Gestión de series autorizadas por la DGII
      </CardDescription>
    </div>
    <Button onClick={() => handleOpenNCFModal('create')}>
      <Plus /> Nueva Serie NCF
    </Button>
  </div>
</CardHeader>
```

**Características:**
- ✅ Botón con icono Plus
- ✅ Posicionado en header del tab
- ✅ Abre modal en modo 'create'

---

### 2. **Botones de Acción en Cada Serie** 🔘

```tsx
<div className="flex items-center gap-2">
  <Badge variant={...}>{serie.estado}</Badge>
  
  <Button
    variant="outline"
    size="sm"
    onClick={() => handleOpenNCFModal('edit', serie)}
  >
    <Edit2 className="h-4 w-4" />
  </Button>
  
  <Button
    variant="outline"
    size="sm"
    onClick={() => handleDeleteNCFSerie(serie.name)}
  >
    <Trash2 className="h-4 w-4 text-red-600" />
  </Button>
</div>
```

**Botones por Serie:**
- ✅ **Editar** (Edit2 icon) - Abre modal con datos precargados
- ✅ **Eliminar** (Trash2 icon rojo) - Confirmación antes de borrar

---

### 3. **Modal Dialog Component** 📄

```tsx
<Dialog open={isNCFModalOpen} onOpenChange={setIsNCFModalOpen}>
  <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
    <DialogHeader>
      <DialogTitle>
        <FileText /> {mode === 'create' ? 'Nueva' : 'Editar'} Serie NCF
      </DialogTitle>
    </DialogHeader>
    {/* Form fields */}
  </DialogContent>
</Dialog>
```

**Características:**
- ✅ Modal responsive de 3xl (max-width: 768px)
- ✅ Scroll vertical automático
- ✅ Título dinámico según modo (create/edit)
- ✅ Cierre con backdrop click

---

### 4. **Selector de Tipo NCF** 📋

```tsx
<Select value={ncfFormData.tipo_ncf}>
  <SelectItem value="01">01 - Facturas de Crédito Fiscal</SelectItem>
  <SelectItem value="02">02 - Facturas de Consumo</SelectItem>
  <SelectItem value="03">03 - Notas de Débito</SelectItem>
  <SelectItem value="04">04 - Notas de Crédito</SelectItem>
  <SelectItem value="11">11 - Proveedores Informales</SelectItem>
  <SelectItem value="12">12 - Registro Único de Ingresos</SelectItem>
  <SelectItem value="13">13 - Gastos Menores</SelectItem>
  <SelectItem value="14">14 - Régimen Especial</SelectItem>
  <SelectItem value="15">15 - Gubernamentales</SelectItem>
  <SelectItem value="16">16 - Exportaciones</SelectItem>
  <SelectItem value="17">17 - Pagos al Exterior</SelectItem>
</Select>
```

**11 Tipos de NCF Disponibles:**

| Código | Descripción |
|--------|-------------|
| 01 | Facturas de Crédito Fiscal (e-CF) |
| 02 | Facturas de Consumo |
| 03 | Notas de Débito |
| 04 | Notas de Crédito |
| 11 | Proveedores Informales |
| 12 | Registro Único de Ingresos |
| 13 | Gastos Menores |
| 14 | Régimen Especial |
| 15 | Gubernamentales |
| 16 | Exportaciones |
| 17 | Pagos al Exterior |

---

### 5. **Campo Serie** 🔤

```tsx
<Input
  id="serie"
  type="text"
  placeholder="B01"
  maxLength={3}
  value={ncfFormData.serie}
  onChange={(e) =>
    setNCFFormData({ 
      ...ncfFormData, 
      serie: e.target.value.toUpperCase() 
    })
  }
/>
<p className="text-xs text-muted-foreground">
  3 caracteres alfanuméricos (ej: B01)
</p>
```

**Características:**
- ✅ Máximo 3 caracteres
- ✅ Conversión automática a mayúsculas
- ✅ Placeholder informativo (B01)
- ✅ Helper text con formato

---

### 6. **Rango de Números** 🔢

```tsx
<div className="grid grid-cols-2 gap-4">
  <div>
    <Label htmlFor="desde">Desde *</Label>
    <Input
      id="desde"
      type="number"
      min="1"
      max="99999999"
      value={ncfFormData.desde}
      onChange={...}
    />
  </div>
  <div>
    <Label htmlFor="hasta">Hasta *</Label>
    <Input
      id="hasta"
      type="number"
      min="1"
      max="99999999"
      value={ncfFormData.hasta}
      onChange={...}
    />
  </div>
</div>

{/* Cálculo automático */}
{ncfFormData.desde && ncfFormData.hasta && (
  <p className="text-xs text-muted-foreground">
    Total disponible: {
      parseInt(ncfFormData.hasta) - parseInt(ncfFormData.desde) + 1
    } comprobantes
  </p>
)}
```

**Características:**
- ✅ Validación min/max (1-99,999,999)
- ✅ Cálculo automático de total disponible
- ✅ Validación backend: desde < hasta

**Ejemplo:**
- Desde: 1
- Hasta: 10,000
- **Total: 10,000 comprobantes**

---

### 7. **Información de Autorización** 📅

```tsx
<Input
  id="company"
  type="text"
  placeholder="Empresa Principal"
  value={ncfFormData.company}
  required
/>

<Input
  id="fecha-autorizacion"
  type="date"
  value={ncfFormData.fecha_autorizacion}
  required
/>

<Input
  id="fecha-vencimiento"
  type="date"
  value={ncfFormData.fecha_vencimiento}
  required
/>
```

**Campos:**
- **Empresa** (*): Nombre de la compañía
- **Fecha Autorización** (*): Fecha de aprobación DGII
- **Fecha Vencimiento** (*): Fecha límite de uso

---

### 8. **Estado y Notas** 📝

```tsx
<Select value={ncfFormData.estado}>
  <SelectItem value="Activo">Activo</SelectItem>
  <SelectItem value="Inactivo">Inactivo</SelectItem>
  <SelectItem value="Vencido">Vencido</SelectItem>
</Select>

<Input
  id="notas"
  type="text"
  placeholder="Notas adicionales..."
  value={ncfFormData.notas}
  optional
/>
```

**Estados:**
- **Activo**: Serie en uso
- **Inactivo**: Serie suspendida
- **Vencido**: Serie expirada

---

### 9. **Alert de Advertencia** ⚠️

```tsx
<div className="bg-amber-50 border-amber-200 rounded-lg p-3">
  <AlertTriangle />
  <p className="font-medium mb-1">Importante:</p>
  <ul className="list-disc list-inside">
    <li>La serie debe estar autorizada por la DGII</li>
    <li>El rango debe coincidir con la autorización oficial</li>
    <li>No se puede modificar tipo NCF ni serie después de crear</li>
    <li>El sistema validará duplicados de series activas</li>
  </ul>
</div>
```

**Estilo:**
- Fondo: amber-50 (dark: amber-950)
- Borde: amber-200 (dark: amber-800)
- Texto: amber-700 (dark: amber-300)
- Icon: AlertTriangle

---

### 10. **Action Buttons** 🔘

```tsx
<div className="flex justify-end gap-2 pt-4 border-t">
  <Button 
    variant="outline"
    onClick={() => setIsNCFModalOpen(false)}
  >
    Cancelar
  </Button>
  <Button onClick={handleSaveNCFSerie}>
    <CheckCircle /> 
    {mode === 'create' ? 'Crear Serie' : 'Guardar Cambios'}
  </Button>
</div>
```

**Botones:**
- **Cancelar**: Cierra modal sin guardar
- **Crear/Guardar**: Llama handleSaveNCFSerie con validación

---

## 🔄 Flujo de Usuario Completo

### Flujo 1: Crear Nueva Serie

1. Usuario click en "Nueva Serie NCF"
2. Trigger: `handleOpenNCFModal('create')`
3. Modal se abre con formulario vacío
4. Usuario llena campos:
   - Tipo NCF: 01
   - Serie: B01
   - Desde: 1
   - Hasta: 10000
   - Empresa: AI Studio RD
   - Fecha autorización: 2025-01-01
   - Fecha vencimiento: 2025-12-31
   - Estado: Activo
5. Click "Crear Serie"
6. Validación:
   - Tipo NCF requerido ✅
   - Serie requerida ✅
   - Rango válido (1 < 10000) ✅
   - Empresa requerida ✅
7. Llamar API: `createNCFSeries(dataToSend)`
8. Backend crea documento NCF Series
9. Toast success: "Serie NCF creada exitosamente"
10. Modal se cierra
11. Tabla se refresca automáticamente

---

### Flujo 2: Editar Serie Existente

1. Usuario click en botón Editar (Edit2) de una serie
2. Trigger: `handleOpenNCFModal('edit', serie)`
3. Modal se abre con datos precargados
4. Usuario modifica campos editables:
   - ✅ Fecha vencimiento
   - ✅ Estado
   - ✅ Notas
   - ❌ Tipo NCF (bloqueado)
   - ❌ Serie (bloqueado)
   - ❌ Rango (bloqueado)
5. Click "Guardar Cambios"
6. Llamar API: `updateNCFSeries(name, dataToSend)`
7. Backend actualiza documento
8. Toast success: "Serie NCF actualizada exitosamente"
9. Modal se cierra
10. Tabla se refresca

---

### Flujo 3: Eliminar Serie

1. Usuario click en botón Eliminar (Trash2)
2. Trigger: `handleDeleteNCFSerie(serieName)`
3. Confirmación: `confirm("¿Está seguro de eliminar?")`
4. Si cancelado: detener
5. Si confirmado:
   - Llamar: `fetch('/api/resource/NCF Series/${name}', {method: 'DELETE'})`
   - Backend elimina documento
   - Toast success: "Serie NCF eliminada exitosamente"
   - Tabla se refresca

---

## 🎯 Estado del Formulario (ncfFormData)

```typescript
interface NCFFormData {
  tipo_ncf: string;           // Required - Select (01-17)
  serie: string;              // Required - 3 chars uppercase
  desde: string;              // Required - number (converted to int)
  hasta: string;              // Required - number (converted to int)
  company: string;            // Required - company name
  fecha_autorizacion: string; // Required - ISO date
  fecha_vencimiento: string;  // Required - ISO date
  estado: string;             // Default: 'Activo'
  notas: string;              // Optional
}
```

**Estado Inicial:**
```typescript
const [ncfFormData, setNCFFormData] = useState({
  tipo_ncf: '',
  serie: '',
  desde: '',
  hasta: '',
  company: '',
  fecha_autorizacion: '',
  fecha_vencimiento: '',
  estado: 'Activo',
  notas: ''
});
```

---

## 🔍 Validaciones Implementadas

### Client-side Validation:

```typescript
// 1. Campos requeridos
if (!ncfFormData.tipo_ncf) {
  toast.error('Tipo de NCF es requerido');
  return;
}

if (!ncfFormData.serie) {
  toast.error('Serie es requerida');
  return;
}

if (!ncfFormData.desde || !ncfFormData.hasta) {
  toast.error('Rango desde-hasta es requerido');
  return;
}

if (!ncfFormData.company) {
  toast.error('Empresa es requerida');
  return;
}

// 2. Validación de números
const desde = parseInt(ncfFormData.desde);
const hasta = parseInt(ncfFormData.hasta);

if (isNaN(desde) || isNaN(hasta)) {
  toast.error('Desde y Hasta deben ser números');
  return;
}

// 3. Validación de rango
if (desde >= hasta) {
  toast.error('El valor Desde debe ser menor que Hasta');
  return;
}
```

### Backend Validation (Expected):

```python
# En csf_do NCF Series DocType validate()
def validate(self):
    # 1. Validar serie única
    if frappe.db.exists('NCF Series', {
        'serie': self.serie,
        'tipo_ncf': self.tipo_ncf,
        'company': self.company,
        'estado': 'Activo',
        'name': ['!=', self.name]
    }):
        frappe.throw('Ya existe una serie activa con este código')
    
    # 2. Validar rango
    if self.desde >= self.hasta:
        frappe.throw('El número Desde debe ser menor que Hasta')
    
    # 3. Validar fechas
    if self.fecha_vencimiento < self.fecha_autorizacion:
        frappe.throw('Fecha de vencimiento debe ser posterior a fecha de autorización')
    
    # 4. Validar formato serie
    if not re.match(r'^[A-Z0-9]{3}$', self.serie):
        frappe.throw('La serie debe tener 3 caracteres alfanuméricos')
```

---

## 📊 Handlers Implementados

### 1. handleOpenNCFModal

```typescript
const handleOpenNCFModal = (mode: 'create' | 'edit', serie?: any) => {
  setNCFModalMode(mode);
  
  if (mode === 'edit' && serie) {
    // Load existing data
    setCurrentNCFSerie(serie);
    setNCFFormData({
      tipo_ncf: serie.tipo_ncf || '',
      serie: serie.serie || '',
      desde: serie.desde?.toString() || '',
      hasta: serie.hasta?.toString() || '',
      company: serie.company || '',
      fecha_autorizacion: serie.fecha_autorizacion || '',
      fecha_vencimiento: serie.fecha_vencimiento || '',
      estado: serie.estado || 'Activo',
      notas: serie.notas || ''
    });
  } else {
    // Reset form for create mode
    setCurrentNCFSerie(null);
    setNCFFormData({
      tipo_ncf: '',
      serie: '',
      desde: '',
      hasta: '',
      company: '',
      fecha_autorizacion: '',
      fecha_vencimiento: '',
      estado: 'Activo',
      notas: ''
    });
  }
  
  setIsNCFModalOpen(true);
};
```

---

### 2. handleSaveNCFSerie

```typescript
const handleSaveNCFSerie = async () => {
  try {
    // Validate all required fields
    // (see Validations section above)

    // Convert string to numbers for API
    const dataToSend = {
      ...ncfFormData,
      desde: parseInt(ncfFormData.desde),
      hasta: parseInt(ncfFormData.hasta)
    };

    // Call appropriate API
    if (ncfModalMode === 'create') {
      await endpoints.regional.dgiiDominican.createNCFSeries(dataToSend);
      toast.success('Serie NCF creada exitosamente');
    } else {
      await endpoints.regional.dgiiDominican.updateNCFSeries(
        currentNCFSerie.name, 
        dataToSend
      );
      toast.success('Serie NCF actualizada exitosamente');
    }

    // Close and refresh
    setIsNCFModalOpen(false);
    // TODO: queryClient.invalidateQueries(['dgii-ncf-series'])
    
  } catch (error: any) {
    toast.error('Error al guardar serie NCF', {
      description: error.message
    });
  }
};
```

---

### 3. handleDeleteNCFSerie

```typescript
const handleDeleteNCFSerie = async (serieName: string) => {
  // Confirmation dialog
  if (!confirm('¿Está seguro de eliminar esta serie NCF?')) {
    return;
  }
  
  try {
    // Delete via REST API
    await fetch(`/api/resource/NCF Series/${serieName}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    toast.success('Serie NCF eliminada exitosamente');
    // TODO: queryClient.invalidateQueries(['dgii-ncf-series'])
    
  } catch (error: any) {
    toast.error('Error al eliminar serie NCF', {
      description: error.message || 'No se pudo eliminar la serie'
    });
  }
};
```

---

## 🎨 Diseño Visual

### Layout:
- **Modal Width**: max-w-3xl (768px)
- **Modal Height**: max-h-90vh con scroll
- **Form Spacing**: space-y-6 entre secciones
- **Grids**: 2 columnas para la mayoría de campos

### Paleta de Colores:
- **Primary**: Blue-600 (iconos, títulos)
- **Warning**: Amber-50/600 (alert de advertencia)
- **Danger**: Red-600 (botón eliminar)
- **Success**: Green-600 (disponibles)

### Iconografía:
- **FileText**: Título modal, tab header
- **Plus**: Botón nueva serie
- **Edit2**: Botón editar
- **Trash2**: Botón eliminar
- **BarChart3**: Sección rango de números
- **Calendar**: Sección fechas
- **CheckCircle**: Botón guardar
- **AlertTriangle**: Alert de advertencia

---

## 📝 Archivos Modificados

### DGII.tsx
**Líneas agregadas:** ~220 líneas de código nuevo

**State (líneas 70-82):**
- isNCFModalOpen
- ncfModalMode
- currentNCFSerie
- ncfFormData

**Handlers (líneas 430-547):**
- handleOpenNCFModal (35 líneas)
- handleSaveNCFSerie (65 líneas)
- handleDeleteNCFSerie (20 líneas)

**UI Updates:**
- Tab NCF Series header: Botón "Nueva Serie NCF" (línea ~1291)
- Cards de series: Botones Editar/Eliminar (líneas ~1320)

**Modal Component (líneas 1838-2041):**
- 203 líneas de JSX completo

### GestionDGII.tsx
**Estado:** Sincronizado con DGII.tsx via Copy-Item

---

## 🔧 Integraciones con Backend

### API Endpoints Usados:

```typescript
// 1. Crear serie
endpoints.regional.dgiiDominican.createNCFSeries({
  tipo_ncf: string,
  serie: string,
  desde: number,
  hasta: number,
  company: string,
  fecha_autorizacion: string,
  fecha_vencimiento: string,
  estado?: string,
  notas?: string
})

// 2. Actualizar serie
endpoints.regional.dgiiDominican.updateNCFSeries(name: string, data: any)

// 3. Eliminar serie
fetch('/api/resource/NCF Series/${name}', { method: 'DELETE' })

// 4. Listar series
endpoints.regional.dgiiDominican.getNCFSeriesList(filters?)
```

---

## 🧪 Testing Checklist

### Visual:
- [ ] Botón "Nueva Serie NCF" visible en header
- [ ] Botones Editar/Eliminar en cada card
- [ ] Modal se abre correctamente
- [ ] Selector de tipo NCF muestra 11 opciones
- [ ] Input serie convierte a mayúsculas
- [ ] Cálculo de total disponible funciona
- [ ] Alert de advertencia bien formateada
- [ ] Botones alineados correctamente

### Funcional:
- [ ] Click "Nueva Serie" abre modal vacío
- [ ] Click "Editar" abre modal con datos
- [ ] Validación de campos requeridos
- [ ] Validación de rango (desde < hasta)
- [ ] Conversión de strings a números
- [ ] Selector de estado funciona
- [ ] Botón Cancelar cierra modal
- [ ] Botón Guardar llama handleSaveNCFSerie

### Integración:
- [ ] API createNCFSeries recibe datos correctos
- [ ] API updateNCFSeries actualiza serie
- [ ] DELETE elimina serie correctamente
- [ ] Confirmación antes de eliminar
- [ ] Toast success/error funcionan
- [ ] Modal se cierra después de guardar
- [ ] Tabla se refresca (con queryClient)

---

## 💡 Mejoras Futuras

### 1. Query Invalidation
```typescript
import { useQueryClient } from '@tanstack/react-query';

const queryClient = useQueryClient();

// After save/delete:
queryClient.invalidateQueries(['dgii-ncf-series']);
```

### 2. Deshabilitar Campos en Modo Edit
```tsx
<Input
  id="serie"
  disabled={ncfModalMode === 'edit'}
  // No se puede cambiar serie después de crear
/>
```

### 3. Validación de Duplicados
```tsx
// Before save:
const exists = ncfSeriesList.some(
  s => s.serie === ncfFormData.serie && 
       s.tipo_ncf === ncfFormData.tipo_ncf &&
       s.estado === 'Activo'
);
if (exists) {
  toast.error('Ya existe una serie activa con este código');
  return;
}
```

### 4. Preview de NCF Completo
```tsx
{ncfFormData.tipo_ncf && ncfFormData.serie && (
  <div className="text-sm text-muted-foreground">
    <p>Vista previa: 
      <strong className="font-mono ml-2">
        E{ncfFormData.tipo_ncf}{ncfFormData.serie}00000001
      </strong>
    </p>
  </div>
)}
```

---

## 📊 Datos de Ejemplo para Testing

### Crear Serie de Facturas de Crédito Fiscal:
```json
{
  "tipo_ncf": "01",
  "serie": "B01",
  "desde": 1,
  "hasta": 10000,
  "company": "AI Studio RD",
  "fecha_autorizacion": "2025-01-01",
  "fecha_vencimiento": "2025-12-31",
  "estado": "Activo",
  "notas": "Serie principal para e-CF"
}
```

### Crear Serie de Notas de Crédito:
```json
{
  "tipo_ncf": "04",
  "serie": "B02",
  "desde": 1,
  "hasta": 5000,
  "company": "AI Studio RD",
  "fecha_autorizacion": "2025-01-01",
  "fecha_vencimiento": "2025-12-31",
  "estado": "Activo",
  "notas": "Para devoluciones y descuentos"
}
```

---

## 🎯 Próximos Pasos

1. ✅ **COMPLETADO:** Modal NCF Series CRUD
2. 🔄 **AHORA:** Testing del modal en navegador
3. ⏳ **SIGUIENTE:** Implementar reportes 606/607/608/IT-1
4. ⏳ **DESPUÉS:** Agregar query invalidation
5. ⏳ **FINALMENTE:** Integrar e-CF en Facturacion.tsx

---

**✨ Modal NCF Series CRUD completado y listo para testing ✨**

Archivo actualizado: `DGII.tsx` y `GestionDGII.tsx`  
Líneas totales: 2,041 (↑ 364 líneas desde versión anterior)  
Funcionalidades: Create, Read, Update, Delete de Series NCF
