from __future__ import annotations

from csf_do.csf_do.utils.dgii_client import DGIIClient, DGIIEnv


def test_endpoints_defaults_without_overrides():
    env = DGIIEnv(name="precert", base_url="https://api.dgii")
    client = DGIIClient(env)
    eps = client.endpoints()
    assert eps["semilla"].startswith("https://api.dgii/")
    assert "/auth/semilla" in eps["semilla"]
    assert "/auth/token" in eps["token"]
    assert "/recepcion/ecf" in eps["recepcion_ecf"]


def test_endpoints_apply_overrides(monkeypatch):
    from csf_do.csf_do.utils import dgii_config

    def fake_get_active_dgii_config(ambiente: str = "custom"):
        return {
            "base_url": "https://api.dgii",
            "verify_ssl": True,
            "ttl_token": 3600,
            "overrides": {
                "auth_semilla_url": "https://auth.semilla",
                "auth_token_url": "https://auth.token",
                "recepcion_ecf_url": "https://rx.ecf",
                "consulta_estado_url": "https://consulta.estado",
                "directorio_servicios_url": "https://dir.servicios",
            },
        }

    monkeypatch.setattr(dgii_config, "get_active_dgii_config", fake_get_active_dgii_config)

    env = DGIIEnv(name="precert", base_url="https://api.dgii")
    client = DGIIClient(env)
    eps = client.endpoints()
    assert eps["semilla"] == "https://auth.semilla"
    assert eps["token"] == "https://auth.token"
    assert eps["recepcion_ecf"] == "https://rx.ecf"
    assert eps["consulta_estado"] == "https://consulta.estado"
    assert eps["directorio_servicios"] == "https://dir.servicios"


