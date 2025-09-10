import unittest

from csf_do.csf_do.utils.ecf32_builder import build_and_validate_ecf32
from csf_do.csf_do.utils.ecf44_builder import build_and_validate_ecf44


class TestBusinessRulesITBIS(unittest.TestCase):
    def test_ecf32_gravado_i1_ok(self):
        data = {
            "encabezado": {
                "Version": "1.0",
                "IdDoc": {
                    "TipoeCF": "32",
                    "eNCF": "E320000000200",
                    "TipoIngresos": "01",
                    "TipoPago": "1",
                },
                "Emisor": {
                    "RNCEmisor": "101234567",
                    "RazonSocialEmisor": "EMPRESA SRL",
                    "DireccionEmisor": "Calle 1",
                    "FechaEmision": "2025-09-09",
                },
                "Comprador": {},
                "Totales": {
                    "MontoGravadoI1": "100.00",
                    "MontoExento": "0.00",
                    "MontoTotal": "100.00",
                },
            },
            "detalles": {
                "items": [
                    {
                        "NumeroLinea": "1",
                        "IndicadorFacturacion": "1",
                        "NombreItem": "ITEM",
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
        self.assertTrue(ok, f"Debe validar XSD. Errores: {errores}\nXML:\n{xml}")

    def test_ecf44_exento_ok(self):
        data = {
            "encabezado": {
                "Version": "1.0",
                "IdDoc": {
                    "TipoeCF": "44",
                    "eNCF": "E440000000200",
                    "FechaVencimientoSecuencia": "2025-12-31",
                    "TipoIngresos": "01",
                    "TipoPago": "1",
                },
                "Emisor": {
                    "RNCEmisor": "101234567",
                    "RazonSocialEmisor": "EMPRESA SRL",
                    "DireccionEmisor": "Calle 1",
                    "FechaEmision": "2025-09-09",
                },
                "Comprador": {"RazonSocialComprador": "CLIENTE"},
                "Totales": {
                    "MontoExento": "100.00",
                    "MontoTotal": "100.00",
                },
            },
            "detalles": {
                "items": [
                    {
                        "NumeroLinea": "1",
                        "IndicadorFacturacion": "0",
                        "NombreItem": "ITEM",
                        "IndicadorBienoServicio": "1",
                        "CantidadItem": "1.00",
                        "PrecioUnitarioItem": "100.0000",
                        "MontoItem": "100.00",
                    }
                ]
            },
            "fecha_hora_firma": "2025-09-09T12:00:00",
        }
        xml, ok, errores = build_and_validate_ecf44(data)
        self.assertTrue(ok, f"Debe validar XSD. Errores: {errores}\nXML:\n{xml}")

    def test_ecf32_gravado_i1_mismatch_ko(self):
        data = {
            "encabezado": {
                "Version": "1.0",
                "IdDoc": {
                    "TipoeCF": "32",
                    "eNCF": "E320000000201",
                    "TipoIngresos": "01",
                    "TipoPago": "1",
                },
                "Emisor": {
                    "RNCEmisor": "101234567",
                    "RazonSocialEmisor": "EMPRESA SRL",
                    "DireccionEmisor": "Calle 1",
                    "FechaEmision": "2025-09-09",
                },
                "Comprador": {},
                "Totales": {
                    "MontoGravadoI1": "120.00",  # mismatch
                    "MontoTotal": "100.00",
                },
            },
            "detalles": {
                "items": [
                    {
                        "NumeroLinea": "1",
                        "IndicadorFacturacion": "1",
                        "NombreItem": "ITEM",
                        "IndicadorBienoServicio": "1",
                        "CantidadItem": "1.00",
                        "PrecioUnitarioItem": "100.0000",
                        "MontoItem": "100.00",
                    }
                ]
            },
            "fecha_hora_firma": "2025-09-09T12:00:00",
        }
        with self.assertRaises(ValueError):
            build_and_validate_ecf32(data)


if __name__ == "__main__":
    unittest.main()


