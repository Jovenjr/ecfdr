import frappe
from frappe.model.document import Document


class DigitalCertificate(Document):
    def validate(self):
        """Validaciones mínimas para uso en firma e-CF.

        - Si el certificado está activo, debe proveer ruta PKCS#12 (p12_path/cert_path/file_path)
        - Solo puede existir un certificado activo a la vez
        """
        # Detectar bandera de activo en distintos esquemas de campos
        is_active = getattr(self, "is_active", None)
        active = getattr(self, "active", None)
        activo = is_active if is_active is not None else (active if active is not None else 0)

        # Resolver ruta PKCS#12 desde campos posibles
        p12_path = (
            getattr(self, "p12_path", None)
            or getattr(self, "cert_path", None)
            or getattr(self, "file_path", None)
        )

        if activo and not p12_path:
            frappe.throw("Debe definir la ruta del certificado PKCS#12 (p12_path) para activar el certificado.")

        # Enforce singleton active certificate si no es Single
        if activo:
            try:
                others = frappe.get_all(
                    "Digital Certificate",
                    filters={"name": ["!=", self.name], "is_active": 1},
                    pluck="name",
                    limit=1,
                )
                if not others:
                    others = frappe.get_all(
                        "Digital Certificate",
                        filters={"name": ["!=", self.name], "active": 1},
                        pluck="name",
                        limit=1,
                    )
                if others:
                    frappe.throw(
                        "Ya existe otro 'Digital Certificate' activo. Solo uno puede estar activo a la vez."
                    )
            except Exception:
                # Si la tabla no existe o estamos fuera de contexto de sitio, omitir
                pass
