# NCF Integration into ERPNext

## Overview

This integration enhances ERPNext by incorporating Dominican Republic's Tax Invoice Management System (NCF) requirements. It introduces new custom fields in the Sales Invoice Doctype, a new Doctype **(NCF HSCode)** for managing tax classification, and dynamic filtering for accurate tax mapping. Additionally, it integrates an external supplier’s <a href="https://docs.cecypo.tech/s/kb/doc/tims-parser-Nni9r8JcjX">Cecypo</a> NCF Parser for seamless invoice processing.

## Features

### 1. Custom Fields in Sales Invoice

To comply with NCF, the following fields have been added to the Sales Invoice Doctype:

| Field Name           | Type | Description                                   |
| :------------------- | :--- | :-------------------------------------------- |
| etr_serial_number    | Data | Unique NCF ETR serial number                 |
| cu_invoice_date      | Date | Invoice date recorded by NCF                 |
| etr_invoice_number   | Data | NCF-assigned invoice number                  |
| cu_link              | URL  | Verification link for the invoice             |

### 2. New Doctype: NCF HSCode

A new Doctype, `NCF HSCode`, has been introduced to store tax classification details.

**Key Fields:**

* **Item Tax**: Specifies the applicable tax template.
* **Description**: Provides additional details about the HS code.

### 3. Custom Fields in Item Tax Table

The following fields have been added to the Item Tax table:

| Field Name    | Type       | Description                                  |
| :------------ | :--------- | :------------------------------------------- |
| ncf_hscode   | Link       | Links to the NCF HSCode Doctype             |
| description   | Read Only  | Auto-fetches the HSCode description          |

### 4. Dynamic Filtering

To ensure accurate selection of HS codes, the `NCF HSCode` field in the Item Tax table is dynamically filtered based on the Item Tax Template.

**Filter Logic:**

Only HS codes that match the Item Tax Template of the current item are displayed.

## NCF Parser Integration

We are utilizing an external NCF Parser for processing and validating NCF invoices. This parser handles:

* Extraction of ETR serial numbers, invoice dates, and numbers from NCF.
* Verification and linking of NCF invoices via `cu_link`.
* Ensuring compliance with DGII requirements.

## Setup Instructions

1.  **Configure NCF HSCode**
    * Navigate to `NCF HSCode`.
    * Add new HS codes with their corresponding Item Tax Template.
    * Or update the already existing HSCodes with their corresponding 
2.  **Ensure Custom Fields in Sales Invoice**
    * Go to `Sales Invoice`.
    * Ensure the four NCF fields (`etr_serial_number`, `cu_invoice_date`, etc.) are visible in the Sales Invoice form.
3.  **Import HS Codes (Optional)**
    * Use ERPNext’s Data Import Tool to bulk upload HS codes.
4.  **Cecypo's External NCF Parser Integration**
    <a href="https://docs.cecypo.tech/s/kb/doc/erpnext-O7U5xeE9DN">Cecypo NCF Integration with ERPNext</a>

## Usage

### Generating a NCF-Compliant Invoice

1.  Create a Sales Invoice.
2.  Select the appropriate Item Tax Template.
3.  Ensure the NCF HSCode is populated for tax compliance.
4.  Upon submission, NCF details will be fetched and linked via the external parser.

### Verifying NCF Invoice

* Click on the `cu_link` to verify the invoice on the DGII portal.

## Benefits

* ✅ **Ensures DGII compliance** – Automates NCF invoice generation.
* ✅ **Enhances tax accuracy** – Uses HSCode mapping for proper tax classification.
* ✅ **Simplifies reconciliation** – NCF details are automatically linked to invoices.
* ✅ **Reduces manual effort** – External parser handles NCF invoice extraction.

## Support

For any issues or customizations, please contact the ERPNext support team or your NCF Parser provider.

## Future Enhancements

* Automated reconciliation of NCF data with ERPNext financials.
* Real-time tax rate updates based on HSCode changes.
* Enhanced error handling for NCF invoice validation.

This integration ensures seamless compliance with Dominican Republic’s NCF regulations while maintaining a smooth ERPNext workflow.
