import unittest

from csf_do.csf_do.utils.ecf47_builder import build_and_validate_ecf47


class TestECF47Builder(unittest.TestCase):
    def test_valid_ecf47_minimal(self):
        data = {
            "encabezado": {
                "Version": "1.0",
                "IdDoc": {
                    "TipoeCF": "47",
                    "eNCF": "E470000000001",
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
                        "NombreItem": "SERVICIO EXTERIOR",
                        "IndicadorBienoServicio": "2",
                        "CantidadItem": "1.00",
                        "PrecioUnitarioItem": "100.0000",
                        "MontoItem": "100.00",
                        "Retencion": {"IndicadorAgenteRetencionoPercepcion": "1", "MontoISRRetenido": "10.00"}
                    }
                ]
            },
            "fecha_hora_firma": "2025-09-09T12:00:00",
        }
        xml, ok, errores = build_and_validate_ecf47(data)
        self.assertTrue(ok, f"Debe validar XSD. Errores: {errores}\nXML:\n{xml}")


if __name__ == "__main__":
    unittest.main()


