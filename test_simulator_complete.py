#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Prueba Completo del Simulador DGII
=============================================

Este script prueba todas las funcionalidades del simulador DGII:
1. Envío de e-CF
2. Consulta de estado
3. Acuse de recibo (ACECFAR)
4. Generación de e-CF de proveedor

Uso:
    python test_simulator_complete.py
"""

import sys
import os
import time
import json
from datetime import datetime

# Agregar el directorio de la aplicación al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'csf_do'))

try:
    import frappe
    from frappe.installer import make_conf
    FRAPPE_AVAILABLE = True
except ImportError:
    FRAPPE_AVAILABLE = False
    print("⚠️  Frappe no está instalado. Ejecutando en modo standalone...")


class SimulatorTester:
    """Clase para probar el simulador DGII"""
    
    def __init__(self):
        self.results = []
        self.track_ids = []
        
    def print_header(self, title):
        """Imprime un encabezado formateado"""
        print("\n" + "="*70)
        print(f"  {title}")
        print("="*70)
        
    def print_result(self, test_name, success, message, details=None):
        """Imprime el resultado de una prueba"""
        icon = "✅" if success else "❌"
        print(f"\n{icon} {test_name}")
        print(f"   Mensaje: {message}")
        if details:
            print(f"   Detalles: {json.dumps(details, indent=2, ensure_ascii=False)}")
        
        self.results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "details": details
        })
        
    def test_imports(self):
        """Prueba la importación de módulos"""
        self.print_header("PRUEBA 1: Importación de Módulos")
        
        try:
            if FRAPPE_AVAILABLE:
                from csf_do.csf_do.integrations.dgii_simulator import DGIISimulator
                from csf_do.csf_do.integrations.dgii_client import DGIIClient, get_dgii_client
                self.print_result(
                    "Importación de módulos",
                    True,
                    "Todos los módulos se importaron correctamente"
                )
                return True
            else:
                self.print_result(
                    "Importación de módulos",
                    False,
                    "Frappe no está disponible. Algunas funciones no estarán disponibles."
                )
                return False
        except Exception as e:
            self.print_result(
                "Importación de módulos",
                False,
                f"Error al importar: {str(e)}"
            )
            return False
    
    def test_simulator_envio(self):
        """Prueba el envío de e-CF simulado"""
        self.print_header("PRUEBA 2: Envío de e-CF Simulado")
        
        if not FRAPPE_AVAILABLE:
            self.print_result(
                "Envío de e-CF",
                False,
                "Requiere Frappe Framework"
            )
            return False
        
        try:
            from csf_do.csf_do.integrations.dgii_simulator import DGIISimulator
            
            simulator = DGIISimulator()
            
            # Simular envío
            xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<ECF xmlns="http://dgii.gov.do/ecf/v1.0">
    <Encabezado>
        <Version>1.0</Version>
        <IdDoc>
            <TipoeCF>31</TipoeCF>
            <eNCF>B0100000001</eNCF>
            <FechaEmision>2025-01-10</FechaEmision>
        </IdDoc>
    </Encabezado>
</ECF>"""
            
            result = simulator.enviar_ecf(xml_content, "31", "B0100000001")
            
            if result.get("success"):
                track_id = result.get("track_id")
                self.track_ids.append(track_id)
                self.print_result(
                    "Envío de e-CF",
                    True,
                    "e-CF enviado exitosamente",
                    {
                        "track_id": track_id,
                        "ncf": result.get("ncf"),
                        "fecha_recepcion": result.get("fecha_recepcion")
                    }
                )
                return True
            else:
                self.print_result(
                    "Envío de e-CF",
                    False,
                    result.get("mensaje", "Error desconocido"),
                    result
                )
                return False
                
        except Exception as e:
            self.print_result(
                "Envío de e-CF",
                False,
                f"Excepción: {str(e)}"
            )
            return False
    
    def test_consulta_estado(self):
        """Prueba la consulta de estado"""
        self.print_header("PRUEBA 3: Consulta de Estado")
        
        if not FRAPPE_AVAILABLE or not self.track_ids:
            self.print_result(
                "Consulta de estado",
                False,
                "Requiere track_id de prueba anterior"
            )
            return False
        
        try:
            from csf_do.csf_do.integrations.dgii_simulator import DGIISimulator
            
            simulator = DGIISimulator()
            track_id = self.track_ids[0]
            
            # Primera consulta (debería estar RECIBIDO)
            print("\n   📊 Consulta 1 (inmediata):")
            result1 = simulator.consultar_estado(track_id)
            print(f"      Estado: {result1.get('estado')}")
            print(f"      Mensaje: {result1.get('mensaje')}")
            
            # Esperar 12 segundos
            print("\n   ⏳ Esperando 12 segundos...")
            time.sleep(12)
            
            # Segunda consulta (debería estar EN_PROCESO)
            print("\n   📊 Consulta 2 (después de 12 seg):")
            result2 = simulator.consultar_estado(track_id)
            print(f"      Estado: {result2.get('estado')}")
            print(f"      Mensaje: {result2.get('mensaje')}")
            
            # Esperar 20 segundos más
            print("\n   ⏳ Esperando 20 segundos más...")
            time.sleep(20)
            
            # Tercera consulta (debería estar ACEPTADO o RECHAZADO)
            print("\n   📊 Consulta 3 (después de 32 seg total):")
            result3 = simulator.consultar_estado(track_id)
            print(f"      Estado: {result3.get('estado')}")
            print(f"      Mensaje: {result3.get('mensaje')}")
            
            if result3.get("success"):
                self.print_result(
                    "Consulta de estado con progresión temporal",
                    True,
                    f"Estado final: {result3.get('estado')}",
                    {
                        "estado_inicial": result1.get('estado'),
                        "estado_intermedio": result2.get('estado'),
                        "estado_final": result3.get('estado')
                    }
                )
                return True
            else:
                self.print_result(
                    "Consulta de estado",
                    False,
                    result3.get("mensaje", "Error desconocido"),
                    result3
                )
                return False
                
        except Exception as e:
            self.print_result(
                "Consulta de estado",
                False,
                f"Excepción: {str(e)}"
            )
            return False
    
    def test_generar_ecf_proveedor(self):
        """Prueba la generación de e-CF de proveedor"""
        self.print_header("PRUEBA 4: Generación de e-CF de Proveedor")
        
        if not FRAPPE_AVAILABLE:
            self.print_result(
                "Generación de e-CF proveedor",
                False,
                "Requiere Frappe Framework"
            )
            return False
        
        try:
            from csf_do.csf_do.integrations.dgii_simulator import DGIISimulator
            
            simulator = DGIISimulator()
            
            xml = simulator.generar_ecf_proveedor(
                supplier_rnc="131793916",
                amount=11800.00
            )
            
            # Verificar que el XML tiene la estructura básica
            has_ecf = "<ECF" in xml
            has_encabezado = "<Encabezado>" in xml
            has_rnc = "131793916" in xml
            has_amount = "11800" in xml
            
            if has_ecf and has_encabezado and has_rnc and has_amount:
                # Guardar XML para inspección
                output_file = "ecf_proveedor_simulado.xml"
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(xml)
                
                self.print_result(
                    "Generación de e-CF de proveedor",
                    True,
                    f"e-CF generado correctamente. Guardado en {output_file}",
                    {
                        "size": len(xml),
                        "supplier_rnc": "131793916",
                        "amount": 11800.00
                    }
                )
                return True
            else:
                self.print_result(
                    "Generación de e-CF de proveedor",
                    False,
                    "XML generado no tiene la estructura esperada"
                )
                return False
                
        except Exception as e:
            self.print_result(
                "Generación de e-CF proveedor",
                False,
                f"Excepción: {str(e)}"
            )
            return False
    
    def test_acuse_recibo(self):
        """Prueba el envío de acuse de recibo"""
        self.print_header("PRUEBA 5: Acuse de Recibo (ACECFAR)")
        
        if not FRAPPE_AVAILABLE or not self.track_ids:
            self.print_result(
                "Acuse de recibo",
                False,
                "Requiere track_id de prueba anterior"
            )
            return False
        
        try:
            from csf_do.csf_do.integrations.dgii_simulator import DGIISimulator
            
            simulator = DGIISimulator()
            track_id = self.track_ids[0]
            
            # Enviar acuse aceptado
            result = simulator.enviar_acuse_recibo(
                track_id=track_id,
                estado="ACEPTADO",
                motivo=""
            )
            
            if result.get("success"):
                self.print_result(
                    "Acuse de recibo",
                    True,
                    "Acuse enviado correctamente",
                    {
                        "track_id": track_id,
                        "estado_acuse": result.get("estado_acuse"),
                        "fecha_acuse": result.get("fecha_acuse")
                    }
                )
                return True
            else:
                self.print_result(
                    "Acuse de recibo",
                    False,
                    result.get("mensaje", "Error desconocido"),
                    result
                )
                return False
                
        except Exception as e:
            self.print_result(
                "Acuse de recibo",
                False,
                f"Excepción: {str(e)}"
            )
            return False
    
    def test_dgii_client(self):
        """Prueba el cliente unificado DGII"""
        self.print_header("PRUEBA 6: Cliente Unificado DGII")
        
        if not FRAPPE_AVAILABLE:
            self.print_result(
                "Cliente DGII",
                False,
                "Requiere Frappe Framework"
            )
            return False
        
        try:
            from csf_do.csf_do.integrations.dgii_client import get_dgii_client
            
            client = get_dgii_client()
            
            # Probar obtener info
            info = client.get_info()
            
            self.print_result(
                "Cliente DGII - Información",
                True,
                "Cliente DGII configurado correctamente",
                {
                    "modo": info.get("modo"),
                    "url_api": info.get("url_api"),
                    "simulador_activo": info.get("simulador_activo")
                }
            )
            
            # Probar test de conexión
            connection_result = client.test_connection()
            
            self.print_result(
                "Cliente DGII - Test de Conexión",
                connection_result.get("success", False),
                connection_result.get("mensaje", "Sin mensaje"),
                connection_result
            )
            
            return True
                
        except Exception as e:
            self.print_result(
                "Cliente DGII",
                False,
                f"Excepción: {str(e)}"
            )
            return False
    
    def print_summary(self):
        """Imprime el resumen final"""
        self.print_header("RESUMEN DE PRUEBAS")
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r["success"])
        failed = total - passed
        
        print(f"\n  Total de pruebas: {total}")
        print(f"  ✅ Exitosas: {passed}")
        print(f"  ❌ Fallidas: {failed}")
        print(f"  📊 Porcentaje éxito: {(passed/total*100):.1f}%")
        
        if failed > 0:
            print("\n  ⚠️  Pruebas fallidas:")
            for r in self.results:
                if not r["success"]:
                    print(f"     - {r['test']}: {r['message']}")
        
        print("\n" + "="*70)
        
        if passed == total:
            print("  🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
        else:
            print("  ⚠️  ALGUNAS PRUEBAS FALLARON")
        
        print("="*70 + "\n")
        
        return passed == total
    
    def run_all_tests(self):
        """Ejecuta todas las pruebas"""
        print("\n🚀 INICIANDO PRUEBAS DEL SIMULADOR DGII")
        print(f"   Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Ejecutar pruebas en orden
        self.test_imports()
        
        if FRAPPE_AVAILABLE:
            self.test_simulator_envio()
            self.test_consulta_estado()
            self.test_generar_ecf_proveedor()
            self.test_acuse_recibo()
            self.test_dgii_client()
        else:
            print("\n⚠️  La mayoría de pruebas requieren Frappe Framework.")
            print("   Por favor, ejecute este script dentro del contexto de Frappe/ERPNext.")
        
        # Imprimir resumen
        success = self.print_summary()
        
        return 0 if success else 1


def main():
    """Función principal"""
    tester = SimulatorTester()
    return tester.run_all_tests()


if __name__ == "__main__":
    sys.exit(main())
