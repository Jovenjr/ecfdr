"""
Script de ejemplo para construir, validar y firmar un e-CF 43.
Uso:
  # Establece variables de entorno con la ruta y contraseña del PKCS#12
  # PowerShell:
  #   $env:P12_PATH = "C:/ruta/a/tu_certificado.p12"
  #   $env:P12_PASSWORD = "tu_password"
  # Ejecuta:
  #   python run_enviar_ecf.py

No imprime el XML completo por pantalla; solo los primeros caracteres.
"""
from __future__ import annotations
import os
from csf_do.csf_do.utils.ecf_service import enviar_ecf
from csf_do.csf_do.utils.cert_loader import get_active_certificate
from getpass import getpass


def main() -> None:
    p12_path = os.environ.get("P12_PATH")
    p12_password = os.environ.get("P12_PASSWORD")

    # Intentar cargar desde Doctype Digital Certificate si no hay P12_PATH
    if not p12_path:
        cert = get_active_certificate()
        if cert and cert.get("p12_path"):
            p12_path = cert["p12_path"]
            # Si el Doctype tiene password y no se pasó por env, úsalo
            if not p12_password and cert.get("password"):
                p12_password = cert["password"]

    if not p12_path:
        raise SystemExit("No se encontró P12_PATH. Define la variable de entorno o configura el Doctype 'Digital Certificate'.")

    # Solicitar contraseña si no está definida
    if not p12_password:
        p12_password = getpass("Contraseña del PKCS#12: ")

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
                }
            ]
        },
        "fecha_hora_firma": "2025-09-09T12:00:00",
    }

    res = enviar_ecf(
        data,
        tipo="43",
        base_url="https://stub.dgii",
        cert_path="",
        key_path="",
        p12_path=p12_path,
        p12_password=p12_password,
    )

    print("OK:", res.ok)
    print("Estado:", res.estado)
    print("TrackId (stub):", res.track_id)
    print("CodigoSeguridad:", res.firma.codigo_seguridad)
    print("XML firmado (primeros 400 chars):\n", res.firma.signed_xml[:400])


if __name__ == "__main__":
    main()
