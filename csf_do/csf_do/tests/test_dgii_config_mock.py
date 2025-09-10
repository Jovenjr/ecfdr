from __future__ import annotations

import types
import sys


def make_frappe_single(doc_fields: dict):
    class _Doc:
        pass

    d = _Doc()
    for k, v in doc_fields.items():
        setattr(d, k, v)

    fake = types.ModuleType("frappe")

    def get_single(name):  # type: ignore
        if name != "DGII Configuration":
            raise Exception("not found")
        return d

    fake.get_single = get_single  # type: ignore
    return fake


def test_get_active_dgii_config_normalizes_mock_precert(monkeypatch):
    from csf_do.csf_do.utils import dgii_config

    frappe = make_frappe_single({
        "precert_base_url": "mock",
        "verify_ssl": 1,
        "token_ttl_minutes": 60,
    })
    monkeypatch.setitem(sys.modules, 'frappe', frappe)

    cfg = dgii_config.get_active_dgii_config(ambiente="precert")
    assert cfg is not None
    assert cfg["base_url"] == "mock://precert"
    assert cfg["verify_ssl"] is True
    assert cfg["ttl_token"] == 3600


def test_get_active_dgii_config_prefers_minutes_over_seconds(monkeypatch):
    from csf_do.csf_do.utils import dgii_config

    frappe = make_frappe_single({
        "prod_base_url": "https://api",
        "verify_ssl": 0,
        "token_ttl_minutes": 2,
        "ttl_token": 9999,
    })
    monkeypatch.setitem(sys.modules, 'frappe', frappe)

    cfg = dgii_config.get_active_dgii_config(ambiente="prod")
    assert cfg is not None
    assert cfg["ttl_token"] == 120
    assert cfg["verify_ssl"] is False


