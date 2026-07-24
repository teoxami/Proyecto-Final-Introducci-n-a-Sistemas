import os
import pandas as pd
from datetime import datetime


class ModuloERP:
    def __init__(self, ruta_libros="data/libro_diario.csv", saldo_inicial=10000.0):
        self.ruta_libros = ruta_libros
        self.saldo_inicial = saldo_inicial
        self.cargar_libro_diario()

    def cargar_libro_diario(self):
        """Carga el historial financiero desde el disco o crea uno nuevo."""
        if os.path.exists(self.ruta_libros) and os.path.getsize(self.ruta_libros) > 0:
            try:
                self.df_libros = pd.read_csv(self.ruta_libros)
                ingresos = self.df_libros[self.df_libros['tipo'] == 'Ingreso']['monto'].sum()
                egresos = self.df_libros[self.df_libros['tipo'] == 'Egreso']['monto'].sum()
                self.caja_chica = self.saldo_inicial + ingresos - egresos
            except Exception as e:
                print(f"Error al cargar libro diario: {e}")
                self._inicializar_vacio()
        else:
            self._inicializar_vacio()

    def _inicializar_vacio(self):
        """Inicializa la estructura si no existe el archivo CSV."""
        self.caja_chica = self.saldo_inicial
        self.df_libros = pd.DataFrame(columns=['fecha', 'monto', 'tipo', 'descripcion'])
        self.guardar_libro_diario()

    def registrar_transaccion(self, monto, tipo, descripcion):
        """Registra un ingreso/egreso y actualiza el saldo."""
        fecha_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if tipo.lower() == 'ingreso':
            self.caja_chica += monto
            tipo_label = 'Ingreso'
        else:
            self.caja_chica -= monto
            tipo_label = 'Egreso'

        nueva_fila = {
            'fecha': fecha_str,
            'monto': float(monto),
            'tipo': tipo_label,
            'descripcion': descripcion
        }
        
        self.df_libros = pd.concat([self.df_libros, pd.DataFrame([nueva_fila])], ignore_index=True)
        self.guardar_libro_diario()

    def registrar_asiento_ingreso(self, id_factura, monto, descripcion):
        """Registra un asiento de ingreso por ventas desde el módulo POS."""
        desc_completa = f"Factura #{id_factura}: {descripcion}"
        self.registrar_transaccion(monto, 'Ingreso', desc_completa)

    def registrar_asiento_merma(self, nombre_producto, monto):
        """Registra un asiento de egreso/pérdida por producto vencido/retirado."""
        self.registrar_transaccion(monto, 'Egreso', f"Merma/Baja de producto: {nombre_producto}")

    def obtener_resumen_financiero(self):
        """Devuelve el DataFrame completo del libro diario."""
        self.cargar_libro_diario()
        return self.df_libros

    def guardar_libro_diario(self):
        """Guarda las transacciones acumuladas en el archivo CSV."""
        os.makedirs(os.path.dirname(self.ruta_libros), exist_ok=True)
        self.df_libros.to_csv(self.ruta_libros, index=False)