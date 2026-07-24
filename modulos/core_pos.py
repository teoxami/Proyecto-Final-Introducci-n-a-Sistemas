import os
import pandas as pd
from datetime import datetime

class SistemaCorePOS:
    def __init__(self, modulo_scm, modulo_erp, modulo_crm, ruta_csv="data/facturas.csv"):
        """
        Recibe las instancias de los 3 módulos satélites para orquestar la integración
        y maneja la persistencia de ventas en un archivo CSV.
        """
        self.scm = modulo_scm
        self.erp = modulo_erp
        self.crm = modulo_crm
        self.ruta_csv = ruta_csv
        self.historial_ventas = []

        # Asegurar que exista la carpeta 'data/'
        os.makedirs(os.path.dirname(self.ruta_csv), exist_ok=True)

        # 1. Si el archivo CSV NO existe, crearlo vacío con sus encabezados
        if not os.path.exists(self.ruta_csv):
            df_vacio = pd.DataFrame(columns=[
                "factura", "barcode", "producto", "cantidad", "total", "paciente", "fecha"
            ])
            df_vacio.to_csv(self.ruta_csv, index=False)
        else:
            # 2. Si ya existe, cargar el historial existente
            try:
                df_existente = pd.read_csv(self.ruta_csv)
                self.historial_ventas = df_existente.to_dict('records')
            except Exception:
                self.historial_ventas = []

    def procesar_dispensacion(self, id_factura, barcode, cantidad, id_paciente=None, nombre_paciente=None):
        """
        Método Principal del Core POS: Valida stock disponible, simula/registra la venta, 
        desencadena la comunicación inter-módulos y guarda la transacción en el CSV.
        """
        print(f"\n🛒 [CORE POS] Procesando dispensación - Factura #{id_factura}...")

        # Formatear el código de barras ingresado para evitar imprecisiones
        barcode_str = str(barcode).split('.')[0].strip()

        # Normalizar el código de barras en el DataFrame actual de SCM
        self.scm.df_inventario['barcode_clean'] = self.scm.df_inventario['barcode'].astype(str).str.split('.').str[0].str.strip()

        idx = self.scm.df_inventario[self.scm.df_inventario['barcode_clean'] == barcode_str].index

        if idx.empty:
            print(f"❌ [CORE POS ERROR] Producto con código '{barcode}' no encontrado en el inventario.")
            return False

        # Obtener los datos más recientes directamente desde SCM
        fila_prod = self.scm.df_inventario.loc[idx[0]]
        nombre_prod = fila_prod['name']
        precio_unitario = float(fila_prod['precio_unitario'])
        stock_disponible = int(fila_prod['stock_actual'])

        # --- 🚨 VALIDACIÓN CRÍTICA DE STOCK EN TIEMPO REAL ---
        if stock_disponible <= 0:
            print(f"🚫 [CORE POS ERROR] No hay stock disponible para '{nombre_prod}' (Stock actual: {stock_disponible}). Venta CANCELADA.")
            return False

        if cantidad > stock_disponible:
            print(f"⚠️ [CORE POS ADVERTENCIA] Stock insuficiente para '{nombre_prod}'. Solicitado: {cantidad} | Disponible: {stock_disponible}. Venta CANCELADA.")
            return False

        # Si supera la validación de stock, calcula el total
        total_venta = precio_unitario * cantidad
        print(f"  📌 Producto: {nombre_prod} | Cantidad: {cantidad} | Total: ${total_venta:.2f}")

        # --- EVENTOS INTER-MÓDULOS ---
        # 1. SCM: Descontar stock y reabastecer si queda por debajo del umbral mínimo
        self.scm.evaluar_y_reabastecer(barcode, cantidad)

        # 2. ERP: Registrar ingreso y asiento en Libro Diario
        self.erp.registrar_asiento_ingreso(
            id_factura=id_factura,
            monto=total_venta,
            descripcion=f"Dispensación de {nombre_prod} (x{cantidad})"
        )

        # 3. CRM: Actualizar o crear interacción del paciente
        if id_paciente:
            self.crm.actualizar_interaccion_paciente(id_paciente, nombre_nuevo=nombre_paciente)

        # --- PERSISTENCIA DE DATOS ---
        registro = {
            "factura": str(id_factura),
            "barcode": barcode_str,
            "producto": nombre_prod,
            "cantidad": cantidad,
            "total": round(total_venta, 2),
            "paciente": id_paciente if id_paciente else "Consumidor Final",
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.historial_ventas.append(registro)

        # Guardar inmediatamente en disco
        df_facturas = pd.DataFrame(self.historial_ventas)
        df_facturas.to_csv(self.ruta_csv, index=False)

        print(f"✅ [CORE POS] Transacción #{id_factura} completada exitosamente.")
        print(f"💾 [PERSISTENCIA] Factura registrada en '{self.ruta_csv}'.\n")
        return True