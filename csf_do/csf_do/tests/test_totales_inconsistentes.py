import unittest

from csf_do.csf_do.utils.ecf43_builder import build_ecf43_xml
from csf_do.csf_do.utils.ecf31_builder import build_ecf31_xml


class TestTotalesInconsistentes(unittest.TestCase):
    def test_totales_inconsistentes_ecf43(self):
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
                        "NombreItem": "ITEM X",
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
            build_ecf43_xml(data)

    def test_totales_inconsistentes_ecf31(self):
        data = {
            "encabezado": {
                "Version": "1.0",
                "IdDoc": {
                    "TipoeCF": "31",
                    "eNCF": "E310000000002",
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
                    "RNCComprador": "101111111",
                    "RazonSocialComprador": "CLIENTE SRL",
                },
                "Totales": {"MontoTotal": "200.00"},
            },
            "detalles": {
                "items": [
                    {
                        "NumeroLinea": "1",
                        "IndicadorFacturacion": "1",
                        "NombreItem": "ITEM Y",
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
            build_ecf31_xml(data)

    def test_totales_otra_moneda_inconsistentes_ecf43(self):
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
                "Totales": {"MontoTotal": "100.00"},
                "OtraMoneda": {"TipoMoneda": "USD", "MontoTotalOtraMoneda": "200.00"},
            },
            "detalles": {
                "items": [
                    {
                        "NumeroLinea": "1",
                        "IndicadorFacturacion": "1",
                        "NombreItem": "ITEM OM",
                        "IndicadorBienoServicio": "1",
                        "CantidadItem": "1.00",
                        "PrecioUnitarioItem": "100.0000",
                        "MontoItem": "100.00",
                        "OtraMonedaDetalle": {"MontoItemOtraMoneda": "120.00"},
                    }
                ]
            },
            "fecha_hora_firma": "2025-09-09T12:00:00",
        }
        with self.assertRaises(ValueError):
            build_ecf43_xml(data)

    def test_totales_otra_moneda_inconsistentes_ecf31(self):
        data = {
            "encabezado": {
                "Version": "1.0",
                "IdDoc": {
                    "TipoeCF": "31",
                    "eNCF": "E310000000004",
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
                    "RNCComprador": "101111111",
                    "RazonSocialComprador": "CLIENTE SRL",
                },
                "Totales": {"MontoTotal": "100.00"},
                "OtraMoneda": {"TipoMoneda": "USD", "MontoTotalOtraMoneda": "300.00"},
            },
            "detalles": {
                "items": [
                    {
                        "NumeroLinea": "1",
                        "IndicadorFacturacion": "1",
                        "NombreItem": "ITEM OM31",
                        "IndicadorBienoServicio": "1",
                        "CantidadItem": "1.00",
                        "PrecioUnitarioItem": "100.0000",
                        "MontoItem": "100.00",
                        "OtraMonedaDetalle": {"MontoItemOtraMoneda": "120.00"},
                    }
                ]
            },
            "fecha_hora_firma": "2025-09-09T12:00:00",
        }
        with self.assertRaises(ValueError):
            build_ecf31_xml(data)


if __name__ == "__main__":
    unittest.main()
