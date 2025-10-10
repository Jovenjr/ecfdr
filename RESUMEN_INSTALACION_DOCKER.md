# 🎯 RESUMEN FINAL - Instalación en Docker

## ✅ Estado Actual

✅ **Código subido a GitHub:**
- Repositorio: https://github.com/Jovenjr/ecfdr
- Rama: `ecfdr`
- Último commit: Simulador DGII completo + Guías de instalación Docker

✅ **Archivos de instalación creados:**
- `INSTALACION_DOCKER.md` - Guía completa paso a paso
- `install_docker_windows.ps1` - Script automático para Windows
- `install_docker.sh` - Script para ejecutar dentro del contenedor

---

## 🚀 OPCIÓN 1: Instalación Automática (RECOMENDADO)

### Desde Windows PowerShell:

```powershell
# Ejecutar el script automático
.\install_docker_windows.ps1

# O especificar contenedor y sitio:
.\install_docker_windows.ps1 -NombreContenedor "frappe-bench-1" -NombreSitio "site1.local"
```

**El script automáticamente:**
- ✅ Detecta tu contenedor de Frappe
- ✅ Verifica tu sitio
- ✅ Descarga la app desde GitHub
- ✅ Instala dependencias
- ✅ Instala en el sitio
- ✅ Ejecuta migraciones
- ✅ Limpia cache
- ✅ Reinicia bench

**Tiempo estimado: 3-5 minutos**

---

## 🔧 OPCIÓN 2: Instalación Manual

### Paso 1: Identificar tu contenedor

```powershell
docker ps
```

Busca el contenedor con "frappe" o "erpnext" en el nombre.

### Paso 2: Entrar al contenedor

```powershell
# Reemplaza NOMBRE_CONTENEDOR con el que encontraste
docker exec -it NOMBRE_CONTENEDOR bash
```

### Paso 3: Instalar la app

Dentro del contenedor:

```bash
# Ir al directorio bench
cd ~/frappe-bench

# Descargar la app desde GitHub
bench get-app https://github.com/Jovenjr/ecfdr.git --branch ecfdr

# Instalar dependencias
cd apps/csf_do
pip install -r requirements.txt
cd ~/frappe-bench

# Instalar en tu sitio (reemplaza site1.local con tu sitio)
bench --site site1.local install-app csf_do

# Migrar
bench --site site1.local migrate

# Limpiar cache
bench --site site1.local clear-cache

# Reiniciar
bench restart
```

### Paso 4: Verificar

```bash
# Ver apps instaladas
bench --site site1.local list-apps

# Debe aparecer 'csf_do' en la lista
```

---

## ⚙️ Configurar el Simulador

### Desde la interfaz web de ERPNext:

1. **Abrir tu navegador** y ir a ERPNext
2. **Buscar:** "DGII Configuration"
3. **Completar:**
   - RNC Emisor: Tu RNC
   - Versión e-CF: 1.0
   - **Modo API: simulator** ← IMPORTANTE
   - Pre-Certificación Base URL: `https://ecf.dgii.gov.do/testecf/`
   - Certificación Base URL: `https://ecf.dgii.gov.do/certecf/`
   - Producción Base URL: `https://ecf.dgii.gov.do/ecf/`
4. **Guardar**

---

## 🧪 Probar la Instalación

### Desde bench console:

```powershell
# Entrar al contenedor
docker exec -it NOMBRE_CONTENEDOR bash

# Abrir console
bench --site site1.local console
```

Dentro de la console:

```python
# Importar el cliente
from csf_do.csf_do.integrations.dgii_client import get_dgii_client

# Obtener cliente
client = get_dgii_client()

# Verificar configuración
info = client.get_info()
print(info)
# Debe mostrar: {"modo": "simulator", "simulador_activo": True, ...}

# Probar conexión
test = client.test_connection()
print(test)
# Debe mostrar: {"success": True, "mensaje": "Simulador activo..."}

# Salir
exit()
```

---

## 📋 Comandos Completos - Copia y Pega

### Windows PowerShell (Automático):
```powershell
.\install_docker_windows.ps1
```

### Dentro del Contenedor (Manual):
```bash
cd ~/frappe-bench
bench get-app https://github.com/Jovenjr/ecfdr.git --branch ecfdr
cd apps/csf_do && pip install -r requirements.txt && cd ~/frappe-bench
bench --site site1.local install-app csf_do
bench --site site1.local migrate
bench --site site1.local clear-cache
bench restart
```

---

## 🔍 Verificación Rápida

Después de instalar, verifica:

```bash
# 1. Apps instaladas
bench --site site1.local list-apps | grep csf_do

# 2. DocTypes disponibles
bench --site site1.local console
>>> import frappe
>>> frappe.get_doc("DGII Configuration")
>>> exit()
```

Si ambos funcionan = ✅ Instalación exitosa

---

## 📚 Documentación Disponible

Después de instalar:

1. **INICIO_RAPIDO.md** - Cómo empezar (3 pasos)
2. **GUIA_RAPIDA_SIMULADOR.md** - Guía completa
3. **INSTRUCCIONES_PRUEBA.md** - Cómo probar
4. **INSTALACION_DOCKER.md** - Detalles de instalación
5. **INDICE_DOCUMENTACION.md** - Índice completo

---

## 🐛 Solución de Problemas Comunes

### Error: "No se encuentra el contenedor"
```powershell
# Ver contenedores en ejecución
docker ps
```

### Error: "Site not found"
```bash
# Listar sitios disponibles
ls ~/frappe-bench/sites/
bench --site all list
```

### Error: "App already installed"
```bash
# Si necesitas reinstalar
bench --site site1.local uninstall-app csf_do
bench --site site1.local install-app csf_do
```

### Error: "DGII Configuration not found"
```bash
# Migrar de nuevo
bench --site site1.local migrate
bench --site site1.local clear-cache
bench restart
```

---

## 🔄 Actualizar Después de Cambios

Cuando hagas cambios y los subas a GitHub:

```bash
# Entrar al contenedor
docker exec -it NOMBRE_CONTENEDOR bash

# Actualizar código
cd ~/frappe-bench/apps/csf_do
git pull origin ecfdr

# Migrar y reiniciar
cd ~/frappe-bench
bench --site site1.local migrate
bench --site site1.local clear-cache
bench restart
```

---

## ✅ Checklist Final

- [ ] Código subido a GitHub ✅
- [ ] Contenedor identificado
- [ ] App descargada desde GitHub
- [ ] Dependencias instaladas
- [ ] App instalada en el sitio
- [ ] Migraciones ejecutadas
- [ ] Cache limpiado
- [ ] Bench reiniciado
- [ ] DGII Configuration existe en ERPNext
- [ ] Modo API = simulator configurado
- [ ] Simulador probado y funciona

---

## 🎉 ¡Ya Está Todo Listo!

**Repositorio GitHub:** https://github.com/Jovenjr/ecfdr  
**Rama:** ecfdr

**Próximo paso:** 
1. Ejecutar `.\install_docker_windows.ps1`
2. Configurar DGII Configuration
3. Leer `INICIO_RAPIDO.md`

---

## 📞 Archivos Importantes

- `INSTALACION_DOCKER.md` - Guía detallada
- `install_docker_windows.ps1` - Script automático Windows
- `install_docker.sh` - Script para contenedor
- `INICIO_RAPIDO.md` - Inicio rápido
- `GUIA_RAPIDA_SIMULADOR.md` - Guía completa

**¡Todo está listo para instalar! 🚀**
