"""
Generador 1:1 del XML para e-CF 33 (Nota de Débito Electrónica) basado en el XSD "e-CF 33 v.1.0.xsd".

Cobertura mínima:
- ECF/Encabezado/Version
- ECF/Encabezado/IdDoc: TipoeCF, eNCF, FechaVencimientoSecuencia, TipoIngresos, TipoPago (+ opcionales)
- ECF/Encabezado/Emisor: RNCEmisor, RazonSocialEmisor, DireccionEmisor, FechaEmision (+ opcionales)
- ECF/Encabezado/Comprador: opcional
- ECF/Encabezado/Totales: MontoTotal (requerido)
- ECF/DetallesItems/Item: NumeroLinea, IndicadorFacturacion, NombreItem, IndicadorBienoServicio, CantidadItem, PrecioUnitarioItem, MontoItem
  (Retencion es opcional, si se provee debe ir inmediatamente después de IndicadorFacturacion)
- ECF/FechaHoraFirma (requerido)
- ECF/(xs:any) → Signature placeholder con texto no vacío

Incluye:
- Normalización de fechas (DD-MM-YYYY) y datetime (DD-MM-YYYY HH:MM:SS)
- Validación previa contra spec JSON (ecf33.json) si existe
- Validaciones de formato (eNCF, RNC, Teléfono, Email)
- Validación de catálogos (UnidadMedida, Provincia/Municipio) si disponibles
- Coherencia de totales (moneda base y otra moneda)
- Validación final contra XSD con lxml
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

def build_ecf33_xml(data: Dict) -> str:
    # Validación previa contra spec (si existe)
    try:
        errs = validate_against_spec(data, spec_name="ecf33.json")
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
    # Validación amigable eNCF
    validate_encf(iddoc_in.get("eNCF"))

    # Emisor
    emisor_in = encabezado_in.get("Emisor", {})
    emisor = ET.SubElement(encabezado, "Emisor")
    for key in REQUIRED_EMISOR_FIELDS:
        val = emisor_in.get(key)
        if val is None or str(val) == "":
            raise ValueError(f"Falta campo requerido en Emisor: {key}")
        text_val = to_dmy(str(val)) if key == "FechaEmision" else str(val)
        ET.SubElement(emisor, key).text = escape_text(text_val)
    # Validación RNC
    validate_rnc(emisor_in.get("RNCEmisor"), field_name="RNCEmisor")
    # Opcionales + catálogos
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

    # Comprador (opcional)
    comprador_in = encabezado_in.get("Comprador")
    if comprador_in is not None:
        comprador = ET.SubElement(encabezado, "Comprador")
        if comprador_in.get("CorreoComprador"):
            validate_email(comprador_in.get("CorreoComprador"), field_name="CorreoComprador")
        for tag in (
            "RNCComprador",
            "IdentificadorExtranjero",
            "RazonSocialComprador",
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
            value = comprador_in.get(tag)
            if tag in ("MunicipioComprador", "ProvinciaComprador"):
                validate_catalog_value(tag, value, catalog_type="ProvinciaMunicipioType")
            if tag in ("FechaEntrega", "FechaOrdenCompra") and value:
                value = to_dmy(str(value))
            add_text_if_not_empty(comprador, tag, value)

    # Totales
    totales_in = encabezado_in.get("Totales", {})
    totales = ET.SubElement(encabezado, "Totales")
    monto_total = totales_in.get("MontoTotal")
    if monto_total is None or str(monto_total) == "":
        raise ValueError("Falta campo requerido en Totales: MontoTotal")
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
        add_text_if_not_empty(otra, "MontoExentoOtraMoneda", otra_in.get("MontoExentoOtraMoneda"))
        if otra_in.get("MontoTotalOtraMoneda") is not None:
            otra_total_om = otra_in.get("MontoTotalOtraMoneda")
            add_text_if_not_empty(otra, "MontoTotalOtraMoneda", otra_total_om)

    # Detalles
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
            if key == "IndicadorFacturacion":
                # Retencion opcional
                ret_in = it_in.get("Retencion")
                if ret_in:
                    ret_el = ET.SubElement(item_el, "Retencion")
                    add_text_if_not_empty(ret_el, "IndicadorAgenteRetencionoPercepcion", ret_in.get("IndicadorAgenteRetencionoPercepcion"))
                    add_text_if_not_empty(ret_el, "MontoITBISRetenido", ret_in.get("MontoITBISRetenido"))
                    add_text_if_not_empty(ret_el, "MontoISRRetenido", ret_in.get("MontoISRRetenido"))
        try:
            sum_items += Decimal(str(it_in.get("MontoItem")))
        except (InvalidOperation, TypeError):
            raise ValueError("MontoItem inválido: debe ser número con hasta 2 decimales")
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

    # Subtotales/Descuentos/Paginacion omitidos (opcionales)

    # InformacionReferencia (requerido en 33)
    info_ref_in = data.get("informacion_referencia") or data.get("InformacionReferencia")
    if not info_ref_in:
        raise ValueError("Falta bloque requerido: InformacionReferencia")
    info_ref = ET.SubElement(root, "InformacionReferencia")
    ncf_mod = info_ref_in.get("NCFModificado")
    fecha_mod = info_ref_in.get("FechaNCFModificado")
    cod_mod = info_ref_in.get("CodigoModificacion")
    if not ncf_mod or not fecha_mod or not cod_mod:
        raise ValueError("InformacionReferencia requiere NCFModificado, FechaNCFModificado y CodigoModificacion")
    ET.SubElement(info_ref, "NCFModificado").text = escape_text(str(ncf_mod))
    ET.SubElement(info_ref, "FechaNCFModificado").text = escape_text(to_dmy(str(fecha_mod)))
    ET.SubElement(info_ref, "CodigoModificacion").text = escape_text(str(cod_mod))

    # FechaHoraFirma
    fecha_firma = data.get("fecha_hora_firma")
    if not fecha_firma:
        raise ValueError("Falta campo requerido: fecha_hora_firma")
    ET.SubElement(root, "FechaHoraFirma").text = escape_text(to_dmy_hms(str(fecha_firma)))

    # xs:any
    ET.SubElement(root, "Signature").text = "-"

    # Coherencia de totales
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


def build_and_validate_ecf33(data: Dict) -> Tuple[str, bool, List[str]]:
    xml = build_ecf33_xml(data)
    ok, errors = validate_xml(xml, xsd_name="e-CF 33 v.1.0.xsd")
    return xml, ok, errors


