"""
Generador del XML para e-CF 41 (Comprobante Electrónico de Compras) basado en el
XSD "e-CF 41 v.1.0.xsd".

Cobertura mínima:
- `ECF/Encabezado/Version`
- `ECF/Encabezado/IdDoc`: `TipoeCF`, `eNCF`, `FechaVencimientoSecuencia`
- `ECF/Encabezado/Emisor`: `RNCEmisor`, `RazonSocialEmisor`, `DireccionEmisor`,
  `FechaEmision`
- `ECF/Encabezado/Comprador`: `RNCComprador`, `RazonSocialComprador`
- `ECF/Encabezado/Totales`: `MontoTotal`
- `ECF/DetallesItems/Item`: `NumeroLinea`, `IndicadorFacturacion`, `Retencion`,
  `NombreItem`, `IndicadorBienoServicio`, `CantidadItem`, `PrecioUnitarioItem`,
  `MontoItem`
- `ECF/FechaHoraFirma`
- `ECF/(xs:any)` → placeholder `Signature`

Incluye:
- Normalización de fechas (DD-MM-YYYY) y datetimes (DD-MM-YYYY HH:MM:SS)
- Validaciones de formato (eNCF, RNC, teléfono, correo electrónico)
- Validaciones contra catálogos (`ProvinciaMunicipioType`, `UnidadMedidaType`,
  `TipoMonedaType`)
- Coherencia de totales en moneda base y otra moneda
- Validación previa contra spec JSON (si disponible) y contra el XSD oficial
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Dict, List, Tuple
from xml.etree import ElementTree as ET

from .amount_utils import round_money_2, round_unit_price_4, to_str
from .field_validators import (
    validate_email,
    validate_encf,
    validate_phone,
    validate_rnc,
)
from .input_validator import validate_against_spec
from .xml_builder_common import add_text_if_not_empty, to_dmy, to_dmy_hms, validate_catalog_value
from .xml_utils import escape_text, remove_empty_elements
from .xsd_validator import validate_xml


REQUIRED_IDDOC_FIELDS = [
    "TipoeCF",
    "eNCF",
    "FechaVencimientoSecuencia",
]

REQUIRED_EMISOR_FIELDS = [
    "RNCEmisor",
    "RazonSocialEmisor",
    "DireccionEmisor",
    "FechaEmision",
]

REQUIRED_COMPRADOR_FIELDS = [
    "RNCComprador",
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


def _add_retencion_block(parent: ET.Element, item_data: Dict) -> None:
    """Inserta el bloque `Retencion` validando su indicador obligatorio."""

    ret_in = item_data.get("Retencion") or {}
    indicador = ret_in.get("IndicadorAgenteRetencionoPercepcion")
    if indicador in (None, ""):
        raise ValueError("Falta Retencion.IndicadorAgenteRetencionoPercepcion en Item")

    ret_el = ET.SubElement(parent, "Retencion")
    ET.SubElement(ret_el, "IndicadorAgenteRetencionoPercepcion").text = escape_text(str(indicador))

    monto_itbis = ret_in.get("MontoITBISRetenido")
    if monto_itbis not in (None, ""):
        ET.SubElement(ret_el, "MontoITBISRetenido").text = to_str(round_money_2(monto_itbis))

    monto_isr = ret_in.get("MontoISRRetenido")
    if monto_isr not in (None, ""):
        ET.SubElement(ret_el, "MontoISRRetenido").text = to_str(round_money_2(monto_isr))


def build_ecf41_xml(data: Dict) -> str:
    # Validación previa contra el spec (si existe)
    try:
        errors = validate_against_spec(data, spec_name="ecf41.json")
        if errors:
            raise ValueError("; ".join(errors))
    except FileNotFoundError:
        pass

    root = ET.Element("ECF")

    encabezado_in = data.get("encabezado", {})
    encabezado = ET.SubElement(root, "Encabezado")

    # Version
    version = encabezado_in.get("Version", "1.0")
    ET.SubElement(encabezado, "Version").text = escape_text(str(version))

    # IdDoc
    iddoc_in = encabezado_in.get("IdDoc", {})
    iddoc = ET.SubElement(encabezado, "IdDoc")
    for key in REQUIRED_IDDOC_FIELDS:
        val = iddoc_in.get(key)
        if val is None or str(val) == "":
            raise ValueError(f"Falta campo requerido en IdDoc: {key}")
        text_val = str(val)
        if key in ("FechaVencimientoSecuencia", "FechaLimitePago"):
            text_val = to_dmy(text_val)
        ET.SubElement(iddoc, key).text = escape_text(text_val)
    validate_encf(iddoc_in.get("eNCF"))

    for opt_key in (
        "IndicadorEnvioDiferido",
        "FechaLimitePago",
        "TerminoPago",
        "TipoPago",
        "TipoCuentaPago",
        "NumeroCuentaPago",
        "BancoPago",
        "FechaDesde",
        "FechaHasta",
    ):
        if opt_key in iddoc_in:
            opt_val = iddoc_in.get(opt_key)
            if opt_key in ("FechaLimitePago", "FechaDesde", "FechaHasta") and opt_val:
                opt_val = to_dmy(str(opt_val))
            add_text_if_not_empty(iddoc, opt_key, opt_val)

    # Emisor
    emisor_in = encabezado_in.get("Emisor", {})
    emisor = ET.SubElement(encabezado, "Emisor")
    for key in REQUIRED_EMISOR_FIELDS:
        val = emisor_in.get(key)
        if val is None or str(val) == "":
            raise ValueError(f"Falta campo requerido en Emisor: {key}")
        text_val = to_dmy(str(val)) if key == "FechaEmision" else str(val)
        ET.SubElement(emisor, key).text = escape_text(text_val)
    validate_rnc(emisor_in.get("RNCEmisor"), field_name="RNCEmisor")

    add_text_if_not_empty(emisor, "NombreComercial", emisor_in.get("NombreComercial"))
    add_text_if_not_empty(emisor, "Sucursal", emisor_in.get("Sucursal"))
    municipio = emisor_in.get("Municipio")
    provincia = emisor_in.get("Provincia")
    validate_catalog_value("Municipio", municipio, catalog_type="ProvinciaMunicipioType")
    validate_catalog_value("Provincia", provincia, catalog_type="ProvinciaMunicipioType")
    add_text_if_not_empty(emisor, "Municipio", municipio)
    add_text_if_not_empty(emisor, "Provincia", provincia)
    if emisor_in.get("TablaTelefonoEmisor"):
        tabla = ET.SubElement(emisor, "TablaTelefonoEmisor")
        for tel in emisor_in["TablaTelefonoEmisor"]:
            validate_phone(tel, field_name="TelefonoEmisor")
            add_text_if_not_empty(tabla, "TelefonoEmisor", tel)
    correo_emisor = emisor_in.get("CorreoEmisor")
    if correo_emisor:
        validate_email(correo_emisor, field_name="CorreoEmisor")
        add_text_if_not_empty(emisor, "CorreoEmisor", correo_emisor)

    # Comprador
    comprador_in = encabezado_in.get("Comprador", {})
    comprador = ET.SubElement(encabezado, "Comprador")
    for key in REQUIRED_COMPRADOR_FIELDS:
        val = comprador_in.get(key)
        if val is None or str(val) == "":
            raise ValueError(f"Falta campo requerido en Comprador: {key}")
        ET.SubElement(comprador, key).text = escape_text(str(val))

    optional_comprador_fields = (
        "IdentificadorExtranjero",
        "ContactoComprador",
        "CorreoComprador",
        "DireccionComprador",
        "MunicipioComprador",
        "ProvinciaComprador",
        "TelefonoAdicional",
        "FechaEntrega",
        "ContactoEntrega",
        "DireccionEntrega",
    )
    for field in optional_comprador_fields:
        val = comprador_in.get(field)
        if val in (None, ""):
            continue
        if field == "CorreoComprador":
            validate_email(val, field_name="CorreoComprador")
        if field in ("MunicipioComprador", "ProvinciaComprador"):
            validate_catalog_value(field, val, catalog_type="ProvinciaMunicipioType")
        if field == "FechaEntrega":
            val = to_dmy(str(val))
        add_text_if_not_empty(comprador, field, val)

    # Totales
    totales_in = encabezado_in.get("Totales", {})
    totales = ET.SubElement(encabezado, "Totales")
    monto_total = totales_in.get("MontoTotal")
    if monto_total in (None, ""):
        raise ValueError("Falta campo requerido en Totales: MontoTotal")
    add_text_if_not_empty(totales, "TotalITBIS", totales_in.get("TotalITBIS"))
    add_text_if_not_empty(totales, "MontoExento", totales_in.get("MontoExento"))
    add_text_if_not_empty(
        totales,
        "MontoExentoPorProveedoresInformales",
        totales_in.get("MontoExentoPorProveedoresInformales"),
    )
    monto_total_str = to_str(round_money_2(monto_total))
    ET.SubElement(totales, "MontoTotal").text = escape_text(monto_total_str)

    # OtraMoneda
    otra_in = encabezado_in.get("OtraMoneda")
    otra_total_om = None
    if otra_in:
        otra = ET.SubElement(encabezado, "OtraMoneda")
        tipo_moneda = otra_in.get("TipoMoneda")
        validate_catalog_value("TipoMoneda", tipo_moneda, catalog_type="TipoMonedaType")
        add_text_if_not_empty(otra, "TipoMoneda", tipo_moneda)
        add_text_if_not_empty(otra, "TipoCambio", otra_in.get("TipoCambio"))
        add_text_if_not_empty(otra, "MontoExentoOtraMoneda", otra_in.get("MontoExentoOtraMoneda"))
        if otra_in.get("MontoTotalOtraMoneda") is not None:
            otra_total_om = otra_in.get("MontoTotalOtraMoneda")
            add_text_if_not_empty(otra, "MontoTotalOtraMoneda", otra_total_om)

    # DetallesItems
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
            text_val = str(val)
            if key == "PrecioUnitarioItem":
                text_val = to_str(round_unit_price_4(val))
            elif key == "MontoItem":
                text_val = to_str(round_money_2(val))
            ET.SubElement(item_el, key).text = escape_text(text_val)

            if key == "IndicadorFacturacion":
                _add_retencion_block(item_el, it_in)

        try:
            sum_items += Decimal(to_str(round_money_2(it_in.get("MontoItem"))))
        except (InvalidOperation, TypeError):
            raise ValueError("MontoItem inválido: debe ser número con hasta 2 decimales")

        add_text_if_not_empty(item_el, "DescripcionItem", it_in.get("DescripcionItem"))
        unidad = it_in.get("UnidadMedida")
        validate_catalog_value("UnidadMedida", unidad, catalog_type="UnidadMedidaType")
        add_text_if_not_empty(item_el, "UnidadMedida", unidad)

        if it_in.get("OtraMonedaDetalle"):
            omd_in = it_in["OtraMonedaDetalle"]
            omd = ET.SubElement(item_el, "OtraMonedaDetalle")
            add_text_if_not_empty(omd, "PrecioOtraMoneda", omd_in.get("PrecioOtraMoneda"))
            add_text_if_not_empty(omd, "DescuentoOtraMoneda", omd_in.get("DescuentoOtraMoneda"))
            add_text_if_not_empty(omd, "RecargoOtraMoneda", omd_in.get("RecargoOtraMoneda"))
            monto_item_om = omd_in.get("MontoItemOtraMoneda")
            add_text_if_not_empty(omd, "MontoItemOtraMoneda", monto_item_om)
            if monto_item_om is not None:
                try:
                    sum_items_otra_moneda += Decimal(str(monto_item_om))
                except (InvalidOperation, TypeError):
                    raise ValueError("MontoItemOtraMoneda inválido: debe ser número con hasta 2 decimales")

    # FechaHoraFirma
    fecha_firma = data.get("fecha_hora_firma")
    if not fecha_firma:
        raise ValueError("Falta campo requerido: fecha_hora_firma")
    ET.SubElement(root, "FechaHoraFirma").text = escape_text(to_dmy_hms(str(fecha_firma)))

    # xs:any placeholder
    ET.SubElement(root, "Signature").text = "-"

    # Coherencia de totales
    try:
        total = Decimal(monto_total_str)
    except (InvalidOperation, TypeError):
        raise ValueError("MontoTotal inválido: debe ser número con hasta 2 decimales")
    if (sum_items - total).copy_abs() > Decimal("0.01"):
        raise ValueError(
            f"Inconsistencia Totales: suma(MontoItem)={sum_items} difiere de MontoTotal={total}"
        )

    if otra_total_om is not None:
        try:
            total_om = Decimal(str(otra_total_om))
        except (InvalidOperation, TypeError):
            raise ValueError("MontoTotalOtraMoneda inválido: debe ser número con hasta 2 decimales")
        if (sum_items_otra_moneda - total_om).copy_abs() > Decimal("0.01"):
            raise ValueError(
                "Inconsistencia Totales OtraMoneda: "
                f"suma(MontoItemOtraMoneda)={sum_items_otra_moneda} difiere de MontoTotalOtraMoneda={total_om}"
            )

    remove_empty_elements(root)

    return ET.tostring(root, encoding="utf-8").decode("utf-8")


def build_and_validate_ecf41(data: Dict) -> Tuple[str, bool, List[str]]:
    xml = build_ecf41_xml(data)
    ok, errors = validate_xml(xml, xsd_name="e-CF 41 v.1.0.xsd")
    return xml, ok, errors
