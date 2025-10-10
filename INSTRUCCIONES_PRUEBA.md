# 🧪 Instrucciones de Prueba - Simulador DGII

## ✅ Estado: LISTO PARA PROBAR

El simulador está completamente funcional. Sigue estos pasos para probarlo.

---

## 🚀 Opción 1: Prueba Rápida (5 minutos)

### Paso 1: Verificar Instalación
```powershell
python verify_simulator_setup.py
```

**Resultado esperado:** 
- ✅ Todos los archivos encontrados
- ✅ Todas las importaciones funcionando
- 📊 Porcentaje de éxito: 100%

### Paso 2: Ejecutar Pruebas Automáticas
```powershell
python test_simulator_complete.py
```

**Resultado esperado:**
```
🚀 INICIANDO PRUEBAS DEL SIMULADOR DGII

==================================================================
  PRUEBA 1: Importación de Módulos
==================================================================
✅ Importación de módulos
   Mensaje: Todos los módulos se importaron correctamente

==================================================================
  PRUEBA 2: Envío de e-CF Simulado
==================================================================
✅ Envío de e-CF
   Mensaje: e-CF enviado exitosamente
   Detalles: {
     "track_id": "abc-123-def-456",
     "ncf": "B0100000001",
     "fecha_recepcion": "2025-10-10T..."
   }

==================================================================
  PRUEBA 3: Consulta de Estado
==================================================================
   📊 Consulta 1 (inmediata):
      Estado: RECIBIDO
      Mensaje: e-CF recibido, en cola de procesamiento

   ⏳ Esperando 12 segundos...

   📊 Consulta 2 (después de 12 seg):
      Estado: EN_PROCESO
      Mensaje: e-CF en proceso de validación

   ⏳ Esperando 20 segundos más...

   📊 Consulta 3 (después de 32 seg total):
      Estado: ACEPTADO
      Mensaje: e-CF aceptado por DGII

✅ Consulta de estado con progresión temporal
   Mensaje: Estado final: ACEPTADO

... (más pruebas)

==================================================================
  RESUMEN DE PRUEBAS
==================================================================

  Total de pruebas: 6
  ✅ Exitosas: 6
  ❌ Fallidas: 0
  📊 Porcentaje éxito: 100.0%

==================================================================
  🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!
==================================================================
```

---

## 🖥️ Opción 2: Prueba Manual en ERPNext (10 minutos)

### Paso 1: Configurar el Simulador

1. **Abrir ERPNext**
   - Navegar a: `http://localhost:8000` (o tu URL)

2. **Ir a DGII Configuration**
   - Buscar: "DGII Configuration"
   - O ir directamente a: `/app/dgii-configuration`

3. **Configurar:**
   ```
   RNC Emisor: [Tu RNC, ej: 123456789]
   Versión e-CF: 1.0
   Modo API: simulator  ← ¡IMPORTANTE!
   
   Pre-Certificación Base URL: https://ecf.dgii.gov.do/testecf/
   Certificación Base URL: https://ecf.dgii.gov.do/certecf/
   Producción Base URL: https://ecf.dgii.gov.do/ecf/
   ```

4. **Guardar**

### Paso 2: Probar desde Console

```python
# Abrir bench console
bench --site [tu-sitio] console

# Ejecutar:
from csf_do.csf_do.integrations.dgii_client import get_dgii_client

# 1. Obtener cliente
client = get_dgii_client()

# 2. Verificar configuración
info = client.get_info()
print(info)
# Debe mostrar: {"modo": "simulator", "simulador_activo": True, ...}

# 3. Probar conexión
test = client.test_connection()
print(test)
# Debe mostrar: {"success": True, "mensaje": "Simulador activo..."}

# 4. Enviar e-CF de prueba
xml = """<?xml version="1.0" encoding="UTF-8"?>
<ECF xmlns="http://dgii.gov.do/ecf/v1.0">
    <Encabezado>
        <Version>1.0</Version>
        <IdDoc>
            <TipoeCF>31</TipoeCF>
            <eNCF>B0100000001</eNCF>
            <FechaEmision>2025-10-10</FechaEmision>
        </IdDoc>
    </Encabezado>
</ECF>"""

result = client.enviar_ecf(xml, "31", "B0100000001")
print(result)
# Debe mostrar: {"success": True, "track_id": "...", ...}

# 5. Guardar track_id
track_id = result["track_id"]

# 6. Consultar estado (inmediato)
import time
estado1 = client.consultar_estado(track_id)
print(f"Estado 1: {estado1['estado']}")  # RECIBIDO

# 7. Esperar y consultar (EN_PROCESO)
time.sleep(12)
estado2 = client.consultar_estado(track_id)
print(f"Estado 2: {estado2['estado']}")  # EN_PROCESO

# 8. Esperar y consultar (ACEPTADO/RECHAZADO)
time.sleep(20)
estado3 = client.consultar_estado(track_id)
print(f"Estado 3: {estado3['estado']}")  # ACEPTADO o RECHAZADO
print(f"Mensaje: {estado3['mensaje']}")

# 9. Generar e-CF de proveedor
from csf_do.csf_do.integrations.dgii_simulator import DGIISimulator
simulator = DGIISimulator()
xml_proveedor = simulator.generar_ecf_proveedor("131793916", 11800.00)
print(xml_proveedor[:200])  # Primeros 200 caracteres
```

**Resultado esperado:**
- ✅ Todos los comandos ejecutan sin errores
- ✅ Estados progresan: RECIBIDO → EN_PROCESO → ACEPTADO
- ✅ Se genera XML de proveedor

### Paso 3: Probar con Factura Real

1. **Crear Cliente**
   - Ir a: Customer → New
   - Nombre: "Cliente Prueba"
   - Customer Type: Company
   - Tax ID: RNC válido (ej: 131793916)
   - Guardar

2. **Crear Item**
   - Ir a: Item → New
   - Item Code: "PROD-001"
   - Item Name: "Producto de Prueba"
   - Standard Selling Rate: 1000
   - Guardar

3. **Crear Sales Invoice**
   - Ir a: Sales Invoice → New
   - Customer: Cliente Prueba
   - Agregar Item: PROD-001
   - Qty: 1
   - Guardar
   - **Submit** (Enviar)

4. **Verificar e-CF**
   - Buscar doctype "e-CF"
   - Debe aparecer un nuevo e-CF
   - Verificar campos:
     - `estado_dgii`: Pendiente → En Proceso → Aceptado
     - `track_id`: Debe tener un UUID
     - `xml_firmado`: Debe tener contenido

**Resultado esperado:**
- ✅ Factura se crea correctamente
- ✅ e-CF se envía automáticamente al simulador
- ✅ Track ID se registra
- ✅ Estado progresa automáticamente

---

## 🧪 Opción 3: Pruebas Unitarias (15 minutos)

### Ejecutar Todos los Tests
```powershell
bench --site [tu-sitio] run-tests --app csf_do
```

### Tests del Simulador Solamente
```powershell
bench --site [tu-sitio] run-tests csf_do.csf_do.tests.test_dgii_simulator
```

**Resultado esperado:**
```
test_dgii_simulator
    test_envio_exito (csf_do.csf_do.tests.test_dgii_simulator.TestDGIISimulator) ... ok
    test_envio_error (csf_do.csf_do.tests.test_dgii_simulator.TestDGIISimulator) ... ok
    test_consulta_estado (csf_do.csf_do.tests.test_dgii_simulator.TestDGIISimulator) ... ok
    test_progresion_temporal (csf_do.csf_do.tests.test_dgii_simulator.TestDGIISimulator) ... ok
    test_generar_ecf_proveedor (csf_do.csf_do.tests.test_dgii_simulator.TestDGIISimulator) ... ok
    test_acuse_recibo (csf_do.csf_do.tests.test_dgii_simulator.TestDGIISimulator) ... ok
    ...

Ran 10+ tests in 35.000s

OK
```

### Tests de ACECFAR
```powershell
bench --site [tu-sitio] run-tests csf_do.csf_do.tests.test_acecfar
```

---

## ✅ Checklist de Verificación

Marca cada item cuando lo completes:

### Verificación Básica
- [ ] `verify_simulator_setup.py` ejecuta sin errores
- [ ] Todos los archivos están presentes
- [ ] Todas las dependencias instaladas

### Pruebas Automáticas
- [ ] `test_simulator_complete.py` pasa todas las pruebas
- [ ] Envío de e-CF funciona
- [ ] Consulta de estado progresa correctamente
- [ ] Generación de e-CF de proveedor funciona

### Configuración ERPNext
- [ ] DGII Configuration existe
- [ ] Campo "Modo API" = simulator
- [ ] RNC Emisor configurado
- [ ] URLs configuradas

### Pruebas Manuales
- [ ] Cliente DGII se obtiene sin errores
- [ ] Test de conexión exitoso
- [ ] Envío manual funciona
- [ ] Estados progresan en el tiempo

### Integración ERPNext
- [ ] Sales Invoice se crea
- [ ] e-CF se genera automáticamente
- [ ] Track ID se registra
- [ ] Estado actualiza automáticamente

### Tests Unitarios
- [ ] Tests del simulador pasan
- [ ] Tests de ACECFAR pasan
- [ ] Sin errores críticos

---

## 🐛 Problemas Comunes

### 1. "ImportError: No module named 'frappe'"

**Causa:** Ejecutando fuera del contexto de Frappe

**Solución:**
```powershell
# Opción A: Usar bench console
bench --site [tu-sitio] console

# Opción B: Ejecutar con frappe
bench --site [tu-sitio] execute python test_simulator_complete.py
```

### 2. "DGII Configuration not found"

**Causa:** DocType no existe o no está configurado

**Solución:**
1. Verificar que csf_do esté instalado
2. Ir a DGII Configuration y completar campos
3. Guardar

### 3. "Simulador no está activo"

**Causa:** api_mode no está en 'simulator'

**Solución:**
1. Ir a DGII Configuration
2. Cambiar "Modo API" a "simulator"
3. Guardar
4. Reiniciar: `bench restart`

### 4. Los estados no cambian

**Causa:** No ha pasado suficiente tiempo

**Solución:**
- Estados cambian con el tiempo:
  - 0-10 seg: RECIBIDO
  - 10-30 seg: EN_PROCESO
  - 30+ seg: ACEPTADO/RECHAZADO
- Esperar al menos 35 segundos

---

## 📊 Resultados Esperados

### ✅ TODO FUNCIONA SI:

1. **verify_simulator_setup.py**
   - 100% de verificaciones pasan
   - Sin archivos faltantes
   - Sin dependencias faltantes

2. **test_simulator_complete.py**
   - 100% de pruebas pasan (6/6)
   - Estados progresan correctamente
   - XML se genera correctamente

3. **ERPNext**
   - Facturas se crean sin errores
   - e-CF se envían automáticamente
   - Estados actualizan periódicamente

4. **Tests Unitarios**
   - 10+ tests pasan
   - Sin fallos críticos

---

## 📞 Siguiente Paso

Una vez que todas las pruebas pasen:

✅ **Leer:** `GUIA_RAPIDA_SIMULADOR.md` para uso avanzado  
✅ **Ver:** `TRABAJO_COMPLETADO.md` para resumen completo  
✅ **Iniciar:** Desarrollo y pruebas de tu aplicación

---

**¡El simulador está listo para usar! 🚀**
