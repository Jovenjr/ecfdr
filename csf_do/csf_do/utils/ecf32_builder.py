"""
Generador 1:1 del XML para e-CF 32 (Factura de Consumo) basado en el XSD "e-CF 32 v.1.0.xsd".

Estructura mínima cubierta según spec generada:
- ECF/Encabezado/Version
- ECF/Encabezado/IdDoc: TipoeCF, eNCF, TipoIngresos, TipoPago (+ opcionales)
- ECF/Encabezado/Emisor: RNCEmisor, RazonSocialEmisor, DireccionEmisor, FechaEmision (+ opcionales)
- ECF/Encabezado/Comprador (presencia requerida por spec, sin campos obligatorios adicionales)
- ECF/Encabezado/Totales: MontoTotal (requerido)
- ECF/DetallesItems/Item: NumeroLinea, IndicadorFacturacion, NombreItem, IndicadorBienoServicio, CantidadItem, PrecioUnitarioItem, MontoItem
- ECF/FechaHoraFirma (requerido)
- ECF/(xs:any) → Signature placeholder con texto no vacío

Incluye:
- Normalización fechas (DD-MM-YYYY) y datetime (DD-MM-YYYY HH:MM:SS)
- Validación previa contra spec JSON (ecf32.json)
- Validaciones amigables de formato (eNCF, RNC, Teléfono, Email)
- Validación de catálogos (UnidadMedida, TipoMoneda, Provincia/Municipio) si disponibles
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
from .amount_utils import round_money_2, round_unit_price_4, to_str
from .tax_utils import compute_item_additional_taxes, aggregate_additional_taxes
from .business_rules import validate_montos_gravados_y_exentos_vs_indicador
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

# De la spec 32: IdDoc requiere TipoeCF, eNCF, TipoIngresos, TipoPago
REQUIRED_IDDOC_FIELDS = [
    "TipoeCF",
    "eNCF",
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

def build_ecf32_xml(data: Dict) -> str:
    # Validación previa contra spec (si existe)
    try:
        errs = validate_against_spec(data, spec_name="ecf32.json")
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
        # Normalizaciones: en 32 no es obligatorio FechaVencimientoSecuencia
        if key in ("FechaVencimientoSecuencia", "FechaLimitePago", "FechaDesde", "FechaHasta"):
            text_val = to_dmy(text_val)
        ET.SubElement(iddoc, key).text = escape_text(text_val)
    # Validaciones amigables
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
    # Validaciones de formato
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

    # Comprador (spec exige presencia del bloque)
    comprador_in = encabezado_in.get("Comprador", {})
    comprador = ET.SubElement(encabezado, "Comprador")
    # Si viene vacío, completar con Consumidor Final para evitar tag vacío rechazado por DGII
    rnc_c = comprador_in.get("RNCComprador")
    razon_c = comprador_in.get("RazonSocialComprador")
    if (rnc_c is None or str(rnc_c).strip() == "") and (razon_c is None or str(razon_c).strip() == ""):
        rnc_c = "000000000"
        razon_c = "CONSUMIDOR FINAL"
    add_text_if_not_empty(comprador, "RNCComprador", rnc_c)
    add_text_if_not_empty(comprador, "RazonSocialComprador", razon_c)
    if comprador_in.get("CorreoComprador"):
        validate_email(comprador_in.get("CorreoComprador"), field_name="CorreoComprador")
        add_text_if_not_empty(comprador, "CorreoComprador", comprador_in.get("CorreoComprador"))

    # Totales
    totales_in = encabezado_in.get("Totales", {})
    totales = ET.SubElement(encabezado, "Totales")
    monto_total = totales_in.get("MontoTotal")
    if monto_total is None or str(monto_total) == "":
        raise ValueError("Falta campo requerido en Totales: MontoTotal")
    add_text_if_not_empty(totales, "MontoExento", totales_in.get("MontoExento"))

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

    # Detalles
    detalles_in = data.get("detalles", {})
    items: List[Dict] = detalles_in.get("items", [])
    if not items:
        raise ValueError("Se requiere al menos un Item en DetallesItems")
    detalles_el = ET.SubElement(root, "DetallesItems")
    sum_items = Decimal("0")
    sum_items_otra_moneda = Decimal("0")
    items_taxes_acc: List[List[Tuple[str, Decimal, Decimal | None]]] = []
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
        try:
            sum_items += Decimal(str(it_in.get("MontoItem")))
        except (InvalidOperation, TypeError):
            raise ValueError("MontoItem inválido: debe ser número con hasta 2 decimales")
        add_text_if_not_empty(item_el, "DescripcionItem", it_in.get("DescripcionItem"))
        # En 32, el XSD no contempla UnidadMedida en Item; no lo incluimos
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

        # Impuesto adicional por ítem (si aplica)
        if it_in.get("TablaImpuestoAdicional"):
            tabla = it_in["TablaImpuestoAdicional"].get("ImpuestoAdicional") or []
            item_taxes = compute_item_additional_taxes(it_in.get("MontoItem"), tabla)
            if item_taxes:
                items_taxes_acc.append(item_taxes)

    # FechaHoraFirma
    fecha_firma = data.get("fecha_hora_firma")
    if not fecha_firma:
        raise ValueError("Falta campo requerido: fecha_hora_firma")
    ET.SubElement(root, "FechaHoraFirma").text = escape_text(to_dmy_hms(str(fecha_firma)))

    # xs:any
    ET.SubElement(root, "Signature").text = "-"

    # Agregación de impuestos adicionales a nivel de Totales (32 exige Tasa en cada ImpuestoAdicional)
    if items_taxes_acc:
        agg = aggregate_additional_taxes(items_taxes_acc)
        # Filtrar sólo los que tienen tasa para cumplir XSD 32
        agg_con_tasa = {k: v for k, v in agg.items() if v.get("tasa")}
        if agg_con_tasa:
            # Primero MontoImpuestoAdicional, luego ImpuestosAdicionales (orden XSD)
            total_imp = sum(Decimal(v["monto"]) for v in agg_con_tasa.values())
            ET.SubElement(totales, "MontoImpuestoAdicional").text = to_str(round_money_2(total_imp))
            impuestos = ET.SubElement(totales, "ImpuestosAdicionales")
            for codigo, info in agg_con_tasa.items():
                imp = ET.SubElement(impuestos, "ImpuestoAdicional")
                ET.SubElement(imp, "TipoImpuesto").text = codigo
                ET.SubElement(imp, "TasaImpuestoAdicional").text = info["tasa"]
                # Usamos OtrosImpuestosAdicionales para totalizar el monto por código
                ET.SubElement(imp, "OtrosImpuestosAdicionales").text = info["monto"]
    # MontoTotal al final de Totales, como exige el XSD
    ET.SubElement(totales, "MontoTotal").text = escape_text(str(monto_total))

    # Validaciones de negocio de montos gravados/exentos vs indicador facturación
    biz_errors = validate_montos_gravados_y_exentos_vs_indicador(totales_in, items)
    if biz_errors:
        raise ValueError("; ".join(biz_errors))

    # Coherencia de totales
    try:
        total = Decimal(to_str(round_money_2(monto_total)))
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

    # Preservar Comprador vacío (la spec exige su presencia en 32)
    remove_empty_elements(root, preserve={"Comprador"})

    return ET.tostring(root, encoding="utf-8").decode("utf-8")


def build_and_validate_ecf32(data: Dict) -> Tuple[str, bool, List[str]]:
    xml = build_ecf32_xml(data)
    ok, errors = validate_xml(xml, xsd_name="e-CF 32 v.1.0.xsd")
    return xml, ok, errors
