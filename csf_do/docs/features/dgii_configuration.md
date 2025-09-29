# DGII Configuration

This guide explains how to configure DGII environments and the digital certificate to send and track e-CF documents from ERPNext.

## Prerequisites

- A working ERPNext site with the `csf_do` app installed.
- A valid PKCS#12 certificate file (`.p12` or `.pfx`) and its password.

## Digital Certificate Doctype

Fields typically used by the app:
- `is_active` or `active`: marks this certificate as the active one.
- `p12_path` (preferred) or `cert_path`/`file_path`: absolute path to the PKCS#12 file on the server.
- `password`: the PKCS#12 password (a Password field in Frappe).

Validation rules enforced in `csf_do/csf_do/doctype/digital_certificate/digital_certificate.py`:
- If active, a PKCS#12 path must be present.
- Only one active record is allowed at a time.

## DGII Configuration Doctype

Per-environment settings expected by utilities in `csf_do/csf_do/utils/`:
- `base_url` (string): target base URL.
- `verify_ssl` (bool): whether to validate TLS certificates.
- `ttl_token` (int): token TTL in seconds (if the API issues tokens).
- `overrides` (JSON/dict): optional extra values, e.g. `consulta_estado_url` to build the QR payload.

Example values:
- Sandbox/mock: `base_url = "mock://dgii"`, any credentials.
- Custom/test:  `base_url = "https://api.dgii.test"`, `verify_ssl = true`.
- Production:   `base_url = "https://api.dgii.gov.do"`, `verify_ssl = true`.

## Using the configuration from code

- Build, sign and send using configured environment:

```python
from csf_do.csf_do.utils.ecf_service import enviar_ecf_config

result = enviar_ecf_config(data, tipo="43", ambiente="custom")
print(result.ok, result.estado, result.track_id)
```

- Query status using configured environment:

```python
from csf_do.csf_do.utils.ecf_service import consultar_estado_config

status = consultar_estado_config(track_id, ambiente="custom")
print(status)
```

## Environment variables (optional, for local scripts)

For local development you may set:
- `P12_PATH`: absolute path to the PKCS#12 file.
- `P12_PASSWORD`: the password.

See `.env.example` and `run_enviar_ecf.py` for usage.
