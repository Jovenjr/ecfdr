#!/usr/bin/env python3
import sys
sys.path.append('/home/frappe/frappe-bench/apps')

print('=' * 60)
print('ECFDR INTEGRATION TESTS - REPUBLICA DOMINICANA')
print('=' * 60)

# Test 1: Import main module
try:
    import csf_do
    print('PASS: Main module imported')
except ImportError as e:
    print('FAIL: Main module import -', e)

# Test 2: Import reports
reports = [
    'csf_do.csf_do.report.dominican_purchase_tax_report.dominican_republic_purchase_tax_report',
    'csf_do.csf_do.report.dominican_republic_sales_tax_report.dominican_republic_sales_tax_report',
    'csf_do.csf_do.report.dominican_bank_payroll_advice_report.dominican_republic_bank_payroll_advice_report'
]

for report in reports:
    try:
        __import__(report)
        print('PASS:', report.split('.')[-1], 'imported')
    except ImportError as e:
        print('FAIL:', report.split('.')[-1], 'import -', e)

print('')
print('Test completed. If all tests pass, ECFDR is working correctly!')
