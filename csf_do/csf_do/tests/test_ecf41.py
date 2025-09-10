import unittest

from csf_do.csf_do.utils.ecf41_builder import build_and_validate_ecf41


class TestECF41Builder(unittest.TestCase):
    def test_valid_ecf41_minimal(self):
        data = {
            "encabezado": {
                "Version": "1.0",
                "IdDoc": {
                    "TipoeCF": "41",
                    "eNCF": "E410000000001",
                    "FechaVencimientoSecuencia": "2025-12-31",
                },
                "Emisor": {
                    "RNCEmisor": "101234567",
                    "RazonSocialEmisor": "MI EMPRESA SRL",
                    "DireccionEmisor": "Calle 1 #2",
                    "FechaEmision": "2025-09-09",
                },
                "Comprador": {
                    "RNCComprador": "101111111",
                    "RazonSocialComprador": "CLIENTE SRL",
                },
                "Totales": {"MontoTotal": "100.00"},
            },
            "detalles": {
                "items": [
                    {
                        "NumeroLinea": "1",
                        "IndicadorFacturacion": "1",
                        "Retencion": {"IndicadorAgenteRetencionoPercepcion": "1"},
                        "NombreItem": "ITEM A",
                        "IndicadorBienoServicio": "1",
                        "CantidadItem": "1.00",
                        "PrecioUnitarioItem": "100.0000",
                        "MontoItem": "100.00",
                    }
                ]
            },
            "fecha_hora_firma": "2025-09-09T12:00:00",
        }
        xml, ok, errores = build_and_validate_ecf41(data)
        self.assertTrue(ok, f"Debe validar XSD. Errores: {errores}\nXML:\n{xml}")

    def test_missing_retencion_indicator(self):
        data = {
            "encabezado": {
                "Version": "1.0",
                "IdDoc": {
                    "TipoeCF": "41",
                    "eNCF": "E410000000002",
                    "FechaVencimientoSecuencia": "2025-12-31",
                },
                "Emisor": {
                    "RNCEmisor": "101234567",
                    "RazonSocialEmisor": "MI EMPRESA SRL",
                    "DireccionEmisor": "Calle 1 #2",
                    "FechaEmision": "2025-09-09",
                },
                "Comprador": {
                    "RNCComprador": "101111111",
                    "RazonSocialComprador": "CLIENTE SRL",
                },
                "Totales": {"MontoTotal": "50.00"},
            },
            "detalles": {"items": [{
                "NumeroLinea": "1",
                "IndicadorFacturacion": "1",
                "NombreItem": "ITEM B",
                "IndicadorBienoServicio": "1",
                "CantidadItem": "1.00",
                "PrecioUnitarioItem": "50.0000",
                "MontoItem": "50.00",
            }]},
            "fecha_hora_firma": "2025-09-09T12:00:00",
        }
        with self.assertRaises(ValueError):
            build_and_validate_ecf41(data)


if __name__ == "__main__":
    unittest.main()


