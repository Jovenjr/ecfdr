"""
Script de prueba completa de instalación de csf_do
Ejecutar desde dentro del contenedor Docker
"""

import frappe
import json
from frappe.utils import nowdate, now

def test_doctypes_exist():
    """Verifica que todos los DocTypes existen"""
    print("=" * 60)
    print("VERIFICANDO DOCTYPES...")
    print("=" * 60)
    
    doctypes = [
        "DGII Configuration",
        "DGII Simulator Config",
        "Digital Certificate",
        "e-CF",
        "eCF Recibido",
        "e-CF Sequence",
        "e-CF Audit Log"
    ]
    
    for doctype in doctypes:
        try:
            frappe.get_meta(doctype)
            print(f"✓ {doctype} - OK")
        except Exception as e:
            print(f"✗ {doctype} - ERROR: {str(e)}")
            return False
    
    return True

def test_dgii_configuration():
    """Prueba crear y configurar DGII Configuration"""
    print("\n" + "=" * 60)
    print("CONFIGURANDO DGII CONFIGURATION...")
    print("=" * 60)
    
    try:
        # Buscar si ya existe
        existing = frappe.db.exists("DGII Configuration", "DGII Configuration")
        
        if existing:
            doc = frappe.get_doc("DGII Configuration", "DGII Configuration")
            print("✓ DGII Configuration ya existe")
        else:
            doc = frappe.get_doc({
                "doctype": "DGII Configuration",
                "api_mode": "simulator",
                "rnc": "123456789",
                "company_name": "Empresa de Prueba SRL",
                "tax_id_name": "RNC"
            })
            doc.insert()
            print("✓ DGII Configuration creada")
        
        # Actualizar a modo simulador
        doc.api_mode = "simulator"
        doc.save()
        frappe.db.commit()
        
        print(f"  - Modo API: {doc.api_mode}")
        print(f"  - RNC: {doc.rnc}")
        print(f"  - Empresa: {doc.company_name}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "Test DGII Configuration")
        return False

def test_dgii_simulator_config():
    """Prueba crear configuración del simulador"""
    print("\n" + "=" * 60)
    print("CONFIGURANDO DGII SIMULATOR...")
    print("=" * 60)
    
    try:
        existing = frappe.db.exists("DGII Simulator Config", "DGII Simulator Config")
        
        if existing:
            doc = frappe.get_doc("DGII Simulator Config", "DGII Simulator Config")
            print("✓ DGII Simulator Config ya existe")
        else:
            doc = frappe.get_doc({
                "doctype": "DGII Simulator Config",
                "enabled": 1,
                "simulate_delays": 0,
                "success_rate": 100,
                "default_response_time": 1
            })
            doc.insert()
            print("✓ DGII Simulator Config creada")
        
        doc.enabled = 1
        doc.success_rate = 100
        doc.save()
        frappe.db.commit()
        
        print(f"  - Habilitado: {doc.enabled}")
        print(f"  - Tasa éxito: {doc.success_rate}%")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "Test DGII Simulator Config")
        return False

def test_dgii_client():
    """Prueba el cliente DGII"""
    print("\n" + "=" * 60)
    print("PROBANDO CLIENTE DGII...")
    print("=" * 60)
    
    try:
        from csf_do.csf_do.integrations.dgii_client import get_dgii_client
        
        client = get_dgii_client()
        print(f"✓ Cliente obtenido: {client.__class__.__name__}")
        print(f"  - Tipo: {'Simulador' if 'Simulator' in client.__class__.__name__ else 'Real'}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "Test DGII Client")
        return False

def test_simulator_enviar_ecf():
    """Prueba enviar un e-CF al simulador"""
    print("\n" + "=" * 60)
    print("PROBANDO ENVÍO DE e-CF AL SIMULADOR...")
    print("=" * 60)
    
    try:
        from csf_do.csf_do.integrations.dgii_simulator import enviar_ecf
        
        # XML de prueba simplificado
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<ECF xmlns="http://dgii.gov.do/ecf/v1.0">
    <Encabezado>
        <RNCEmisor>123456789</RNCEmisor>
        <RNCComprador>987654321</RNCComprador>
        <TipoECF>31</TipoECF>
        <eNCF>E310000000001</eNCF>
        <FechaEmision>2024-01-10</FechaEmision>
    </Encabezado>
    <Totales>
        <MontoTotal>1000.00</MontoTotal>
    </Totales>
</ECF>"""
        
        result = enviar_ecf(xml_content)
        
        print(f"✓ Respuesta del simulador:")
        print(f"  - Track ID: {result.get('track_id')}")
        print(f"  - Estado: {result.get('estado')}")
        print(f"  - Mensaje: {result.get('mensaje')}")
        print(f"  - Código resultado: {result.get('codigo_resultado')}")
        
        return result.get('estado') == 'ACEPTADO'
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "Test Simulator Enviar ECF")
        return False

def test_simulator_consultar_estado():
    """Prueba consultar estado de un e-CF"""
    print("\n" + "=" * 60)
    print("PROBANDO CONSULTA DE ESTADO...")
    print("=" * 60)
    
    try:
        from csf_do.csf_do.integrations.dgii_simulator import consultar_estado
        
        track_id = "SIM-2024-00001"
        result = consultar_estado(track_id)
        
        print(f"✓ Respuesta del simulador:")
        print(f"  - Track ID: {result.get('track_id')}")
        print(f"  - Estado: {result.get('estado')}")
        print(f"  - Mensaje: {result.get('mensaje')}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "Test Simulator Consultar Estado")
        return False

def main():
    """Ejecuta todas las pruebas"""
    print("\n")
    print("*" * 60)
    print("  PRUEBA DE INSTALACIÓN COMPLETA - CSF_DO")
    print("*" * 60)
    print("\n")
    
    results = []
    
    # Test 1: DocTypes existen
    results.append(("DocTypes existen", test_doctypes_exist()))
    
    # Test 2: DGII Configuration
    results.append(("DGII Configuration", test_dgii_configuration()))
    
    # Test 3: DGII Simulator Config
    results.append(("DGII Simulator Config", test_dgii_simulator_config()))
    
    # Test 4: Cliente DGII
    results.append(("Cliente DGII", test_dgii_client()))
    
    # Test 5: Enviar e-CF
    results.append(("Enviar e-CF", test_simulator_enviar_ecf()))
    
    # Test 6: Consultar estado
    results.append(("Consultar estado", test_simulator_consultar_estado()))
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
    
    print("\n" + "=" * 60)
    print(f"RESULTADO: {passed}/{total} pruebas pasadas")
    
    if passed == total:
        print("🎉 ¡INSTALACIÓN COMPLETA Y FUNCIONAL!")
    else:
        print("⚠️  Algunas pruebas fallaron, revisar errores")
    
    print("=" * 60)

if __name__ == "__main__":
    frappe.init(site="localhost")
    frappe.connect()
    
    try:
        main()
    except Exception as e:
        print(f"\n✗ Error fatal: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "Test Installation")
    finally:
        frappe.destroy()
