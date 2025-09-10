from base64 import b64encode
from io import BytesIO
from typing import Optional, Dict

import qrcode
from xml.etree import ElementTree as ET


def get_qr_code(data: str) -> str:
	qr_code_bytes = get_qr_code_bytes(data, format="PNG")
	base_64_string = bytes_to_base64_string(qr_code_bytes)

	return add_file_info(base_64_string)


def add_file_info(data: str) -> str:
	"""Add info about the file type and encoding.
	
	This is required so the browser can make sense of the data."""
	return f"data:image/png;base64, {data}"


def get_qr_code_bytes(data, format: str) -> bytes:
	"""Create a QR code and return the bytes."""
	img = qrcode.make(data)

	buffered = BytesIO()
	img.save(buffered, format=format)

	return buffered.getvalue()


def bytes_to_base64_string(data: bytes) -> str:
	"""Convert bytes to a base64 encoded string."""
	return b64encode(data).decode("utf-8")


def build_qr_payload_from_xml(signed_xml: str, codigo_seguridad: str, *, consulta_base_url: Optional[str] = None) -> Dict[str, str]:
	"""Extrae campos necesarios del XML firmado (RNCEmisor, eNCF, MontoTotal, FechaEmision)
	para construir el payload del QR. Retorna un dict con 'texto' (para el QR) y 'url' (si se armó).

	Nota: La URL de consulta exacta puede variar por ambiente/pauta DGII; si se provee consulta_base_url
	se añade como parámetro apropiado.
	"""
	root = ET.fromstring(signed_xml)
	# Buscar bajo ECF/Encabezado
	encabezado = root.find(".//Encabezado")
	if encabezado is None:
		raise ValueError("XML e-CF inválido: falta Encabezado")
	iddoc = encabezado.find("IdDoc")
	emisor = encabezado.find("Emisor")
	totales = encabezado.find("Totales")
	if iddoc is None or emisor is None or totales is None:
		raise ValueError("XML e-CF inválido: faltan IdDoc/Emisor/Totales")
	e_ncf = (iddoc.findtext("eNCF") or "").strip()
	rnc_emisor = (emisor.findtext("RNCEmisor") or "").strip()
	fecha_emision = (emisor.findtext("FechaEmision") or "").strip()
	monto_total = (totales.findtext("MontoTotal") or "").strip()
	if not (e_ncf and rnc_emisor and fecha_emision and monto_total and codigo_seguridad):
		raise ValueError("Faltan campos requeridos para QR: eNCF/RNCEmisor/FechaEmision/MontoTotal/CodigoSeguridad")

	# Formato de texto QR (ajustable a pauta DGII; aquí usamos pares clave=valor separados por '|')
	texto = f"RNC={rnc_emisor}|eNCF={e_ncf}|FechaEmision={fecha_emision}|MontoTotal={monto_total}|CodigoSeguridad={codigo_seguridad}"
	url = None
	if consulta_base_url:
		sep = "&" if "?" in consulta_base_url else "?"
		url = f"{consulta_base_url}{sep}rnc={rnc_emisor}&encf={e_ncf}&cs={codigo_seguridad}"
	return {"texto": texto, "url": url}

