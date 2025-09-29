# ERPNext Country Specific Functionality for Dominican Republic (CSF_DO)

## _*Enhancing ERPNext with Dominican Republic-specific features for tax compliance, payroll, and localized business needs.*_

## Overview

This is a custom application designed to extend the capabilities of [ERPNext](https://erpnext.com/) to meet the unique regulatory and operational requirements of businesses in Dominican Republic. Originally developed by [Navari Limited](https://navari.co.ke) for Kenya, this app has been refactored to provide seamless integration with Dominican tax systems, localized payroll reporting, and additional tools tailored to streamline business processes in the Dominican Republic.

Key features include:

- Tax compliance with Dirección General de Impuestos Internos (DGII) regulations.
- Integration with NCF/e-NCF (Número de Comprobante Fiscal) system.
- Comprehensive payroll reports for statutory deductions.
- Localized financial and tax reporting for Dominican Republic.

This README provides an overview of the application, its features, installation instructions, and additional resources to get you started.

---

## Features

### 1. Dominican Republic Payroll Reports

Designed to ensure compliance with Dominican Republic payroll regulations, these reports generate the necessary documentation for statutory deductions and employee payments.

- **[RST Declaration Setup](csf_do/docs/features/RST_declaration_setup.md)**  
  Explains the process of mapping salary components for RST (Régimen Simplificado de Tributación)
- **[RST Declaration Report](csf_do/docs/reports/dominican_rst_declaration_report.md)**  
  Summarizes annual tax deductions for employees, required for RST tax filing.
- **[RST Monthly Report](csf_do/docs/reports/dominican_rst_monthly_report.md)**  
  Monthly tax return report submitted by employers to DGII.
- **[Periodic Payroll Comparison Report](csf_do/docs/reports/periodic_payroll_comparison.md)**  
  Compares salary slips between the current month and the previous month, providing a detailed breakdown of changes in salary components (Earnings, Deductions) and Loan repayments.
- **SFS Report**  
  Tracks contributions to the Sistema de Fondo de Seguridad (SFS) for employee social security.
- **SNS Report**  
  Provides a clear overview of employee Sistema Nacional de Salud (SNS) contributions.
- **Educational Loans Report**  
  Summarizes deductions for educational loans repayments.
- **Bank Payroll Advice Report**  
  Generates bank-ready instructions for salary disbursements.
- **Payroll Register Report**  
  Provides a detailed breakdown of payroll transactions for record-keeping and auditing.
- **IPI Contribution Report**  
  Provides a clear and concise overview of essential employee information alongside their gross salary contributions for Impuesto sobre Propiedad Inmobiliaria (IPI).

### 2. Tax Reports

Streamlined reporting for sales and purchase taxes to ensure compliance with Dominican Republic tax laws.

- **[Sales Tax Report](csf_do/docs/reports/dominican_sales_tax_report.md)**  
  Summarizes ITBIS and other taxes collected from sales transactions.
- **[Purchase Tax Report](csf_do/docs/reports/dominican_purchase_tax_report.md)**  
  Details ITBIS and taxes paid on purchases for accurate tax reconciliation.

### 3. Tax Compliance Features

Custom fields and integrations to meet DGII tax regulations and facilitate seamless reporting.

- **Custom NCF Fields in Invoices**  
  Captures NCF/e-NCF invoice details in Sales and Purchase Invoices for Electronic Tax Register (ETR) compliance.
- **NCF HSCode Integration**  
  Links items to Harmonized System (HS) codes for accurate tax classification and reporting.  
  _[Learn more](csf_do/docs/features/ncf_integration.md)_.
- **[ITBIS Withholding](csf_do/docs/doctypes/itbis_withholding.md)**  
  Simplifies importing ITBIS withholding data from the DGII website into ERPNext for reconciliation.

#### NCF Parser Integration

For NCF integration, we partner with [Cecypo](https://docs.cecypo.tech/s/kb/doc/erpnext-O7U5xeE9DN). Contact them for installation and setup assistance.

### Electronic Invoicing (e-CF) Builders

This app includes XML builders and validators for DGII e-CF (electronic NCF). Builders generate minimal valid XMLs per XSD and enforce business rules prior to submission.

- No empty tags policy: Builders only output tags with content. Empty tags can cause DGII rejections. A single exception exists in e-CF 32 (see below), where the XSD requires the presence of `Comprador`. In that case we auto-fill sensible defaults to avoid a truly empty tag.
- XSD-driven pre-validation: We extract required paths from official XSDs into `csf_do/csf_do/specs/*.json` and verify input before building.
- Final XSD validation: All generated XMLs are validated with lxml against the official XSDs.
- Catalog checks: When catalog JSONs are present (e.g., `unidad_medida.json`, `tipo_moneda.json`), builders validate that codes belong to the allowed sets.
- Totals coherence: Builders assert that the sum of line amounts matches header totals (with small tolerance), both in base currency and in Otra Moneda when provided.

Required minimal fields per type

- e-CF 31 (Factura de Crédito Fiscal)
  - `Encabezado/Version`
  - `Encabezado/IdDoc`: `TipoeCF`, `eNCF`, `FechaVencimientoSecuencia`, `TipoIngresos`, `TipoPago`
  - `Encabezado/Emisor`: `RNCEmisor`, `RazonSocialEmisor`, `DireccionEmisor`, `FechaEmision`
  - `Encabezado/Comprador`: `RNCComprador`, `RazonSocialComprador`
  - `Encabezado/Totales`: `MontoTotal`
  - `DetallesItems/Item`: `NumeroLinea`, `IndicadorFacturacion`, `NombreItem`, `IndicadorBienoServicio`, `CantidadItem`, `PrecioUnitarioItem`, `MontoItem`
  - `FechaHoraFirma`

- e-CF 32 (Factura de Consumo)
  - `Encabezado/Version`
  - `Encabezado/IdDoc`: `TipoeCF`, `eNCF`, `TipoIngresos`, `TipoPago`
  - `Encabezado/Emisor`: `RNCEmisor`, `RazonSocialEmisor`, `DireccionEmisor`, `FechaEmision`
  - `Encabezado/Comprador`: The block must be present by XSD. If left empty in input, the builder auto-fills: `RNCComprador = "000000000"`, `RazonSocialComprador = "CONSUMIDOR FINAL"` to avoid an empty tag while staying compliant.
  - `Encabezado/Totales`: `MontoTotal`
  - `DetallesItems/Item`: `NumeroLinea`, `IndicadorFacturacion`, `NombreItem`, `IndicadorBienoServicio`, `CantidadItem`, `PrecioUnitarioItem`, `MontoItem`
  - `FechaHoraFirma`

- e-CF 43 (Gastos Menores)
  - `Encabezado/Version`
  - `Encabezado/IdDoc`: `TipoeCF`, `eNCF`, `FechaVencimientoSecuencia`
  - `Encabezado/Emisor`: `RNCEmisor`, `RazonSocialEmisor`, `DireccionEmisor`, `FechaEmision`
  - `Encabezado/Totales`: `MontoTotal`
  - `DetallesItems/Item`: `NumeroLinea`, `IndicadorFacturacion`, `NombreItem`, `IndicadorBienoServicio`, `CantidadItem`, `PrecioUnitarioItem`, `MontoItem`
  - `FechaHoraFirma`

Notes

- Builders normalize date fields to DD-MM-YYYY and DateTime to "DD-MM-YYYY HH:MM:SS".
- Friendly format checks: `eNCF` (13 alphanumeric), `RNC` (9 or 11 digits), telephone format `ddd-ddd-dddd`, basic email pattern.
- A mock DGII client is included for local testing (use base_url starting with `mock://`).

### 4. Additional Features

 - **[Selling Item Price Margin](csf_do/docs/doctypes/selling_item_price_margin.md)**  
  Calculates and tracks profit margins on sales items to aid in pricing and profitability analysis.

---

## Installation 🛠️

Follow the instructions below to install CSF_DO on your ERPNext instance. You can choose between self-hosting with Frappe Bench or using FrappeCloud.

### Prerequisites

- A working ERPNext instance (v13 or higher recommended).
- Access to a terminal with `bench` commands enabled (for self-hosting).
- Git installed on your system.

### Option 1: Manual Installation (Self-Hosting)

1. **Set Up Frappe Bench**  
   If you don't already have a Frappe Bench instance, follow the [official Frappe installation guide](https://frappeframework.com/docs/user/en/installation) to set it up.

2. **Add the CSF_DO App**  
   In your Bench directory, run the following command to download the app from GitHub:

   ```sh
   bench get-app https://github.com/navariltd/navari_csf_do.git
   ```

3. **Install the App on Your Site**
   Replace `<your.site.name.here>` with your ERPNext site name and run:

   ```sh
   bench --site <your.site.name.here> install-app csf_do
   ```

4. **Verify Installation**

   Restart your Bench instance and log in to ERPNext to confirm that the `CSF_DO` app appears in your app list.

---

### Option 2: FrappeCloud Installation ☁️

1. **Set Up a FrappeCloud Account**
   Sign up or log in to [FrappeCloud](https://frappecloud.com/).

2. Create a Bench and Site
   Follow the FrappeCloud dashboard instructions to create a new Bench and site.

3. Add the CSF_DO App

   - Navigate to the **Apps** tab in your Bench.
   - Click **Add App**.
   - Search **Navari CSF DO**
   - Click **Install**.
     OR
   - [Frappe Cloud Marketplace](https://frappecloud.com/marketplace/apps/csf_do)
   - Click **Install Now**.

4. Activate the App

- Once installed in your bench, add the app on your site via the FrappeCloud interface.

---

## Configuration

After installation, configure the app to suit your business needs:

1. Set Up Tax Rules

- Define ITBIS, set up RST Declaration, and withholding tax settings in ERPNext's **Accounts** module.

2. Link NCF Integration

- Contact [Cecypo](mailto:support@cecypo.tech) for NCF Parser setup.

### Test Reports

- Run sample payroll and tax reports to ensure data accuracy.
- Make some transactions to ensure NCF Tax fields are setup.

---

## Environment variables and local scripts

For local development and the helper script `run_enviar_ecf.py`, you may set:

- `P12_PATH` — absolute path to your PKCS#12 file (.p12/.pfx)
- `P12_PASSWORD` — the PKCS#12 password

See the example file `.env.example`. Do not commit real secrets.

---

## Testing

This repository contains both pure-Python tests and tests that require a running Frappe/ERPNext bench.

- To run pure-Python tests locally or in CI:
  
  ```sh
  pytest -m "not requires_bench"
  ```

- Tests that interact with Frappe/ERPNext are marked with `@pytest.mark.requires_bench` and should be executed inside a bench context.

Note: Frappe/ERPNext/HRMS are installed via Bench; they are not Python package dependencies in `requirements.txt`.

---

## Usage Examples

### Generating a RST Declaration Report

1. Navigate to the **Dominican Republic** module in ERPNext.
2. Select **RST Declaration Report** from the Payroll reports.
3. Choose the **employee** and **year**.
4. Export the report as a **PDF** for submission to DGII or employee records.

### Importing Customer's Paid ITBIS Withholding Data

1. Log in to the **DGII portal** and download your ITBIS withholding statement.
2. In ERPNext, go to the **ITBIS Withholding** doctype and click **Import**.
3. Upload the file using the **Data Import** tool and map the fields as prompted.
4. Save and Submit the imported records and reconcile the **Journal Entries** created.

### Selling Item Price Margins

1. Open the **Selling Item Price Margin** doctype.
2. Set up your preferred **Price List**, **Margin Type**, **Margin Amount** and **Items**
3. **Save** and **Submit** the newly created document.
4. The system automatically calculates the **margin percentage** for analysis on Purchase Receipt or Purchase Invoice submission.
