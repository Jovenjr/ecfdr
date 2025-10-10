# 🐳 Instalación en Docker - CSF_DO (ECFDR)

## 📋 Requisitos Previos

- Docker y Docker Compose instalados y corriendo
- Contenedor de Frappe/ERPNext en ejecución
- Acceso al contenedor (docker exec)
- Conexión a Internet (para clonar desde GitHub)

---

## 🚀 Paso 1: Identificar el Contenedor

Primero, identifica el nombre de tu contenedor de Frappe:

```powershell
# Listar todos los contenedores en ejecución
docker ps

# O buscar específicamente contenedores de Frappe
docker ps | Select-String "frappe"
```

**Busca el contenedor que dice algo como:**
- `frappe-bench-1`
- `erpnext_frappe_1`
- `frappe_worker_1`
- O similar con "frappe" o "erpnext" en el nombre

**Anota el nombre del contenedor**, lo necesitarás en los siguientes pasos.

---

## 🔐 Paso 2: Entrar al Contenedor

Reemplaza `NOMBRE_CONTENEDOR` con el nombre que encontraste:

```powershell
docker exec -it NOMBRE_CONTENEDOR bash
```

**Ejemplos:**
```powershell
# Si tu contenedor se llama frappe-bench-1
docker exec -it frappe-bench-1 bash

# Si tu contenedor se llama erpnext_frappe_1
docker exec -it erpnext_frappe_1 bash
```

**Deberías ver un prompt como:**
```bash
frappe@abc123:/home/frappe/frappe-bench$
```

---

## 📦 Paso 3: Navegar al Directorio de Bench

Dentro del contenedor:

```bash
# Ir al directorio de bench (usualmente ya estás ahí)
cd ~/frappe-bench

# O si no funciona:
cd /home/frappe/frappe-bench

# Verificar que estés en el directorio correcto
pwd
# Debe mostrar: /home/frappe/frappe-bench

# Ver las apps instaladas actualmente
ls -la apps/
```

---

## 🔽 Paso 4: Obtener la Aplicación desde GitHub

Ahora vamos a descargar la aplicación desde tu repositorio:

```bash
# Opción 1: Usar bench get-app (RECOMENDADO)
bench get-app https://github.com/Jovenjr/ecfdr.git --branch ecfdr

# Opción 2: Si la opción 1 falla, clonar manualmente
cd apps/
git clone -b ecfdr https://github.com/Jovenjr/ecfdr.git csf_do
cd ..
```

**Verificar que se descargó correctamente:**
```bash
ls -la apps/csf_do/
# Deberías ver los archivos de la aplicación
```

---

## 🏗️ Paso 5: Instalar Dependencias Python

Instalar las dependencias necesarias:

```bash
# Instalar desde requirements.txt
cd apps/csf_do
pip install -r requirements.txt

# O instalar manualmente las dependencias principales
pip install requests lxml cryptography xmlsec pycryptodome

# Volver al directorio bench
cd ~/frappe-bench
```

---

## 🔧 Paso 6: Instalar la App en tu Sitio

Primero, identifica el nombre de tu sitio:

```bash
# Listar sitios disponibles
bench --site all list

# O ver en el directorio sites
ls sites/
```

**El nombre del sitio usualmente es algo como:**
- `site1.local`
- `localhost`
- `erp.tudominio.com`
- O el nombre que configuraste

**Instalar la app en el sitio:**

```bash
# Reemplaza NOMBRE_SITIO con tu sitio
bench --site NOMBRE_SITIO install-app csf_do
```

**Ejemplo:**
```bash
bench --site site1.local install-app csf_do
```

**Este proceso puede tardar varios minutos. Verás mensajes como:**
```
Installing csf_do...
Migrating csf_do
Updating DocTypes for csf_do: 100%
Installing fixtures...
```

---

## ✅ Paso 7: Verificar la Instalación

### 7.1 Verificar que la app está instalada

```bash
bench --site NOMBRE_SITIO list-apps
```

**Deberías ver `csf_do` en la lista.**

### 7.2 Ejecutar migraciones (por si acaso)

```bash
bench --site NOMBRE_SITIO migrate
```

### 7.3 Limpiar cache

```bash
bench --site NOMBRE_SITIO clear-cache
bench --site NOMBRE_SITIO clear-website-cache
```

### 7.4 Reiniciar bench

```bash
bench restart
```

---

## 🧪 Paso 8: Probar la Instalación

### Desde el contenedor (bench console):

```bash
bench --site NOMBRE_SITIO console
```

**Dentro de la consola, ejecuta:**

```python
# Verificar importación
import csf_do
print("CSF_DO instalado correctamente!")

# Verificar el simulador
from csf_do.csf_do.integrations.dgii_client import get_dgii_client
client = get_dgii_client()
info = client.get_info()
print(info)

# Salir
exit()
```

### Desde la interfaz web de ERPNext:

1. **Abrir tu navegador**
2. **Ir a:** `http://localhost:8000` (o tu URL de ERPNext)
3. **Iniciar sesión**
4. **Buscar:** "DGII Configuration"
5. **Si aparece** = ✅ Instalación exitosa

---

## ⚙️ Paso 9: Configurar el Simulador

Desde la interfaz de ERPNext:

1. **Ir a:** DGII Configuration
2. **Completar:**
   - **RNC Emisor:** Tu RNC (ej: 123456789)
   - **Versión e-CF:** 1.0
   - **Modo API:** `simulator` ← **IMPORTANTE para usar el simulador**
   - **Pre-Certificación Base URL:** `https://ecf.dgii.gov.do/testecf/`
   - **Certificación Base URL:** `https://ecf.dgii.gov.do/certecf/`
   - **Producción Base URL:** `https://ecf.dgii.gov.do/ecf/`
3. **Guardar**

---

## 🎯 Paso 10: Probar el Simulador

Desde bench console:

```bash
bench --site NOMBRE_SITIO console
```

```python
from csf_do.csf_do.integrations.dgii_client import get_dgii_client

# Obtener cliente
client = get_dgii_client()

# Verificar modo
info = client.get_info()
print(f"Modo: {info['modo']}")  # Debe ser 'simulator'
print(f"Simulador activo: {info['simulador_activo']}")  # Debe ser True

# Probar envío
result = client.enviar_ecf("<xml>test</xml>", "31", "B0100000001")
print(f"Track ID: {result.get('track_id')}")

# Consultar estado
import time
time.sleep(35)
estado = client.consultar_estado(result['track_id'])
print(f"Estado: {estado['estado']}")  # ACEPTADO o RECHAZADO

exit()
```

---

## 📝 Comandos Completos - Resumen

```powershell
# 1. En tu PowerShell (Windows)
docker ps
docker exec -it NOMBRE_CONTENEDOR bash

# 2. Dentro del contenedor
cd ~/frappe-bench
bench get-app https://github.com/Jovenjr/ecfdr.git --branch ecfdr
cd apps/csf_do
pip install -r requirements.txt
cd ~/frappe-bench
bench --site NOMBRE_SITIO install-app csf_do
bench --site NOMBRE_SITIO migrate
bench --site NOMBRE_SITIO clear-cache
bench restart

# 3. Verificar
bench --site NOMBRE_SITIO list-apps
bench --site NOMBRE_SITIO console
```

---

## 🐛 Solución de Problemas

### Error: "No such container"
**Solución:** Verifica el nombre exacto con `docker ps`

### Error: "bench: command not found"
**Solución:** 
```bash
# Verificar ubicación de bench
which bench

# Si no está, agregarlo al PATH o usar ruta completa
/home/frappe/frappe-bench/env/bin/bench --site ...
```

### Error: "App csf_do already exists"
**Solución:** La app ya está descargada, solo instálala en el sitio:
```bash
bench --site NOMBRE_SITIO install-app csf_do
```

### Error: "Cannot connect to GitHub"
**Solución:** Verificar conectividad:
```bash
ping github.com
# Si no funciona, verificar configuración de red del contenedor
```

### Error al instalar: "Permission denied"
**Solución:** Verificar usuario:
```bash
whoami  # Debe ser 'frappe'
# Si no, salir y entrar con:
docker exec -it -u frappe NOMBRE_CONTENEDOR bash
```

### Error: "Site not found"
**Solución:** Listar sitios disponibles:
```bash
bench --site all list
ls sites/
```

### La app se instala pero no aparece en ERPNext
**Solución:**
```bash
bench --site NOMBRE_SITIO migrate
bench --site NOMBRE_SITIO clear-cache
bench restart
# Refrescar navegador con Ctrl+F5
```

---

## 🔄 Actualizar la Aplicación (Después de cambios)

Cuando hagas cambios y los subas a GitHub:

```bash
# 1. Entrar al contenedor
docker exec -it NOMBRE_CONTENEDOR bash

# 2. Actualizar el código
cd ~/frappe-bench/apps/csf_do
git pull origin ecfdr

# 3. Migrar cambios
cd ~/frappe-bench
bench --site NOMBRE_SITIO migrate

# 4. Limpiar cache y reiniciar
bench --site NOMBRE_SITIO clear-cache
bench restart
```

---

## 📚 Documentación Adicional

Después de instalar, consulta:

- **INICIO_RAPIDO.md** - Cómo empezar a usar el simulador
- **GUIA_RAPIDA_SIMULADOR.md** - Guía completa de uso
- **INSTRUCCIONES_PRUEBA.md** - Cómo probar el simulador
- **INDICE_DOCUMENTACION.md** - Índice de toda la documentación

---

## ✅ Checklist de Instalación

- [ ] Identificar nombre del contenedor Docker
- [ ] Entrar al contenedor (`docker exec -it ...`)
- [ ] Descargar app desde GitHub (`bench get-app`)
- [ ] Instalar dependencias (`pip install -r requirements.txt`)
- [ ] Instalar app en sitio (`bench install-app`)
- [ ] Migrar (`bench migrate`)
- [ ] Limpiar cache (`bench clear-cache`)
- [ ] Reiniciar (`bench restart`)
- [ ] Verificar en ERPNext (buscar "DGII Configuration")
- [ ] Configurar modo simulador
- [ ] Probar el simulador

---

## 🎉 ¡Listo!

Si completaste todos los pasos, la aplicación CSF_DO está instalada y el simulador DGII está listo para usar.

**Próximo paso:** Leer `INICIO_RAPIDO.md` y crear tu primera factura de prueba.

---

## 📞 Comandos Rápidos de Referencia

```bash
# Ver logs en tiempo real
bench --site NOMBRE_SITIO watch

# Ver logs de errores
cat sites/NOMBRE_SITIO/logs/site_errors.txt

# Reinstalar la app (si es necesario)
bench --site NOMBRE_SITIO uninstall-app csf_do
bench --site NOMBRE_SITIO install-app csf_do

# Ejecutar tests
bench --site NOMBRE_SITIO run-tests --app csf_do

# Salir del contenedor
exit
```

---

**URL del Repositorio:** https://github.com/Jovenjr/ecfdr  
**Rama:** ecfdr
