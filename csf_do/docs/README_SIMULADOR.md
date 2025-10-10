# 🎯 README - Simulador DGII

## Estado: ✅ COMPLETADO Y LISTO PARA PROBAR

El simulador DGII está completamente implementado y listo para usar. No requiere conexión a DGII - funciona completamente offline.

---

## 🚀 Inicio Rápido

### 1. Verificar que todo esté listo
```powershell
python verify_simulator_setup.py
```

### 2. Ejecutar pruebas
```powershell
python test_simulator_complete.py
```

### 3. Configurar en ERPNext
1. Abrir **DGII Configuration**
2. Establecer **Modo API** = `simulator`
3. Guardar

### 4. ¡Probar!
Crear una factura de venta en ERPNext y el sistema usará el simulador automáticamente.

---

## 📖 Documentación

| Documento | Descripción |
|-----------|-------------|
| **[INICIO_RAPIDO.md](../INICIO_RAPIDO.md)** | Inicio rápido en 3 pasos |
| **[GUIA_RAPIDA_SIMULADOR.md](../GUIA_RAPIDA_SIMULADOR.md)** | Guía completa de uso |
| **[TRABAJO_COMPLETADO.md](../TRABAJO_COMPLETADO.md)** | Resumen del trabajo realizado |
| **[SIMULADOR_DGII.md](SIMULADOR_DGII.md)** | Documentación técnica |
| **[MODULO_ACECFAR.md](MODULO_ACECFAR.md)** | Módulo ACECFAR |

---

## 🧪 Scripts Disponibles

| Script | Propósito |
|--------|-----------|
| `test_simulator_complete.py` | Pruebas completas del simulador |
| `verify_simulator_setup.py` | Verificar instalación |
| `setup_simulator.py` | Configuración automática |

---

## 🎯 Funcionalidades

### ✅ Completamente Implementado

- **Envío de e-CF**
  - Genera Track ID automáticamente
  - Simula respuesta de DGII
  - Múltiples escenarios (éxito, error, timeout)

- **Consulta de Estado**
  - Progresión temporal realista
  - RECIBIDO → EN_PROCESO → ACEPTADO/RECHAZADO
  - 95% aceptados, 5% rechazados

- **Generación de e-CF de Proveedor**
  - XML completo según estándar DGII
  - Para testing de ACECFAR
  - Configurable (RNC, monto)

- **Acuse de Recibo (ACECFAR)**
  - Simula envío de acuse
  - Estados: ACEPTADO/RECHAZADO
  - Con motivo de rechazo

- **Cliente Unificado**
  - Cambio transparente simulador ↔ producción
  - API consistente
  - Configuración desde UI

---

## 📊 Progresión de Estados

```
Tiempo      Estado         Descripción
─────────────────────────────────────────────────────
0-10 seg    RECIBIDO       e-CF en cola
10-30 seg   EN_PROCESO     Validando
30+ seg     ACEPTADO       95% éxito
            RECHAZADO      5% error
```

---

## 💻 Ejemplos de Código

### Enviar e-CF
```python
from csf_do.csf_do.integrations.dgii_client import get_dgii_client

client = get_dgii_client()
result = client.enviar_ecf(xml_content, "31", "B0100000001")
print(result["track_id"])
```

### Consultar Estado
```python
import time
time.sleep(35)  # Esperar progresión
estado = client.consultar_estado(track_id)
print(estado["estado"])  # ACEPTADO o RECHAZADO
```

### Generar e-CF de Proveedor
```python
from csf_do.csf_do.integrations.dgii_simulator import DGIISimulator

simulator = DGIISimulator()
xml = simulator.generar_ecf_proveedor("131793916", 11800.00)
```

---

## 🔧 Configuración

### Modo API (DGII Configuration)

- **`simulator`** - Desarrollo local (sin DGII)
- **`test`** - Certificación con DGII
- **`production`** - Producción real

### Escenarios (DGII Simulator Config)

- **`scenario_envio`**: success, validation_error, timeout, server_error
- **`scenario_consulta`**: success, not_found
- **`scenario_acuse`**: success, error

---

## ✅ Tests

### Ejecutar Todos los Tests
```powershell
bench --site [sitio] run-tests --app csf_do
```

### Tests del Simulador
```powershell
bench --site [sitio] run-tests csf_do.csf_do.tests.test_dgii_simulator
```

### Tests de ACECFAR
```powershell
bench --site [sitio] run-tests csf_do.csf_do.tests.test_acecfar
```

---

## 📁 Estructura

```
csf_do/
├── integrations/
│   ├── dgii_simulator.py       ← Simulador principal
│   ├── dgii_client.py          ← Cliente unificado
│   └── acecfar_processor.py    ← Procesador ACECFAR
├── utils/
│   ├── acecfar_parser.py       ← Parser XML
│   └── signature_validator.py  ← Validador firma
├── doctype/
│   ├── dgii_configuration/     ← Config principal
│   ├── dgii_simulator_config/  ← Config simulador
│   └── ecf_recibido/           ← e-CF recibidos
├── tests/
│   ├── test_dgii_simulator.py  ← Tests unitarios
│   └── test_acecfar.py         ← Tests ACECFAR
└── docs/
    ├── SIMULADOR_DGII.md       ← Doc técnica
    └── MODULO_ACECFAR.md       ← Doc ACECFAR
```

---

## 🐛 Solución de Problemas

### Error: "DGII Configuration not found"
**Solución:** Ir a DGII Configuration y completar RNC Emisor

### Error: "Simulador no está activo"
**Solución:** Verificar que api_mode = `simulator`

### Las pruebas fallan
**Solución:** Ejecutar dentro de bench console

### Los estados no cambian
**Solución:** Esperar al menos 30 segundos

---

## 🎓 Próximos Pasos

1. ✅ Ejecutar `verify_simulator_setup.py`
2. ✅ Ejecutar `test_simulator_complete.py`
3. ✅ Configurar modo API = `simulator`
4. ✅ Crear factura de prueba
5. 📖 Leer `GUIA_RAPIDA_SIMULADOR.md`

---

## 📞 Recursos

- **Documentación:** Ver `/docs/`
- **Código fuente:** Ver `/csf_do/integrations/`
- **Pruebas:** Ver `/csf_do/tests/`
- **Scripts:** Ver raíz del proyecto

---

**¡El simulador está listo! 🚀**
