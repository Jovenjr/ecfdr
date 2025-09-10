import unittest

from csf_do.csf_do.utils.ecf43_builder import build_and_validate_ecf43


class TestECF43Builder(unittest.TestCase):
    def test_valid_ecf43_minimal(self):
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
                        "NombreItem": "LAPIZ HB",
                        "IndicadorBienoServicio": "1",
                        "CantidadItem": "1.00",
                        "PrecioUnitarioItem": "100.0000",
                        "MontoItem": "100.00",
                        # "UnidadMedida": "43",  # opcional (UND)
                    }
                ]
            },
            "fecha_hora_firma": "2025-09-09T12:00:00",
        }

        xml, ok, errores = build_and_validate_ecf43(data)
        self.assertTrue(ok, f"Debe validar XSD. Errores: {errores}\nXML:\n{xml}")

    def test_invalid_unidad_medida_catalog(self):
        data = {
            "encabezado": {
                "Version": "1.0",
                "IdDoc": {
                    "TipoeCF": "43",
                    "eNCF": "E310000000002",
                    "FechaVencimientoSecuencia": "2025-12-31",
                },
                "Emisor": {
                    "RNCEmisor": "101234567",
                    "RazonSocialEmisor": "MI EMPRESA SRL",
                    "DireccionEmisor": "Calle 1 #2",
                    "FechaEmision": "2025-09-09",
                },
                "Totales": {"MontoTotal": "50.00"},
            },
            "detalles": {
                "items": [
                    {
                        "NumeroLinea": "1",
                        "IndicadorFacturacion": "1",
                        "NombreItem": "REGLA 30cm",
                        "IndicadorBienoServicio": "1",
                        "CantidadItem": "1.00",
                        "PrecioUnitarioItem": "50.0000",
                        "MontoItem": "50.00",
                        "UnidadMedida": "999",  # valor inválido (no existe en catálogo)
                    }
                ]
            },
            "fecha_hora_firma": "2025-09-09T12:00:00",
        }

        with self.assertRaises(ValueError):
            build_and_validate_ecf43(data)

    def test_missing_required_field(self):
        # Falta MontoTotal en Totales (requerido)
        data = {
            "encabezado": {
                "Version": "1.0",
                "IdDoc": {
                    "TipoeCF": "43",
                    "eNCF": "E310000000003",
                    "FechaVencimientoSecuencia": "2025-12-31",
                },
                "Emisor": {
                    "RNCEmisor": "101234567",
                    "RazonSocialEmisor": "MI EMPRESA SRL",
                    "DireccionEmisor": "Calle 1 #2",
                    "FechaEmision": "2025-09-09",
                },
                "Totales": {},  # MontoTotal requerido
            },
            "detalles": {
                "items": [
                    {
                        "NumeroLinea": "1",
                        "IndicadorFacturacion": "1",
                        "NombreItem": "BORRADOR",
                        "IndicadorBienoServicio": "1",
                        "CantidadItem": "1.00",
                        "PrecioUnitarioItem": "20.0000",
                        "MontoItem": "20.00",
                    }
                ]
            },
            "fecha_hora_firma": "2025-09-09T12:00:00",
        }

        with self.assertRaises(ValueError):
            build_and_validate_ecf43(data)


if __name__ == "__main__":
    unittest.main()
