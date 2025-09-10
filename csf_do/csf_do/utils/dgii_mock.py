"""
Cliente DGII Mock para pruebas locales (sin conexión).

Provee:
- recepcion_ecf(xml): devuelve track_id y estado inicial "Recibido".
- consulta_estado(track_id): simula progresión de estados.

Uso: Integrado por ecf_service cuando base_url inicia con "mock://".
"""
from __future__ import annotations
from typing import Dict
import time
import hashlib


class DGIIMock:
    def __init__(self, base_url: str = "mock://dgii") -> None:
        self.base_url = base_url

    def recepcion_ecf(self, xml: str) -> Dict:
        # Derivar un track_id desde el hash del XML + timestamp
        h = hashlib.sha256(xml.encode("utf-8")).hexdigest()[:16]
        tid = f"MOCK-{h}-{int(time.time())}"
        return {"track_id": tid, "estado": "Recibido"}

    def consulta_estado(self, track_id: str) -> Dict:
        # Simular: alternar entre En Proceso y Aceptado en función del tiempo/longitud
        if int(time.time()) % 2 == 0:
            return {"track_id": track_id, "estado": "En Proceso"}
        # 1 de cada 5 veces "Rechazado" con un mensaje
        if int(time.time()) % 5 == 0:
            return {"track_id": track_id, "estado": "Rechazado", "errores": ["Validación simulada no superada"]}
        return {"track_id": track_id, "estado": "Aceptado"}
