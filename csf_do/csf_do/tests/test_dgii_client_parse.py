from __future__ import annotations

from types import SimpleNamespace

from csf_do.csf_do.utils.dgii_client import DGIIClient, DGIIEnv


class FakeResp:
    def __init__(self, text: str, content_type: str = "application/json", status: int = 200, json_obj=None):
        self.text = text
        self.status_code = status
        self._json = json_obj
        self.headers = {"Content-Type": content_type}

    def raise_for_status(self):
        if not (200 <= self.status_code < 300):
            raise RuntimeError("http error")

    def json(self):
        if self._json is None:
            raise ValueError("no json")
        return self._json


def test_post_xml_parses_json_track_id(monkeypatch):
    env = DGIIEnv(name="precert", base_url="https://api")
    client = DGIIClient(env)

    def fake_post(url, data, headers, timeout, verify):  # type: ignore
        return FakeResp("{}", json_obj={"track_id": "ABC123", "estado": "Recibido"})

    import csf_do.csf_do.utils.dgii_client as mod
    monkeypatch.setattr(mod, "requests", SimpleNamespace(post=fake_post))

    out = client.post_xml("recepcion_ecf", "<xml/>", cert_path="", key_path="")
    assert out["track_id"] == "ABC123"
    assert out.get("estado") == "Recibido"


def test_post_xml_parses_xml_track_id(monkeypatch):
    env = DGIIEnv(name="precert", base_url="https://api")
    client = DGIIClient(env)

    xml_body = """
    <Respuesta>
      <TrackId>ZXCV-999</TrackId>
      <Estado>Recibido</Estado>
    </Respuesta>
    """.strip()

    def fake_post(url, data, headers, timeout, verify):  # type: ignore
        return FakeResp(xml_body, content_type="application/xml")

    import csf_do.csf_do.utils.dgii_client as mod
    monkeypatch.setattr(mod, "requests", SimpleNamespace(post=fake_post))

    out = client.post_xml("recepcion_ecf", "<xml/>", cert_path="", key_path="")
    assert out["track_id"] == "ZXCV-999"
    assert out.get("estado") == "Recibido"


def test_status_track_id_parses_json(monkeypatch):
    env = DGIIEnv(name="precert", base_url="https://api")
    client = DGIIClient(env)

    def fake_get(url, headers, timeout, verify):  # type: ignore
        return FakeResp("{}", json_obj={"estado": "Aceptado", "codigo": "0"})

    import csf_do.csf_do.utils.dgii_client as mod
    monkeypatch.setattr(mod, "requests", SimpleNamespace(get=fake_get))

    out = client.status_track_id("T1")
    assert out.get("estado") == "Aceptado"
    assert out.get("codigo") == "0"


def test_status_track_id_parses_xml(monkeypatch):
    env = DGIIEnv(name="precert", base_url="https://api")
    client = DGIIClient(env)

    xml_body = """
    <Respuesta>
      <Estado>Rechazado</Estado>
      <Codigo>104</Codigo>
    </Respuesta>
    """.strip()

    def fake_get(url, headers, timeout, verify):  # type: ignore
        return FakeResp(xml_body, content_type="text/xml")

    import csf_do.csf_do.utils.dgii_client as mod
    monkeypatch.setattr(mod, "requests", SimpleNamespace(get=fake_get))

    out = client.status_track_id("T2")
    assert out.get("estado") == "Rechazado"
    assert out.get("codigo") == "104"


