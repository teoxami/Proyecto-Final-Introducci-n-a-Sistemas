import pandas as pd
from datetime import datetime

class ModuloSCM:
    def __init__(self, ruta_inventario="data/inventario_lotes.csv"):
        self.ruta_inventario = ruta_inventario
        self.ordenes_compra = []
        self.cargar_inventario()

    def cargar_inventario(self):
        """Carga el inventario asegurando que el código de barras sea string sin flotantes."""
        try:
            self.df_inventario = pd.read_csv(self.ruta_inventario)
            self.df_inventario['barcode'] = self.df_inventario['barcode'].astype(str).str.split('.').str[0].str.strip()
        except Exception as e:
            print(f"❌ Error al cargar inventario SCM: {e}")

    def guardar_inventario(self):
        """Guarda el inventario eliminando columnas temporales de cálculo."""
        df_a_guardar = self.df_inventario.copy()
        if 'barcode_clean' in df_a_guardar.columns:
            df_a_guardar = df_a_guardar.drop(columns=['barcode_clean'])
        if 'fecha_caducidad_dt' in df_a_guardar.columns:
            df_a_guardar = df_a_guardar.drop(columns=['fecha_caducidad_dt'])
            
        df_a_guardar.to_csv(self.ruta_inventario, index=False)

    def verificar_caducidades(self, dias_umbral=30):
        hoy = datetime.now()
        self.df_inventario['fecha_caducidad_dt'] = pd.to_datetime(self.df_inventario['fecha_caducidad'])
        
        vencidos = self.df_inventario[self.df_inventario['fecha_caducidad_dt'] < hoy]
        limite = hoy + pd.Timedelta(days=dias_umbral)
        por_vencer = self.df_inventario[
            (self.df_inventario['fecha_caducidad_dt'] >= hoy) & 
            (self.df_inventario['fecha_caducidad_dt'] <= limite)
        ]
        
        return vencidos, por_vencer

    def evaluar_y_reabastecer(self, barcode, cantidad_vendida):
        barcode_str = str(barcode).split('.')[0].strip()
        idx = self.df_inventario[self.df_inventario['barcode'] == barcode_str].index
        
        if not idx.empty:
            i = idx[0]
            stock_actual = self.df_inventario.loc[i, 'stock_actual'] - cantidad_vendida
            self.df_inventario.loc[i, 'stock_actual'] = max(0, stock_actual)
            stock_minimo = self.df_inventario.loc[i, 'stock_minimo']
            nombre = self.df_inventario.loc[i, 'name']

            if stock_actual <= stock_minimo:
                orden = {
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "barcode": barcode_str,
                    "producto": nombre,
                    "cantidad_reorden": 20,
                    "estado": "Generada Automáticamente"
                }
                self.ordenes_compra.append(orden)
                print(f"[SCM ALERTA] Stock bajo de '{nombre}' ({stock_actual} un.). ¡Orden generada!")
            
            self.guardar_inventario()
            return True
        return False