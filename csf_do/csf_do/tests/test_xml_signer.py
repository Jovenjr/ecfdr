import unittest
import tempfile
import os

from csf_do.csf_do.utils.ecf43_builder import build_and_validate_ecf43

# Comprobar dependencias opcionales
try:
    from csf_do.csf_do.utils.xml_signer import sign_ecf_with_pkcs12, sign_with_pkcs12
    _HAS_SIGNER = True
except Exception:
    sign_ecf_with_pkcs12 = None  # type: ignore
    sign_with_pkcs12 = None  # type: ignore
    _HAS_SIGNER = False

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives.serialization.pkcs12 import serialize_key_and_certificates
    from cryptography.hazmat.primitives import hashes
    from cryptography.x509.oid import NameOID
    import cryptography.x509 as x509
    from datetime import datetime, timedelta
    _HAS_CRYPTO = True
    from lxml import etree
except Exception:
    _HAS_CRYPTO = False


@unittest.skipUnless(_HAS_SIGNER and _HAS_CRYPTO, "signxml/cryptography no disponibles")
class TestXMLSigner(unittest.TestCase):
    def _make_pkcs12(self, password: str) -> str:
        # Generar clave y certificado autofirmado
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, u"DO"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Test Org"),
            x509.NameAttribute(NameOID.COMMON_NAME, u"Test ECF Cert"),
        ])
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow() - timedelta(days=1))
            .not_valid_after(datetime.utcnow() + timedelta(days=365))
            .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
            .sign(private_key=key, algorithm=hashes.SHA256())
        )
        p12_bytes = serialize_key_and_certificates(
            name=b"test-ecf",
            key=key,
            cert=cert,
            cas=None,
            encryption_algorithm=serialization.BestAvailableEncryption(password.encode("utf-8")),
        )
        fd, path = tempfile.mkstemp(suffix=".p12")
        with os.fdopen(fd, "wb") as f:
            f.write(p12_bytes)
        return path

    def test_sign_ecf43_with_pkcs12(self):
        # Construir XML válido para e-CF 43
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
        xml, ok, errores = build_and_validate_ecf43(data)
        self.assertTrue(ok, f"XML base debe ser válido. Errores: {errores}")

        # Generar PKCS#12 temporal
        password = "pass1234"
        p12_path = self._make_pkcs12(password)
        try:
            res = sign_ecf_with_pkcs12(xml, p12_path=p12_path, password=password)
            self.assertIn("signed_xml", res)
            self.assertIn("signature_hash", res)
            self.assertIn("codigo_seguridad", res)
            self.assertEqual(len(res["codigo_seguridad"]), 6)
            self.assertEqual(len(res["signature_hash"]), 64)  # sha256 hex
            signed_xml = res["signed_xml"]
            # Comprobar que es XML bien formado y contiene firma
            root = etree.fromstring(signed_xml.encode("utf-8"))
            self.assertIsNotNone(root)
            # Buscar cualquier nodo Signature con cualquier namespace
            sig = root.find('.//{*}Signature')
            self.assertIsNotNone(sig, "El XML firmado debe contener un nodo Signature")
        finally:
            try:
                os.remove(p12_path)
            except Exception:
                pass

    def test_sign_specific_tag_semilla_with_pkcs12(self):
        # XML simple de semilla
        seed_xml = """
        <SemillaModel>
            <Semilla>PLACEHOLDER</Semilla>
        </SemillaModel>
        """.strip()

        password = "pass1234"
        p12_path = self._make_pkcs12(password)
        try:
            res = sign_with_pkcs12(seed_xml, p12_path=p12_path, password=password, target_tag='SemillaModel')
            self.assertIn("signed_xml", res)
            self.assertIn("signature_hash", res)
            self.assertIn("codigo_seguridad", res)
            self.assertEqual(len(res["codigo_seguridad"]), 6)
            # Validar que la firma está dentro de SemillaModel
            root = etree.fromstring(res["signed_xml"].encode("utf-8"))
            sig = root.find('.//{*}Signature')
            self.assertIsNotNone(sig)
        finally:
            try:
                os.remove(p12_path)
            except Exception:
                pass


if __name__ == "__main__":
    unittest.main()
