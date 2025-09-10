import unittest

from csf_do.csf_do.utils.ecf32_builder import build_and_validate_ecf32


class TestECF32CDT(unittest.TestCase):
    def test_ecf32_with_cdt_additional_tax(self):
        data = {
            "encabezado": {
                "Version": "1.0",
                "IdDoc": {
                    "TipoeCF": "32",
                    "eNCF": "E320000000123",
                    "TipoIngresos": "01",
                    "TipoPago": "1",
                },
                "Emisor": {
                    "RNCEmisor": "101234567",
                    "RazonSocialEmisor": "EMPRESA TELECOM SRL",
                    "DireccionEmisor": "Av. Siempre Viva",
                    "FechaEmision": "2025-09-09",
                },
                "Comprador": {},
                "Totales": {"MontoTotal": "100.00"},
            },
            "detalles": {
                "items": [
                    {
                        "NumeroLinea": "1",
                        "IndicadorFacturacion": "1",
                        "NombreItem": "PLAN DE TELECOM",
                        "IndicadorBienoServicio": "2",
                        "CantidadItem": "1.00",
                        "PrecioUnitarioItem": "100.0000",
                        "MontoItem": "100.00",
                        "UnidadMedida": "43",
                        "TablaImpuestoAdicional": {
                            "ImpuestoAdicional": [
                                {
                                    "TipoImpuesto": "002",  # CDT
                                    "TasaImpuestoAdicional": "2.00",
                                }
                            ]
                        },
                    }
                ]
            },
            "fecha_hora_firma": "2025-09-09T12:00:00",
        }
        xml, ok, errores = build_and_validate_ecf32(data)
        self.assertTrue(ok, f"XML 32 con CDT debe validar. Errores: {errores}\nXML:\n{xml}")
        self.assertIn("<ImpuestosAdicionales>", xml)
        self.assertIn("<TipoImpuesto>002</TipoImpuesto>", xml)
        self.assertIn("<TasaImpuestoAdicional>2.00</TasaImpuestoAdicional>", xml)
        self.assertIn("<OtrosImpuestosAdicionales>2.00</OtrosImpuestosAdicionales>", xml)
        self.assertIn("<MontoImpuestoAdicional>2.00</MontoImpuestoAdicional>", xml)


if __name__ == "__main__":
    unittest.main()


