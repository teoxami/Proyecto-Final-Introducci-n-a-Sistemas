import os
import pandas as pd
from datetime import datetime

# Definir la ruta base absoluta para evitar que se guarde en carpetas incorrectas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_FACTURAS_DEF = os.path.join(BASE_DIR, "data", "facturas.csv")

class SistemaCorePOS:
    def __init__(self, modulo_scm, modulo_erp, modulo_crm, ruta_csv=RUTA_FACTURAS_DEF):
        self.scm = modulo_scm
        self.erp = modulo_erp
        self.crm = modulo_crm
        self.ruta_csv = ruta_csv
        self.historial_ventas = []

        # Asegurar directorio
        os.makedirs(os.path.dirname(self.ruta_csv), exist_ok=True)

        # Cargar historial si ya existe
        if os.path.exists(self.ruta_csv) and os.path.getsize(self.ruta_csv) > 0:
            try:
                df_existente = pd.read_csv(self.ruta_csv)
                self.historial_ventas = df_existente.to_dict('records')
            except Exception as e:
                print(f"[CORE POS] Error al leer {self.ruta_csv}: {e}")
                self.historial_ventas = []
        else:
            # Crear CSV con encabezados si no existe
            df_vacio = pd.DataFrame(columns=[
                "factura", "barcode", "producto", "cantidad", "total", "paciente", "fecha"
            ])
            df_vacio.to_csv(self.ruta_csv, index=False)

    def procesar_dispensacion(self, id_factura, barcode, cantidad, id_paciente=None, nombre_paciente=None):
        print(f"\n[CORE POS] Procesando dispensación - Factura #{id_factura}...")

        # 1. Normalizar código de barras ingresado
        barcode_str = str(barcode).split('.')[0].strip()

        # 2. Buscar coincidencia exacta en el SCM
        df_inv = self.scm.df_inventario.copy()
        df_inv['barcode_clean'] = df_inv['barcode'].astype(str).str.split('.').str[0].str.strip()

        coincidencias = df_inv[df_inv['barcode_clean'] == barcode_str]

        if coincidencias.empty:
            print(f"[CORE POS ERROR] Producto con código '{barcode_str}' no encontrado en el inventario.")
            return False

        fila_prod = coincidencias.iloc[0]
        nombre_prod = fila_prod['name']
        precio_unitario = float(fila_prod['precio_unitario'])
        stock_disponible = int(fila_prod['stock_actual'])

        # 3. Validar Stock disponible
        if stock_disponible <= 0:
            print(f"[CORE POS ERROR] No hay stock disponible para '{nombre_prod}' (Stock actual: {stock_disponible}). Venta CANCELADA.")
            return False

        if cantidad > stock_disponible:
            print(f"[CORE POS ADVERTENCIA] Stock insuficiente para '{nombre_prod}'. Solicitado: {cantidad} | Disponible: {stock_disponible}. Venta CANCELADA.")
            return False

        # 4. Calcular Total
        total_venta = precio_unitario * cantidad
        print(f"Producto: {nombre_prod} | Cantidad: {cantidad} | Total: ${total_venta:.2f}")

        # 5. Ejecutar eventos inter-módulos
        self.scm.evaluar_y_reabastecer(barcode_str, cantidad)
        self.erp.registrar_asiento_ingreso(id_factura, total_venta, f"Dispensación de {nombre_prod} (x{cantidad})")

        if id_paciente:
            self.crm.actualizar_interaccion_paciente(id_paciente, nombre_nuevo=nombre_paciente)

        # 6. REGISTRAR Y GUARDAR EN FACTURAS.CSV
        registro = {
            "factura": str(id_factura),
            "barcode": barcode_str,
            "producto": nombre_prod,
            "cantidad": cantidad,
            "total": round(total_venta, 2),
            "paciente": str(id_paciente) if id_paciente else "Consumidor Final",
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.historial_ventas.append(registro)

        # Escribir DataFrame a disco de forma inmediata
        df_facturas = pd.DataFrame(self.historial_ventas)
        df_facturas.to_csv(self.ruta_csv, index=False)

        print(f"[CORE POS] Transacción #{id_factura} completada exitosamente.")
        print(f"[PERSISTENCIA] Factura guardada en: {self.ruta_csv} (Total guardadas: {len(self.historial_ventas)})\n")
        return True