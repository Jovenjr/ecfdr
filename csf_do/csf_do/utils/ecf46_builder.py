from __future__ import annotations
from typing import Dict, List, Tuple, Optional
from xml.etree import ElementTree as ET
from datetime import datetime
from decimal import Decimal, InvalidOperation
import json
import importlib.resources as pkg_resources

from .xml_utils import escape_text, remove_empty_elements
from .xsd_validator import validate_xml
from .input_validator import validate_against_spec
from .field_validators import (
    validate_encf,
    validate_rnc,
    validate_phone,
    validate_email,
)


REQUIRED_EMISOR_FIELDS = [
    "RNCEmisor",
    "RazonSocialEmisor",
    "DireccionEmisor",
    "FechaEmision",
]

REQUIRED_IDDOC_FIELDS = [
    "TipoeCF",
    "eNCF",
    "FechaVencimientoSecuencia",
    "TipoIngresos",
    "TipoPago",
]

REQUIRED_COMPRADOR_FIELDS = [
    "RazonSocialComprador",
]

REQUIRED_ITEM_FIELDS = [
    "NumeroLinea",
    "IndicadorFacturacion",
    "NombreItem",
    "IndicadorBienoServicio",
    "CantidadItem",
    "PrecioUnitarioItem",
    "MontoItem",
]

CATALOG_FILES = {
    "UnidadMedidaType": "unidad_medida.json",
    "TipoMonedaType": "tipo_moneda.json",
    "ProvinciaMunicipioType": "provincia_municipio.json",
}


def _load_catalog_values(catalog_json_file: str) -> List[str]:
    data_pkg = "csf_do.csf_do.data"
    try:
        with pkg_resources.files(data_pkg).joinpath(catalog_json_file).open("r", encoding="utf-8") as f:
            payload = json.load(f)
            values = payload.get("values")
            if values is None:
                entries = payload.get("entries", [])
                return [str(e.get("code")) for e in entries if e.get("code") is not None]
            return [str(v) for v in values]
    except FileNotFoundError:
        return []


def _validate_catalog_value(field: str, value: Optional[str], *, catalog_type: str) -> None:
    if value is None or str(value) == "":
        return
    json_file = CATALOG_FILES.get(catalog_type)
    if not json_file:
        return
    allowed = _load_catalog_values(json_file)
    if allowed and str(value) not in allowed:
        raise ValueError(f"Valor inválido para {field}: '{value}'. Debe pertenecer a catálogo {catalog_type}.")


def _add_if_present(parent: ET.Element, tag: str, value: Optional[str]) -> None:
    if value is not None and str(value) != "":
        ET.SubElement(parent, tag).text = escape_text(str(value))


def _to_dmy(date_str: str) -> str:
    s = str(date_str)
    try:
        dt = datetime.strptime(s, "%Y-%m-%d")
        return dt.strftime("%d-%m-%Y")
    except Exception:
        return s


def _to_dmy_hms(datetime_str: str) -> str:
    s = str(datetime_str)
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            dt = datetime.strptime(s, fmt)
            return dt.strftime("%d-%m-%Y %H:%M:%S")
        except Exception:
            pass
    return s


def build_ecf46_xml(data: Dict) -> str:
    try:
        errs = validate_against_spec(data, spec_name="ecf46.json")
        if errs:
            raise ValueError("; ".join(errs))
    except FileNotFoundError:
        pass

    root = ET.Element("ECF")

    encabezado_in = data.get("encabezado", {})
    encabezado = ET.SubElement(root, "Encabezado")

    version = encabezado_in.get("Version", "1.0")
    ET.SubElement(encabezado, "Version").text = escape_text(str(version))

    iddoc_in = encabezado_in.get("IdDoc", {})
    iddoc = ET.SubElement(encabezado, "IdDoc")
    for key in REQUIRED_IDDOC_FIELDS:
        val = iddoc_in.get(key)
        if val is None or str(val) == "":
            raise ValueError(f"Falta campo requerido en IdDoc: {key}")
        text_val = str(val)
        if key in ("FechaVencimientoSecuencia", "FechaLimitePago"):
            text_val = _to_dmy(text_val)
        ET.SubElement(iddoc, key).text = escape_text(text_val)
    validate_encf(iddoc_in.get("eNCF"))

    emisor_in = encabezado_in.get("Emisor", {})
    emisor = ET.SubElement(encabezado, "Emisor")
    for key in REQUIRED_EMISOR_FIELDS:
        val = emisor_in.get(key)
        if val is None or str(val) == "":
            raise ValueError(f"Falta campo requerido en Emisor: {key}")
        text_val = _to_dmy(str(val)) if key == "FechaEmision" else str(val)
        ET.SubElement(emisor, key).text = escape_text(text_val)
    validate_rnc(emisor_in.get("RNCEmisor"), field_name="RNCEmisor")
    _add_if_present(emisor, "NombreComercial", emisor_in.get("NombreComercial"))
    _add_if_present(emisor, "Sucursal", emisor_in.get("Sucursal"))
    municipio = emisor_in.get("Municipio")
    provincia = emisor_in.get("Provincia")
    _validate_catalog_value("Municipio", municipio, catalog_type="ProvinciaMunicipioType")
    _validate_catalog_value("Provincia", provincia, catalog_type="ProvinciaMunicipioType")
    _add_if_present(emisor, "Municipio", municipio)
    _add_if_present(emisor, "Provincia", provincia)
    if emisor_in.get("TablaTelefonoEmisor"):
        tabla = ET.SubElement(emisor, "TablaTelefonoEmisor")
        for tel in emisor_in["TablaTelefonoEmisor"]:
            validate_phone(tel, field_name="TelefonoEmisor")
            _add_if_present(tabla, "TelefonoEmisor", tel)
    if emisor_in.get("CorreoEmisor"):
        validate_email(emisor_in.get("CorreoEmisor"), field_name="CorreoEmisor")
        _add_if_present(emisor, "CorreoEmisor", emisor_in.get("CorreoEmisor"))

    comprador_in = encabezado_in.get("Comprador", {})
    comprador = ET.SubElement(encabezado, "Comprador")
    for key in REQUIRED_COMPRADOR_FIELDS:
        val = comprador_in.get(key)
        if val is None or str(val) == "":
            raise ValueError(f"Falta campo requerido en Comprador: {key}")
        _add_if_present(comprador, key, val)
    if comprador_in.get("CorreoComprador"):
        validate_email(comprador_in.get("CorreoComprador"), field_name="CorreoComprador")
    for tag in (
        "RNCComprador",
        "IdentificadorExtranjero",
        "ContactoComprador",
        "CorreoComprador",
        "DireccionComprador",
        "MunicipioComprador",
        "ProvinciaComprador",
        "FechaEntrega",
        "ContactoEntrega",
        "DireccionEntrega",
        "TelefonoAdicional",
        "FechaOrdenCompra",
        "NumeroOrdenCompra",
        "CodigoInternoComprador",
        "ResponsablePago",
        "InformacionAdicionalComprador",
    ):
        _add_if_present(comprador, tag, comprador_in.get(tag))

    totales_in = encabezado_in.get("Totales", {})
    totales = ET.SubElement(encabezado, "Totales")
    monto_total = totales_in.get("MontoTotal")
    if monto_total is None or str(monto_total) == "":
        raise ValueError("Falta campo requerido en Totales: MontoTotal")
    _add_if_present(totales, "TotalITBIS", totales_in.get("TotalITBIS"))
    ET.SubElement(totales, "MontoTotal").text = escape_text(str(monto_total))

    otra_in = encabezado_in.get("OtraMoneda")
    otra_total_om = None
    if otra_in:
        otra = ET.SubElement(encabezado, "OtraMoneda")
        tipo_moneda = otra_in.get("TipoMoneda")
        _validate_catalog_value("TipoMoneda", tipo_moneda, catalog_type="TipoMonedaType")
        _add_if_present(otra, "TipoMoneda", tipo_moneda)
        _add_if_present(otra, "TipoCambio", otra_in.get("TipoCambio"))
        _add_if_present(otra, "MontoExentoOtraMoneda", otra_in.get("MontoExentoOtraMoneda"))
        if otra_in.get("MontoTotalOtraMoneda") is not None:
            otra_total_om = otra_in.get("MontoTotalOtraMoneda")
            _add_if_present(otra, "MontoTotalOtraMoneda", otra_total_om)

    detalles_in = data.get("detalles", {})
    items: List[Dict] = detalles_in.get("items", [])
    if not items:
        raise ValueError("Se requiere al menos un Item en DetallesItems")
    detalles_el = ET.SubElement(root, "DetallesItems")
    sum_items = Decimal("0")
    sum_items_otra_moneda = Decimal("0")
    for it_in in items:
        item_el = ET.SubElement(detalles_el, "Item")
        for key in REQUIRED_ITEM_FIELDS:
            val = it_in.get(key)
            if val is None or str(val) == "":
                raise ValueError(f"Falta campo requerido en Item: {key}")
            ET.SubElement(item_el, key).text = escape_text(str(val))
        try:
            sum_items += Decimal(str(it_in.get("MontoItem")))
        except (InvalidOperation, TypeError):
            raise ValueError("MontoItem inválido: debe ser número con hasta 2 decimales")
        _add_if_present(item_el, "DescripcionItem", it_in.get("DescripcionItem"))
        unidad = it_in.get("UnidadMedida")
        _validate_catalog_value("UnidadMedida", unidad, catalog_type="UnidadMedidaType")
        _add_if_present(item_el, "UnidadMedida", unidad)
        if it_in.get("OtraMonedaDetalle"):
            omd = ET.SubElement(item_el, "OtraMonedaDetalle")
            _add_if_present(omd, "PrecioOtraMoneda", it_in["OtraMonedaDetalle"].get("PrecioOtraMoneda"))
            _add_if_present(omd, "DescuentoOtraMoneda", it_in["OtraMonedaDetalle"].get("DescuentoOtraMoneda"))
            _add_if_present(omd, "RecargoOtraMoneda", it_in["OtraMonedaDetalle"].get("RecargoOtraMoneda"))
            monto_item_om = it_in["OtraMonedaDetalle"].get("MontoItemOtraMoneda")
            _add_if_present(omd, "MontoItemOtraMoneda", monto_item_om)
            if monto_item_om is not None:
                try:
                    sum_items_otra_moneda += Decimal(str(monto_item_om))
                except (InvalidOperation, TypeError):
                    raise ValueError("MontoItemOtraMoneda inválido: debe ser número con hasta 2 decimales")

    fecha_firma = data.get("fecha_hora_firma")
    if not fecha_firma:
        raise ValueError("Falta campo requerido: fecha_hora_firma")
    ET.SubElement(root, "FechaHoraFirma").text = escape_text(_to_dmy_hms(str(fecha_firma)))

    ET.SubElement(root, "Signature").text = "-"

    try:
        total = Decimal(str(monto_total))
    except (InvalidOperation, TypeError):
        raise ValueError("MontoTotal inválido: debe ser número con hasta 2 decimales")
    if (sum_items - total).copy_abs() > Decimal("0.01"):
        raise ValueError(f"Inconsistencia Totales: suma(MontoItem)={sum_items} difiere de MontoTotal={total}")
    if otra_total_om is not None:
        try:
            total_om = Decimal(str(otra_total_om))
        except (InvalidOperation, TypeError):
            raise ValueError("MontoTotalOtraMoneda inválido: debe ser número con hasta 2 decimales")
        if (sum_items_otra_moneda - total_om).copy_abs() > Decimal("0.01"):
            raise ValueError(
                f"Inconsistencia Totales OtraMoneda: suma(MontoItemOtraMoneda)={sum_items_otra_moneda} difiere de MontoTotalOtraMoneda={total_om}"
            )

    remove_empty_elements(root)

    return ET.tostring(root, encoding="utf-8").decode("utf-8")


def build_and_validate_ecf46(data: Dict) -> Tuple[str, bool, List[str]]:
    xml = build_ecf46_xml(data)
    ok, errors = validate_xml(xml, xsd_name="e-CF 46 v.1.0.xsd")
    return xml, ok, errors


