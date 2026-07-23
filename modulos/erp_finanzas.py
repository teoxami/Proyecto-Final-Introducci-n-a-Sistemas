from datetime import datetime
import pandas as pd

class ModuloERP:
    def __init__(self, saldo_inicial=5000.0):
        self.caja_chica = saldo_inicial
        self.libros_contables = []

    def registrar_asiento_ingreso(self, id_factura, monto, descripcion="Venta de Medicamentos"):
        """
        Disparador ERP: Se ejecuta automáticamente al realizar una venta en el Core POS.
        Aumenta el flujo de caja y registra el haber.
        """
        self.caja_chica += monto
        asiento = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "id_factura": id_factura,
            "tipo": "INGRESO",
            "descripcion": descripcion,
            "monto": monto,
            "saldo_caja_resultante": self.caja_chica
        }
        self.libros_contables.append(asiento)
        print(f"  💵 [ERP CONTABILIDAD] Asiento registrado para Factura #{id_factura}. +${monto:.2f} | Caja Actual: ${self.caja_chica:.2f}")

    def registrar_asiento_merma(self, nombre_producto, monto_perdida):
        """
        Registra el egreso/pérdida contable por medicamentos caducados retirados.
        """
        self.caja_chica -= monto_perdida
        asiento = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "id_factura": "N/A (MERMA)",
            "tipo": "EGRESO / PERDIDA",
            "descripcion": f"Retiro por Caducidad: {nombre_producto}",
            "monto": -monto_perdida,
            "saldo_caja_resultante": self.caja_chica
        }
        self.libros_contables.append(asiento)
        print(f"  📉 [ERP CONTABILIDAD] Pérdida por caducidad registrada: {nombre_producto} (-${monto_perdida:.2f})")

    def obtener_resumen_financiero(self):
        """Genera un DataFrame con el libro diario contable."""
        return pd.DataFrame(self.libros_contables)