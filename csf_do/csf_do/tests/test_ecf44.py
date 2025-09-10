import unittest

from csf_do.csf_do.utils.ecf44_builder import build_and_validate_ecf44


class TestECF44Builder(unittest.TestCase):
    def test_valid_ecf44_minimal(self):
        data = {
            "encabezado": {
                "Version": "1.0",
                "IdDoc": {
                    "TipoeCF": "44",
                    "eNCF": "E440000000001",
                    "FechaVencimientoSecuencia": "2025-12-31",
                    "TipoIngresos": "01",
                    "TipoPago": "1",
                },
                "Emisor": {
                    "RNCEmisor": "101234567",
                    "RazonSocialEmisor": "MI EMPRESA SRL",
                    "DireccionEmisor": "Calle 1 #2",
                    "FechaEmision": "2025-09-09",
                },
                "Comprador": {
                    "RazonSocialComprador": "CLIENTE SRL",
                },
                "Totales": {"MontoTotal": "100.00"},
            },
            "detalles": {
                "items": [
                    {
                        "NumeroLinea": "1",
                        "IndicadorFacturacion": "1",
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
        xml, ok, errores = build_and_validate_ecf44(data)
        self.assertTrue(ok, f"Debe validar XSD. Errores: {errores}\nXML:\n{xml}")


if __name__ == "__main__":
    unittest.main()


