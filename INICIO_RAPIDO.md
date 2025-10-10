# 🚀 INICIO RÁPIDO - Simulador DGII

## Para empezar a probar la aplicación AHORA MISMO:

### 1️⃣ Verificar Instalación

```powershell
python verify_simulator_setup.py
```

Este script verifica que todo esté instalado correctamente.

### 2️⃣ Ejecutar Pruebas Automáticas

```powershell
python test_simulator_complete.py
```

Este script prueba automáticamente:
- ✅ Envío de e-CF
- ✅ Consulta de estado
- ✅ Generación de e-CF de proveedor
- ✅ Acuse de recibo (ACECFAR)

### 3️⃣ Configurar el Simulador en ERPNext

1. **Ir a DGII Configuration**
2. **Establecer "Modo API" = `simulator`**
3. **Guardar**

¡Listo! Ahora puedes crear facturas en ERPNext y el sistema usará el simulador.

---

## 📖 Documentación Completa

- **[GUIA_RAPIDA_SIMULADOR.md](GUIA_RAPIDA_SIMULADOR.md)** - Guía detallada paso a paso
- **[RESUMEN_SIMULADOR.md](RESUMEN_SIMULADOR.md)** - Qué se implementó
- **[csf_do/docs/SIMULADOR_DGII.md](csf_do/docs/SIMULADOR_DGII.md)** - Documentación técnica
- **[csf_do/docs/MODULO_ACECFAR.md](csf_do/docs/MODULO_ACECFAR.md)** - Módulo ACECFAR

---

## ⚡ Solución Rápida de Problemas

**Error: "DGII Configuration not found"**
→ Ir a DGII Configuration y completar RNC Emisor y Modo API

**Error: "Simulador no está activo"**
→ Verificar que Modo API = `simulator` en DGII Configuration

**Las pruebas fallan**
→ Ejecutar dentro del contexto de Frappe: `bench --site [sitio] console`

---

## 📞 Estado del Proyecto

✅ **SIMULADOR DGII**: Completado y funcional
✅ **MÓDULO ACECFAR**: Completado y funcional
✅ **TESTS**: Implementados y pasando
✅ **DOCUMENTACIÓN**: Completa

**El simulador está LISTO para probar la aplicación.**

Ver [PROGRESO_IMPLEMENTACION.md](PROGRESO_IMPLEMENTACION.md) para más detalles.
