import unittest

from csf_do.csf_do.utils.ecf34_builder import build_and_validate_ecf34


class TestECF34Builder(unittest.TestCase):
    def test_valid_ecf34_minimal(self):
        data = {
            "encabezado": {
                "Version": "1.0",
                "IdDoc": {
                    "TipoeCF": "34",
                    "eNCF": "E340000000001",
                    "IndicadorNotaCredito": "1",
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
            "InformacionReferencia": {
                "NCFModificado": "E310000000001",
                "FechaNCFModificado": "2025-09-01",
                "CodigoModificacion": "3",
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
        xml, ok, errores = build_and_validate_ecf34(data)
        self.assertTrue(ok, f"Debe validar XSD. Errores: {errores}\nXML:\n{xml}")


if __name__ == "__main__":
    unittest.main()


