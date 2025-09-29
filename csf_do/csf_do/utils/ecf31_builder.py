"""
Generador 1:1 del XML para e-CF 31 (Factura de Crédito Fiscal) basado en el XSD "e-CF 31 v.1.0.xsd".

Cubre estructura mínima requerida:
- ECF/Encabezado/Version
- ECF/Encabezado/IdDoc: TipoeCF, eNCF, FechaVencimientoSecuencia, TipoIngresos, TipoPago (+ opcionales)
- ECF/Encabezado/Emisor: RNCEmisor, RazonSocialEmisor, DireccionEmisor, FechaEmision (+ opcionales)
- ECF/Encabezado/Comprador: RNCComprador, RazonSocialComprador (+ opcionales)
- ECF/Encabezado/Totales: MontoTotal (requerido)
- ECF/DetallesItems/Item: NumeroLinea, IndicadorFacturacion, NombreItem, IndicadorBienoServicio, CantidadItem, PrecioUnitarioItem, MontoItem
- ECF/FechaHoraFirma (requerido)
- ECF/(xs:any) → Signature placeholder con texto no vacío

Incluye:
- Normalización de fechas a formatos XSD (DD-MM-YYYY y "DD-MM-YYYY HH:MM:SS").
- Validación contra XSD usando xsd_validator.
- Validaciones de catálogos (UnidadMedida, TipoMoneda, Provincia/Municipio) si los catálogos están presentes.
"""
from __future__ import annotations
from typing import Dict, List, Tuple, Optional
from xml.etree import ElementTree as ET
from decimal import Decimal, InvalidOperation

from .xml_utils import escape_text, remove_empty_elements
from .xsd_validator import validate_xml
from .input_validator import validate_against_spec
from .field_validators import (
    validate_encf,
    validate_rnc,
    validate_phone,
    validate_email,
)
from .amount_utils import round_money_2, round_unit_price_4, round_subquantity_3, to_str
from .xml_builder_common import (
    add_text_if_not_empty,
    to_dmy,
    to_dmy_hms,
    validate_catalog_value,
)


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

REQUIRED_IDDOC_FIELDS = [
    "TipoeCF",
    "eNCF",
    "FechaVencimientoSecuencia",
    "TipoIngresos",
    "TipoPago",
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

def _normalize_tipo_ingresos(value: str) -> str:
    """Asegura formato '01'..'06' según TipoIngresosValidationType.
    Si viene '1'..'6' lo formatea a dos dígitos.
    """
    s = str(value).strip()
    if s.isdigit() and len(s) == 1:
        s = f"0{s}"
    return s


def build_ecf31_xml(data: Dict) -> str:
    # Validación previa contra spec (si existe)
    try:
        errs = validate_against_spec(data, spec_name="ecf31.json")
        if errs:
            raise ValueError("; ".join(errs))
    except FileNotFoundError:
        pass

    root = ET.Element("ECF")

    encabezado_in = data.get("encabezado", {})
    encabezado = ET.SubElement(root, "Encabezado")

    # Version
    version = encabezado_in.get("Version", "1.0")
    ET.SubElement(encabezado, "Version").text = escape_text(str(version))

    # IdDoc (con campos requeridos)
    iddoc_in = encabezado_in.get("IdDoc", {})
    iddoc = ET.SubElement(encabezado, "IdDoc")
    for key in REQUIRED_IDDOC_FIELDS:
        val = iddoc_in.get(key)
        if val is None or str(val) == "":
            raise ValueError(f"Falta campo requerido en IdDoc: {key}")
        text_val = str(val)
        if key in ("FechaVencimientoSecuencia", "FechaLimitePago", "FechaDesde", "FechaHasta"):
            text_val = to_dmy(text_val)
        if key == "TipoIngresos":
            text_val = _normalize_tipo_ingresos(text_val)
        ET.SubElement(iddoc, key).text = escape_text(text_val)
    # Validaciones de formato amigables
    validate_encf(iddoc_in.get("eNCF"))
    # Opcionales comunes
    for opt in ("IndicadorEnvioDiferido", "IndicadorMontoGravado", "IndicadorServicioTodoIncluido",
                "FechaLimitePago", "TerminoPago", "TipoCuentaPago", "NumeroCuentaPago", "BancoPago",
                "FechaDesde", "FechaHasta", "TotalPaginas"):
        if opt in iddoc_in:
            val = iddoc_in.get(opt)
            if opt in ("FechaLimitePago", "FechaDesde", "FechaHasta") and val:
                val = to_dmy(str(val))
            add_text_if_not_empty(iddoc, opt, val)

    # Emisor
    emisor_in = encabezado_in.get("Emisor", {})
    emisor = ET.SubElement(encabezado, "Emisor")
    for key in REQUIRED_EMISOR_FIELDS:
        val = emisor_in.get(key)
        if val is None or str(val) == "":
            raise ValueError(f"Falta campo requerido en Emisor: {key}")
        text_val = to_dmy(str(val)) if key == "FechaEmision" else str(val)
        ET.SubElement(emisor, key).text = escape_text(text_val)
    # Validaciones de formato amigables
    validate_rnc(emisor_in.get("RNCEmisor"), field_name="RNCEmisor")
    # Opcionales emisor + validación catálogo Provincia/Municipio
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
    if emisor_in.get("CorreoEmisor"):
        validate_email(emisor_in.get("CorreoEmisor"), field_name="CorreoEmisor")
        add_text_if_not_empty(emisor, "CorreoEmisor", emisor_in.get("CorreoEmisor"))
    add_text_if_not_empty(emisor, "WebSite", emisor_in.get("WebSite"))
    add_text_if_not_empty(emisor, "ActividadEconomica", emisor_in.get("ActividadEconomica"))
    add_text_if_not_empty(emisor, "CodigoVendedor", emisor_in.get("CodigoVendedor"))
    add_text_if_not_empty(emisor, "NumeroFacturaInterna", emisor_in.get("NumeroFacturaInterna"))
    add_text_if_not_empty(emisor, "NumeroPedidoInterno", emisor_in.get("NumeroPedidoInterno"))
    add_text_if_not_empty(emisor, "ZonaVenta", emisor_in.get("ZonaVenta"))
    add_text_if_not_empty(emisor, "RutaVenta", emisor_in.get("RutaVenta"))
    add_text_if_not_empty(emisor, "InformacionAdicionalEmisor", emisor_in.get("InformacionAdicionalEmisor"))

    # Comprador (requerido)
    comprador_in = encabezado_in.get("Comprador", {})
    comprador = ET.SubElement(encabezado, "Comprador")
    for key in REQUIRED_COMPRADOR_FIELDS:
        val = comprador_in.get(key)
        if val is None or str(val) == "":
            raise ValueError(f"Falta campo requerido en Comprador: {key}")
        ET.SubElement(comprador, key).text = escape_text(str(val))
    # Comprador opcionales con catálogo Provincia/Municipio y fechas
    add_text_if_not_empty(comprador, "ContactoComprador", comprador_in.get("ContactoComprador"))
    if comprador_in.get("CorreoComprador"):
        validate_email(comprador_in.get("CorreoComprador"), field_name="CorreoComprador")
        add_text_if_not_empty(comprador, "CorreoComprador", comprador_in.get("CorreoComprador"))
    add_text_if_not_empty(comprador, "DireccionComprador", comprador_in.get("DireccionComprador"))
    mun_c = comprador_in.get("MunicipioComprador")
    prov_c = comprador_in.get("ProvinciaComprador")
    validate_catalog_value("MunicipioComprador", mun_c, catalog_type="ProvinciaMunicipioType")
    validate_catalog_value("ProvinciaComprador", prov_c, catalog_type="ProvinciaMunicipioType")
    add_text_if_not_empty(comprador, "MunicipioComprador", mun_c)
    add_text_if_not_empty(comprador, "ProvinciaComprador", prov_c)
    if comprador_in.get("FechaEntrega"):
        add_text_if_not_empty(comprador, "FechaEntrega", to_dmy(str(comprador_in.get("FechaEntrega"))))
    add_text_if_not_empty(comprador, "ContactoEntrega", comprador_in.get("ContactoEntrega"))
    add_text_if_not_empty(comprador, "DireccionEntrega", comprador_in.get("DireccionEntrega"))
    add_text_if_not_empty(comprador, "TelefonoAdicional", comprador_in.get("TelefonoAdicional"))
    if comprador_in.get("FechaOrdenCompra"):
        add_text_if_not_empty(comprador, "FechaOrdenCompra", to_dmy(str(comprador_in.get("FechaOrdenCompra"))))
    add_text_if_not_empty(comprador, "NumeroOrdenCompra", comprador_in.get("NumeroOrdenCompra"))
    add_text_if_not_empty(comprador, "CodigoInternoComprador", comprador_in.get("CodigoInternoComprador"))
    add_text_if_not_empty(comprador, "ResponsablePago", comprador_in.get("ResponsablePago"))
    add_text_if_not_empty(comprador, "InformacionAdicionalComprador", comprador_in.get("InformacionAdicionalComprador"))

    # Totales
    totales_in = encabezado_in.get("Totales", {})
    totales = ET.SubElement(encabezado, "Totales")
    monto_total = totales_in.get("MontoTotal")
    if monto_total is None or str(monto_total) == "":
        raise ValueError("Falta campo requerido en Totales: MontoTotal")
    # Algunos totales opcionales (los demás se omiten por ahora)
    add_text_if_not_empty(totales, "MontoGravadoTotal", totales_in.get("MontoGravadoTotal"))
    add_text_if_not_empty(totales, "MontoExento", totales_in.get("MontoExento"))
    add_text_if_not_empty(totales, "TotalITBIS", totales_in.get("TotalITBIS"))
    ET.SubElement(totales, "MontoTotal").text = escape_text(str(monto_total))

    # OtraMoneda (opcional)
    otra_in = encabezado_in.get("OtraMoneda")
    otra_total_om = None
    if otra_in:
        otra = ET.SubElement(encabezado, "OtraMoneda")
        tipo_moneda = otra_in.get("TipoMoneda")
        validate_catalog_value("TipoMoneda", tipo_moneda, catalog_type="TipoMonedaType")
        add_text_if_not_empty(otra, "TipoMoneda", tipo_moneda)
        add_text_if_not_empty(otra, "TipoCambio", otra_in.get("TipoCambio"))
        add_text_if_not_empty(otra, "MontoGravadoTotalOtraMoneda", otra_in.get("MontoGravadoTotalOtraMoneda"))
        add_text_if_not_empty(otra, "MontoExentoOtraMoneda", otra_in.get("MontoExentoOtraMoneda"))
        add_text_if_not_empty(otra, "TotalITBISOtraMoneda", otra_in.get("TotalITBISOtraMoneda"))
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
        # acumular MontoItem para validar totales
        try:
            sum_items += Decimal(str(it_in.get("MontoItem")))
        except (InvalidOperation, TypeError):
            raise ValueError("MontoItem inválido: debe ser número con hasta 2 decimales")
        # Opcionales
        if it_in.get("TablaCodigosItem"):
            tabla = ET.SubElement(item_el, "TablaCodigosItem")
            for code in it_in["TablaCodigosItem"]:
                cod_el = ET.SubElement(tabla, "CodigosItem")
                add_text_if_not_empty(cod_el, "TipoCodigo", code.get("TipoCodigo"))
                add_text_if_not_empty(cod_el, "CodigoItem", code.get("CodigoItem"))
        add_text_if_not_empty(item_el, "DescripcionItem", it_in.get("DescripcionItem"))
        unidad = it_in.get("UnidadMedida")
        validate_catalog_value("UnidadMedida", unidad, catalog_type="UnidadMedidaType")
        add_text_if_not_empty(item_el, "UnidadMedida", unidad)
        if it_in.get("OtraMonedaDetalle"):
            omd = ET.SubElement(item_el, "OtraMonedaDetalle")
            add_text_if_not_empty(omd, "PrecioOtraMoneda", it_in["OtraMonedaDetalle"].get("PrecioOtraMoneda"))
            add_text_if_not_empty(omd, "DescuentoOtraMoneda", it_in["OtraMonedaDetalle"].get("DescuentoOtraMoneda"))
            add_text_if_not_empty(omd, "RecargoOtraMoneda", it_in["OtraMonedaDetalle"].get("RecargoOtraMoneda"))
            monto_item_om = it_in["OtraMonedaDetalle"].get("MontoItemOtraMoneda")
            add_text_if_not_empty(omd, "MontoItemOtraMoneda", monto_item_om)
            if monto_item_om is not None:
                try:
                    sum_items_otra_moneda += Decimal(str(monto_item_om))
                except (InvalidOperation, TypeError):
                    raise ValueError("MontoItemOtraMoneda inválido: debe ser número con hasta 2 decimales")

    # FechaHoraFirma (requerido)
    fecha_firma = data.get("fecha_hora_firma")
    if not fecha_firma:
        raise ValueError("Falta campo requerido: fecha_hora_firma")
    ET.SubElement(root, "FechaHoraFirma").text = escape_text(to_dmy_hms(str(fecha_firma)))

    # xs:any → Signature placeholder (no vacío)
    ET.SubElement(root, "Signature").text = "-"

    # Coherencia de totales (tolerancia 0.01)
    try:
        total = Decimal(to_str(round_money_2(monto_total)))
    except (InvalidOperation, TypeError):
        raise ValueError("MontoTotal inválido: debe ser número con hasta 2 decimales")
    if (sum_items - total).copy_abs() > Decimal("0.01"):
        raise ValueError(f"Inconsistencia Totales: suma(MontoItem)={sum_items} difiere de MontoTotal={total}")

    # Coherencia de totales en OtraMoneda si se proporcionó
    if otra_total_om is not None:
        try:
            total_om = Decimal(str(otra_total_om))
        except (InvalidOperation, TypeError):
            raise ValueError("MontoTotalOtraMoneda inválido: debe ser número con hasta 2 decimales")
        if (sum_items_otra_moneda - total_om).copy_abs() > Decimal("0.01"):
            raise ValueError(
                f"Inconsistencia Totales OtraMoneda: suma(MontoItemOtraMoneda)={sum_items_otra_moneda} difiere de MontoTotalOtraMoneda={total_om}"
            )

    # Limpieza de elementos vacíos
    remove_empty_elements(root)

    return ET.tostring(root, encoding="utf-8").decode("utf-8")


def build_and_validate_ecf31(data: Dict) -> Tuple[str, bool, List[str]]:
    xml = build_ecf31_xml(data)
    ok, errors = validate_xml(xml, xsd_name="e-CF 31 v.1.0.xsd")
    return xml, ok, errors
