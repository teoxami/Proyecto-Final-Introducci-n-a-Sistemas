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
        hoy = datetime.now()
        df = df_inventario.copy()
        df['fecha_caducidad_dt'] = pd.to_datetime(df['fecha_caducidad'])
        
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
            explode=(0, 0.05, 0.08)
        )
        
        # Convertir en gráfico de dona para un look más moderno
        centre_circle = plt.Circle((0,0),0.50,fc='white')
        fig.gca().add_artist(centre_circle)
        
        plt.setp(autotexts, size=10, weight="bold", color="white")
        plt.title('SCM: Control de Caducidad en Inventario', fontsize=14, fontweight='bold', pad=20)
        
        ruta_archivo = os.path.join(self.ruta_guardado, "grafico_caducidades.png")
        plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"📊 [ANALYTICS] Gráfico guardado: {ruta_archivo}")

    def generar_grafico_finanzas(self, df_libros_contables):
        """Genera un gráfico de línea mostrando la evolución de la Caja Chica (ERP)."""
        if df_libros_contables.empty:
            return
            
        plt.figure(figsize=(9, 5))
        plt.plot(
            df_libros_contables['id_factura'].astype(str), 
            df_libros_contables['saldo_caja_resultante'], 
            marker='o', 
            color='#2980b9', 
            linewidth=2.5, 
            markersize=8
        )
        
        plt.title('ERP: Flujo de Caja en Tiempo Real', fontsize=14, fontweight='bold', pad=15)
        plt.xlabel('Transacción / Movimiento Contable', fontsize=11)
        plt.ylabel('Saldo Disponible ($)', fontsize=11)
        plt.xticks(rotation=15)
        plt.grid(True, linestyle='--', alpha=0.6)
        
        ruta_archivo = os.path.join(self.ruta_guardado, "grafico_flujo_caja.png")
        plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"📊 [ANALYTICS] Gráfico guardado: {ruta_archivo}")