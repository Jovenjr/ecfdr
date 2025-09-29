# Fase 0 · Pipeline CI/CD Inicial

## Objetivos
- Validar calidad de código y cumplimiento normativo DGII de manera automática.
- Garantizar que cada cambio genere XML firmados válidos antes de integrar.

## Etapas del Pipeline
1. **Preparación**
   - Instalar dependencias (`pip install -r requirements.txt`).
   - Configurar variables de entorno (`DGII_ENV=PRECERT`, rutas a certificados dummy).
2. **Lint y Estilo**
   - `ruff` / `flake8` para Python.
   - Validación de formato JSON/YAML (`python -m json.tool`, `yamllint`).
3. **Tests Unitarios**
   - `pytest` (incluir `csf_do/csf_do/tests/` y `test_ecfdr_integration.py`).
4. **Validación XML/XSD**
   - Generar muestras e-CF (tipos 31, 32, 33, 34, 41, 43, 44, 45, 46, 47).
   - Ejecutar `python -m csf_do.csf_do.utils.validate_cli --xsd <tipo>` (script a definir) para cada XML.
   - Verificar ausencia de campos vacíos.
5. **Firma Digital en Staging**
   - Usar certificado sandbox para firmar XML (`signing.py`).
   - Verificar hash SHA-256 y SN del certificado.
6. **Validación de nombres de archivo**
   - Asegurar patrón `RNCEmisor+eNCF.xml`.
7. **Generación ARECF/ACECF**
   - Construir y validar XML de receptor (ARECF/ACECF) contra XSD.
8. **Reportes y Fixtures**
   - Validar fixtures (`bench --site test migrate` en entorno CI).
   - Generar previsualizaciones de RI (opcional con pruebas visuales).
9. **Publicación de Artefactos**
   - Guardar XML y logs en almacenamiento de CI (artifact store) para auditoría.
10. **Notificaciones**
    - Enviar resultados a Slack/Teams con resumen de errores DGII.

## Integraciones Futuras (Fase 1+)
- Pruebas de integración contra DGII Mock (`dgii_mock.py`).
- Tests de recepción (ARECF/ACECF) en colas.
- Escaneos de seguridad (SAST/DAST) y compliance (SonarQube).

## Checklist de Pipeline
- [ ] Scripts reproducibles para generar XML de prueba.
- [ ] Certificado sandbox en vault de CI.
- [ ] Jobs configurados en plataforma CI (GitHub Actions, GitLab CI, etc.).
- [ ] Notificaciones automáticas.
- [ ] Documentación del pipeline en `docs/`.
