# Refactorización: Kenya → República Dominicana

## Plan de Refactorización CSF_KE → CSF_DO

### **Fase 1: Configuración Base** ✅
- [x] **setup.py** - Cambiar nombre del proyecto y metadatos
- [x] **README.md** - Actualizar documentación principal
- [x] **MANIFEST.in** - Actualizar archivos incluidos
- [x] **requirements.txt** - Verificar dependencias
- [x] **LICENSE** - Mantener o actualizar según necesidad

### **Fase 2: Configuración del Módulo** ✅
- [x] **csf_ke/__init__.py** - Cambiar nombre del módulo
- [x] **csf_ke/config/csf_ke.py** - Actualizar configuraciones principales
- [x] **csf_ke/config/desktop.py** - Actualizar workspace y menús
- [x] **csf_ke/config/docs.py** - Actualizar documentación
- [x] **csf_ke/hooks.py** - Actualizar hooks del sistema
- [x] **csf_ke/modules.txt** - Actualizar módulos
- [x] **csf_ke/patches.txt** - Actualizar patches

### **Fase 3: Renombrar Directorios Principales** ✅
- [x] **csf_ke/** → **csf_do/**
- [x] **csf_ke/csf_ke/** → **csf_do/csf_do/**
- [x] **csf_ke/workspace/kenya/** → **csf_do/workspace/dominican_republic/**

### **Fase 4: Doctypes - Impuestos y Contribuciones** ✅
- [x] **vat_withholding** → **itbis_withholding** (VAT → ITBIS)
- [x] **tims_hscode** → **ncf_hscode** (TIMs → NCF)
- [x] **selling_item_price_margin** - Mantener (aplicable a RD)
- [x] **employee_dependent_and_beneficiary** - Mantener (aplicable a RD)
- [x] **employee_separation_type** - Mantener (aplicable a RD)
- [x] **job_applicant** - Mantener (aplicable a RD)
- [x] **relationship** - Mantener (aplicable a RD)

### **Fase 5: Reportes de Impuestos** ✅
- [x] **kenya_sales_tax_report** → **dominican_sales_tax_report** (VAT → ITBIS)
- [x] **kenya_purchase_tax_report** → **dominican_purchase_tax_report** (VAT → ITBIS)
- [x] **kenya_p9a_tax_deduction_card_report** → **dominican_rst_declaration_report** (P9A → RST)
- [x] **kenya_p10_tax_report** → **dominican_rst_monthly_report** (P10 → RST Mensual)
- [x] **withholding_tax** → **itbis_withholding_tax** (VAT → ITBIS)

### **Fase 6: Reportes de Nómina y Contribuciones** ✅
- [x] **kenya_nssf_report** → **dominican_sfs_report** (NSSF → SFS)
- [x] **kenya_nhif_report** → **dominican_sns_report** (NHIF → SNS)
- [x] **kenya_housing_levy_contribution** → **dominican_ipi_contribution** (Housing Levy → IPI)
- [x] **kenya_helb_report** → **dominican_educational_loans_report** (HELB → Préstamos Educativos)
- [x] **kenya_shif_contribution** → **dominican_health_insurance_report** (SHIF → Seguro de Salud)
- [x] **kenya_payroll_register_report** → **dominican_payroll_register_report**
- [x] **kenya_bank_payroll_advice_report** → **dominican_bank_payroll_advice_report**

### **Fase 7: Reportes Generales** ✅
- [x] **periodic_payroll_comparison** - Mantener (aplicable a RD)
- [x] **budget_variance_report_enhanced** - Mantener (aplicable a RD)
- [x] **customer_addresses** - Mantener (aplicable a RD)
- [x] **customer_contacts** - Mantener (aplicable a RD)
- [x] **gross_profit_report** - Mantener (aplicable a RD)
- [x] **sales_analytics_enhanced** - Mantener (aplicable a RD)
- [x] **sales_person_wise_transaction_summary_enhanced** - Mantener (aplicable a RD)
- [x] **payment_period_based_on_invoice_date_enhanced** - Mantener (aplicable a RD)

### **Fase 8: Overrides y Patches** ✅
- [x] **overrides/customer.py** - Actualizar validación PIN → RNC
- [x] **overrides/customer.js** - Actualizar validación PIN → RNC
- [x] **overrides/validate_pin.py** → **validate_rnc.py**
- [x] **overrides/sales_doc.py** - Actualizar para ITBIS
- [x] **overrides/job_card.py** - Mantener (aplicable a RD)
- [x] **patches/** - Actualizar todos los patches para RD

### **Fase 9: Utilidades** ✅
- [x] **utils/get_tims_hscode.py** → **utils/get_ncf_hscode.py**
- [x] **utils/qr_code_generator.py** - Mantener (aplicable a RD)

### **Fase 10: Web Forms** ✅
- [x] **web_form/job_application** - Mantener (aplicable a RD)

### **Fase 11: Documentación** ✅
- [x] **docs/doctypes/** - Actualizar toda la documentación
- [x] **docs/features/** - Actualizar características
- [x] **docs/reports/** - Actualizar documentación de reportes
- [ ] **docs/images/** - Actualizar imágenes y capturas

### **Fase 12: Fixtures** ✅
- [x] **fixtures/custom_field.json** - Actualizar campos personalizados
- [x] **fixtures/doctype_link.json** - Actualizar enlaces
- [x] **fixtures/selling.json** - Actualizar para ITBIS

### **Fase 13: Workspace** ✅
- [x] **workspace/kenya/kenya.json** → **workspace/dominican_republic/dominican_republic.json**

### **Fase 14: Templates** ✅
- [x] **templates/** - Actualizar plantillas para RD

---

## **Mapeo de Conceptos Clave**

| **Kenya** | **República Dominicana** | **Tasa/Detalle** |
|-----------|---------------------------|------------------|
| VAT 16% | ITBIS 18% | Impuesto al Valor Agregado |
| KRA | DGII | Dirección General de Impuestos Internos |
| TIMs | NCF/e-NCF | Número de Comprobante Fiscal |
| P9A | RST Declaración | Régimen Simplificado de Tributación |
| P10 | RST Mensual | Reporte Mensual RST |
| NSSF | SFS | Sistema de Fondo de Seguridad |
| NHIF | SNS | Sistema Nacional de Salud |
| Housing Levy 1.5% | IPI | Impuesto sobre Propiedad Inmobiliaria |
| HELB | Préstamos Educativos | Préstamos Estudiantiles |
| PIN | RNC | Registro Nacional del Contribuyente |

---

## **Notas de Refactorización**

### **Cambios de Tasa de Impuestos:**
- VAT 16% → ITBIS 18%
- Verificar todas las referencias a tasas de impuestos

### **Cambios de Nomenclatura:**
- `kenya_*` → `dominican_*` o `do_*`
- `csf_ke` → `csf_do`
- `tims_*` → `ncf_*`
- `vat_*` → `itbis_*`

### **Mantener Estructura:**
- No crear archivos nuevos
- Solo renombrar y editar existentes
- Mantener la lógica de negocio
- Adaptar solo los conceptos fiscales

---

## **Estado del Proyecto**
- **Inicio:** [Fecha]
- **Progreso:** 0/14 Fases completadas
- **Última actualización:** [Fecha]
