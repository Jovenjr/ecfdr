import unittest

from csf_do.csf_do.utils.ecf32_builder import build_ecf32_xml


class TestInputValidatorMessages(unittest.TestCase):
    def test_missing_tipo_pago_message(self):
        data = {
            "encabezado": {
                "Version": "1.0",
                "IdDoc": {
                    "TipoeCF": "32",
                    "eNCF": "E320000000300",
                    # Falta TipoPago
                    "TipoIngresos": "01",
                },
                "Emisor": {
                    "RNCEmisor": "101234567",
                    "RazonSocialEmisor": "EMPRESA SRL",
                    "DireccionEmisor": "Calle 1",
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
        with self.assertRaisesRegex(ValueError, "Falta el TipoPago"):
            build_ecf32_xml(data)


if __name__ == "__main__":
    unittest.main()


