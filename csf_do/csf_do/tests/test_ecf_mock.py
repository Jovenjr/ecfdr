import unittest

from csf_do.csf_do.utils.ecf43_builder import build_and_validate_ecf43
from csf_do.csf_do.utils.ecf_service import enviar_ecf


class TestECFMockFlow(unittest.TestCase):
    def test_send_ecf43_to_mock(self):
        data = {
            "encabezado": {
                "Version": "1.0",
                "IdDoc": {
                    "TipoeCF": "43",
                    "eNCF": "E310000000001",
                    "FechaVencimientoSecuencia": "2025-12-31",
                },
                "Emisor": {
                    "RNCEmisor": "101234567",
                    "RazonSocialEmisor": "MI EMPRESA SRL",
                    "DireccionEmisor": "Calle 1 #2",
                    "FechaEmision": "2025-09-09",
                },
                "Totales": {"MontoTotal": "100.00"},
            },
            "detalles": {
                "items": [
                    {
                        "NumeroLinea": "1",
                        "IndicadorFacturacion": "1",
                        "NombreItem": "ITEM MOCK",
                        "IndicadorBienoServicio": "1",
                        "CantidadItem": "1.00",
                        "PrecioUnitarioItem": "100.0000",
                        "MontoItem": "100.00",
                    }
                ]
            },
            "fecha_hora_firma": "2025-09-09T12:00:00",
        }
        xml, ok, errores = build_and_validate_ecf43(data)
        self.assertTrue(ok, f"XML debe validar contra XSD. Errores: {errores}")

        # Enviar a mock (firma placeholder porque no pasamos p12)
        res = enviar_ecf(
            data,
            tipo="43",
            base_url="mock://dgii",
            cert_path="",
            key_path="",
        )
        self.assertTrue(res.ok)
        self.assertEqual(res.estado, "Enviado")
        self.assertIsNotNone(res.track_id)
        self.assertIn("<ECF>", res.xml)


if __name__ == "__main__":
    unittest.main()
