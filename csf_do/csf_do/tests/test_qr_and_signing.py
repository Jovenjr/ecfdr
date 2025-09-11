from __future__ import annotations

import unittest

from csf_do.csf_do.utils.signing import sign_xml
from csf_do.csf_do.utils.qr_code_generator import build_qr_payload_from_xml


class TestQRAndSigning(unittest.TestCase):
    def test_sign_and_qr_payload(self):
        xml = """
<ECF>
  <Encabezado>
    <IdDoc>
      <eNCF>E310000000001</eNCF>
    </IdDoc>
    <Emisor>
      <RNCEmisor>131415926</RNCEmisor>
      <FechaEmision>2025-09-10</FechaEmision>
    </Emisor>
    <Totales>
      <MontoTotal>100.00</MontoTotal>
    </Totales>
  </Encabezado>
</ECF>
""".strip()
        firma = sign_xml(xml, cert_path="", key_path="")
        self.assertTrue(firma.signed_xml)

        payload = build_qr_payload_from_xml(firma.signed_xml, codigo_seguridad=firma.codigo_seguridad or "ABC123")
        self.assertIn("eNCF=E310000000001", payload["texto"])  # basic presence


