import pandas as pd
from datetime import datetime

class ModuloSCM:
    def __init__(self, ruta_inventario="data/inventario_lotes.csv"):
        self.ruta_inventario = ruta_inventario
        self.ordenes_compra = []
        self.cargar_inventario()

    def cargar_inventario(self):
        """Carga el inventario desde el archivo CSV."""
        try:
            self.df_inventario = pd.read_csv(self.ruta_inventario)
            self.df_inventario['barcode'] = self.df_inventario['barcode'].astype(str)
        except Exception as e:
            print(f"❌ Error al cargar inventario SCM: {e}")

    def guardar_inventario(self):
        """Guarda las actualizaciones del inventario en el CSV."""
        self.df_inventario.to_csv(self.ruta_inventario, index=False)

    def verificar_caducidades(self, dias_umbral=30):
        """Retorna productos caducados y próximos a caducar."""
        hoy = datetime.now()
        self.df_inventario['fecha_caducidad_dt'] = pd.to_datetime(self.df_inventario['fecha_caducidad'])
        
        # Filtrar medicamentos vencidos
        vencidos = self.df_inventario[self.df_inventario['fecha_caducidad_dt'] < hoy]
        
        # Filtrar medicamentos próximos a vencer (en menos de 'dias_umbral')
        limite = hoy + pd.Timedelta(days=dias_umbral)
        por_vencer = self.df_inventario[
            (self.df_inventario['fecha_caducidad_dt'] >= hoy) & 
            (self.df_inventario['fecha_caducidad_dt'] <= limite)
        ]
        
        return vencidos, por_vencer

    def evaluar_y_reabastecer(self, barcode, cantidad_vendida):
        """
        Disparador SCM: Reduce stock tras venta y genera orden de compra
        automática si el stock cae por debajo del mínimo.
        """
        idx = self.df_inventario[self.df_inventario['barcode'] == str(barcode)].index
        if not idx.empty:
            i = idx[0]
            stock_actual = self.df_inventario.loc[i, 'stock_actual'] - cantidad_vendida
            self.df_inventario.loc[i, 'stock_actual'] = max(0, stock_actual)
            stock_minimo = self.df_inventario.loc[i, 'stock_minimo']
            nombre = self.df_inventario.loc[i, 'name']

            # Desencadenante automático de Orden de Compra
            if stock_actual <= stock_minimo:
                orden = {
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "barcode": barcode,
                    "producto": nombre,
                    "cantidad_reorden": 20,
                    "estado": "Generada Automáticamente"
                }
                self.ordenes_compra.append(orden)
                print(f"  📦 [SCM ALERTA] Stock bajo de '{nombre}' ({stock_actual} un.). ¡Orden de compra generada automáticamente!")
            
            self.guardar_inventario()
            return True
        return False