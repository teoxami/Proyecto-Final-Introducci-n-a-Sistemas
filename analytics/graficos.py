import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Estilo visual moderno y limpio
sns.set_theme(style="whitegrid")

class GeneradorAnalitica:
    def __init__(self, ruta_guardado="analytics/"):
        self.ruta_guardado = ruta_guardado
        os.makedirs(self.ruta_guardado, exist_ok=True)

    def generar_grafico_caducidades(self, df_inventario):
        """Genera gráfico de dona con la distribución de caducidades (SCM)."""
        if df_inventario is None or df_inventario.empty:
            print("⚠️ No hay datos de inventario para graficar.")
            return

        hoy = datetime.now()
        df = df_inventario.copy()
        df['fecha_caducidad_dt'] = pd.to_datetime(df['fecha_caducidad'], errors='coerce')
        
        limite_30 = hoy + pd.Timedelta(days=30)
        
        vencidos = len(df[df['fecha_caducidad_dt'] < hoy])
        por_vencer = len(df[(df['fecha_caducidad_dt'] >= hoy) & (df['fecha_caducidad_dt'] <= limite_30)])
        optimos = len(df[df['fecha_caducidad_dt'] > limite_30])
        
        etiquetas = ['Óptimos (>30 días)', 'Próximos a Vencer (<=30 días)', 'Caducados']
        cantidades = [optimos, por_vencer, vencidos]
        colores = ['#2ecc71', '#f39c12', '#e74c3c']
        
        fig, ax = plt.subplots(figsize=(7, 7))
        wedges, texts, autotexts = ax.pie(
            cantidades, 
            labels=etiquetas, 
            autopct='%1.1f%%', 
            colors=colores, 
            startangle=140, 
            pctdistance=0.75,
            explode=(0, 0.05, 0.08) if sum(cantidades) > 0 else (0, 0, 0)
        )
        
        # Convertir en gráfico de dona
        centre_circle = plt.Circle((0, 0), 0.50, fc='white')
        fig.gca().add_artist(centre_circle)
        
        plt.setp(autotexts, size=10, weight="bold", color="white")
        plt.title('SCM: Control de Caducidad en Inventario', fontsize=14, fontweight='bold', pad=20)
        
        ruta_archivo = os.path.join(self.ruta_guardado, "grafico_caducidades.png")
        plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"📊 [ANALYTICS] Gráfico guardado: {ruta_archivo}")

    def generar_grafico_finanzas(self, df_libros_contables, saldo_inicial=10000.0):
        """Genera un gráfico de línea mostrando la evolución de la Caja Chica (ERP)."""
        if df_libros_contables is None or df_libros_contables.empty:
            print("⚠️ No hay transacciones en el libro diario para graficar.")
            return

        df = df_libros_contables.copy()

        # 1. Calcular el saldo de caja resultante paso a paso
        df['monto_neto'] = df.apply(
            lambda row: float(row['monto']) if str(row['tipo']).strip().lower() == 'ingreso' else -float(row['monto']),
            axis=1
        )
        df['saldo_caja_resultante'] = saldo_inicial + df['monto_neto'].cumsum()

        # 2. Extraer el ID de Factura (#F-XXXXX) desde la descripción o columnas existentes
        def obtener_etiqueta_eje_x(row):
            desc = str(row.get('descripcion', ''))
            match = pd.Series(desc).str.extract(r'(F-\d+)', expand=False).iloc[0]
            if pd.notnull(match):
                return f"Fact. #{match}"
            elif 'id_factura' in row and pd.notnull(row['id_factura']):
                return f"Fact. #{row['id_factura']}"
            elif 'fecha' in row and pd.notnull(row['fecha']):
                return str(row['fecha']).split(' ')[-1]
            else:
                return f"Mov. #{row.name + 1}"

        eje_x = df.apply(obtener_etiqueta_eje_x, axis=1)

        # 3. Graficar con las etiquetas reales de Factura
        plt.figure(figsize=(10, 5))
        plt.plot(
            eje_x, 
            df['saldo_caja_resultante'], 
            marker='o', 
            color='#2980b9', 
            linewidth=2.5, 
            markersize=8
        )
        
        plt.title('ERP: Flujo de Caja en Tiempo Real', fontsize=14, fontweight='bold', pad=15)
        plt.xlabel('Factura / Movimiento Contable', fontsize=11)
        plt.ylabel('Saldo Disponible ($)', fontsize=11)
        plt.xticks(rotation=25, ha='right')
        plt.grid(True, linestyle='--', alpha=0.6)
        
        ruta_archivo = os.path.join(self.ruta_guardado, "grafico_flujo_caja.png")
        plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"📊 [ANALYTICS] Gráfico guardado: {ruta_archivo}")