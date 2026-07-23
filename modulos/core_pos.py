import pandas as pd
from datetime import datetime

class SistemaCorePOS:
    def __init__(self, modulo_scm, modulo_erp, modulo_crm):
        """
        Recibe las instancias de los 3 módulos satélites para orquestar la integración.
        """
        self.scm = modulo_scm
        self.erp = modulo_erp
        self.crm = modulo_crm
        self.historial_ventas = []

    def procesar_dispensacion(self, id_factura, barcode, cantidad, id_paciente=None):
        """
        Método Principal del Core POS: Simula la venta y desencadena la comunicación inter-módulos.
        """
        print(f"\n🛒 [CORE POS] Procesando dispensación - Factura #{id_factura}...")

        # 1. Buscar producto en el inventario de SCM
        df_inv = self.scm.df_inventario
        producto = df_inv[df_inv['barcode'] == str(barcode)]

        if producto.empty:
            print(f"❌ [CORE POS ERROR] Producto con código {barcode} no encontrado.")
            return False

        nombre_prod = producto.iloc[0]['name']
        precio_unitario = producto.iloc[0]['precio_unitario']
        total_venta = precio_unitario * cantidad

        print(f"  📌 Producto: {nombre_prod} | Cantidad: {cantidad} | Total: ${total_venta:.2f}")

        # 2. Evento SCM: Actualizar stock y verificar reabastecimiento automático
        self.scm.evaluar_y_reabastecer(barcode, cantidad)

        # 3. Evento ERP: Registrar el ingreso de dinero y asiento contable
        self.erp.registrar_asiento_ingreso(
            id_factura=id_factura,
            monto=total_venta,
            descripcion=f"Dispensación de {nombre_prod} (x{cantidad})"
        )

        # 4. Evento CRM: Si hay paciente asociado, actualizar su tratamiento
        if id_paciente:
            self.crm.actualizar_interaccion_paciente(id_paciente)

        # Guardar en el historial de transacciones en memoria
        self.historial_ventas.append({
            "factura": id_factura,
            "barcode": barcode,
            "producto": nombre_prod,
            "cantidad": cantidad,
            "total": total_venta,
            "paciente": id_paciente,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        print(f"✅ [CORE POS] Transacción #{id_factura} completada exitosamente.\n")
        return True