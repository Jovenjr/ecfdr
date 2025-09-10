from __future__ import annotations

from csf_do.csf_do.utils.qr_code_generator import build_qr_payload_from_xml


MIN_XML = """
<ECF>
  <Encabezado>
    <IdDoc>
      <eNCF>E3100000001</eNCF>
    </IdDoc>
    <Emisor>
      <RNCEmisor>123456789</RNCEmisor>
      <FechaEmision>10-09-2025</FechaEmision>
    </Emisor>
    <Totales>
      <MontoTotal>1000.00</MontoTotal>
    </Totales>
  </Encabezado>
</ECF>
""".strip()


def test_build_qr_payload_from_xml_min():
    payload = build_qr_payload_from_xml(MIN_XML, "ABCDEF")
    assert "RNC=123456789" in payload["texto"]
    assert "eNCF=E3100000001" in payload["texto"]
    assert "FechaEmision=10-09-2025" in payload["texto"]
    assert "MontoTotal=1000.00" in payload["texto"]
    assert "CodigoSeguridad=ABCDEF" in payload["texto"]


def test_build_qr_payload_with_url():
    payload = build_qr_payload_from_xml(MIN_XML, "ABCDEF", consulta_base_url="https://consulta.dgii")
    assert payload["url"].startswith("https://consulta.dgii?")
    assert "rnc=123456789" in payload["url"]
    assert "encf=E3100000001" in payload["url"]
    assert "cs=ABCDEF" in payload["url"]


