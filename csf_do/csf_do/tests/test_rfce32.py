import unittest

from csf_do.csf_do.utils.rfce32_builder import build_and_validate_rfce32


class TestRFCE32Builder(unittest.TestCase):
    def test_valid_rfce32_minimal(self):
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
                    "FechaEmision": "2025-09-09",
                },
                "Totales": {"MontoTotal": "100.00"},
            },
            "CodigoSeguridadeCF": "ABCDEF",
        }
        xml, ok, errores = build_and_validate_rfce32(data)
        self.assertTrue(ok, f"Debe validar XSD. Errores: {errores}\nXML:\n{xml}")


if __name__ == "__main__":
    unittest.main()


