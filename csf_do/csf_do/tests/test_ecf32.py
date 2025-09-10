import unittest

from csf_do.csf_do.utils.ecf32_builder import build_and_validate_ecf32


class TestECF32Builder(unittest.TestCase):
    def test_valid_ecf32_minimal(self):
        data = {
            "encabezado": {
                "Version": "1.0",
                "IdDoc": {
                    "TipoeCF": "32",
                    "eNCF": "E320000000001",
                    "TipoIngresos": "01",
                    "TipoPago": "1",
                },
                "Emisor": {
                    "RNCEmisor": "101234567",
                    "RazonSocialEmisor": "MI EMPRESA SRL",
                    "DireccionEmisor": "Calle 1 #2",
                    "FechaEmision": "2025-09-09",
                },
                # En 32, la presencia de Comprador es requerida por spec, pero sin campos obligatorios
                "Comprador": {},
                "Totales": {"MontoTotal": "100.00"},
            },
            "detalles": {
                "items": [
                    {
                        "NumeroLinea": "1",
                        "IndicadorFacturacion": "1",
                        "NombreItem": "ITEM 32",
                        "IndicadorBienoServicio": "1",
                        "CantidadItem": "1.00",
                        "PrecioUnitarioItem": "100.0000",
                        "MontoItem": "100.00",
                    }
                ]
            },
            "fecha_hora_firma": "2025-09-09T12:00:00",
        }
        xml, ok, errores = build_and_validate_ecf32(data)
        self.assertTrue(ok, f"XML 32 debe validar contra XSD. Errores: {errores}\nXML:\n{xml}")

    def test_missing_required_field(self):
        data = {
            "encabezado": {
                "Version": "1.0",
                "IdDoc": {
                    # Falta TipoPago
                    "TipoeCF": "32",
                    "eNCF": "E320000000002",
                    "TipoIngresos": "01",
                },
                "Emisor": {
                    "RNCEmisor": "101234567",
                    "RazonSocialEmisor": "MI EMPRESA SRL",
                    "DireccionEmisor": "Calle 1 #2",
                    "FechaEmision": "2025-09-09",
                },
                "Comprador": {},
                "Totales": {"MontoTotal": "50.00"},
            },
            "detalles": {
                "items": [
                    {
                        "NumeroLinea": "1",
                        "IndicadorFacturacion": "1",
                        "NombreItem": "ITEM FAIL",
                        "IndicadorBienoServicio": "1",
                        "CantidadItem": "1.00",
                        "PrecioUnitarioItem": "50.0000",
                        "MontoItem": "50.00",
                    }
                ]
            },
            "fecha_hora_firma": "2025-09-09T12:00:00",
        }
        with self.assertRaises(ValueError):
            build_and_validate_ecf32(data)

    def test_consumidor_final_defaults_when_comprador_empty(self):
        data = {
            "encabezado": {
                "Version": "1.0",
                "IdDoc": {
                    "TipoeCF": "32",
                    "eNCF": "E320000000010",
                    "TipoIngresos": "01",
                    "TipoPago": "1",
                },
                "Emisor": {
                    "RNCEmisor": "101234567",
                    "RazonSocialEmisor": "MI EMPRESA SRL",
                    "DireccionEmisor": "Calle 1 #2",
                    "FechaEmision": "2025-09-09",
                },
                # Comprador vacío a propósito
                "Comprador": {},
                "Totales": {"MontoTotal": "100.00"},
            },
            "detalles": {
                "items": [
                    {
                        "NumeroLinea": "1",
                        "IndicadorFacturacion": "1",
                        "NombreItem": "ITEM 32",
                        "IndicadorBienoServicio": "1",
                        "CantidadItem": "1.00",
                        "PrecioUnitarioItem": "100.0000",
                        "MontoItem": "100.00",
                    }
                ]
            },
            "fecha_hora_firma": "2025-09-09T12:00:00",
        }
        xml, ok, errores = build_and_validate_ecf32(data)
        self.assertTrue(ok, f"XML 32 debe validar contra XSD. Errores: {errores}\nXML:\n{xml}")
        self.assertIn("<Comprador>", xml)
        self.assertIn("<RNCComprador>000000000</RNCComprador>", xml)
        self.assertIn("<RazonSocialComprador>CONSUMIDOR FINAL</RazonSocialComprador>", xml)


if __name__ == "__main__":
    unittest.main()
