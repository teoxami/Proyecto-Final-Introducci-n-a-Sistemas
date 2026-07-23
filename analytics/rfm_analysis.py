import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

sns.set_theme(style="whitegrid")

class AnalisisRFM:
    def __init__(self, ruta_pacientes="data/pacientes.csv", ruta_guardado="analytics/"):
        self.ruta_pacientes = ruta_pacientes
        self.ruta_guardado = ruta_guardado
        os.makedirs(self.ruta_guardado, exist_ok=True)

    def ejecutar_analisis_rfm(self):
        """Procesa los datos de pacientes y genera el mapa de segmentación RFM."""
        try:
            df = pd.read_csv(self.ruta_pacientes)
            df['ultima_compra'] = pd.to_datetime(df['ultima_compra'])
            hoy = datetime.now()
            
            # Cálculo de Recencia (días desde la última compra)
            df['Recencia_Dias'] = (hoy - df['ultima_compra']).dt.days
            df['Frecuencia'] = df['total_compras']

            # Clasificación de Segmentos basada en reglas de negocio
            def clasificar_paciente(row):
                if row['Recencia_Dias'] <= 30 and row['Frecuencia'] >= 3:
                    return 'VIP / Leal'
                elif row['Recencia_Dias'] <= 30 and row['Frecuencia'] < 3:
                    return 'Nuevo / Ocasional'
                elif 30 < row['Recencia_Dias'] <= 60:
                    return 'En Riesgo de Abandono'
                else:
                    return 'Tratamiento Abandonado'

            df['Segmento_RFM'] = df.apply(clasificar_paciente, axis=1)

            # Generar gráfico visual de la segmentación RFM
            self._generar_grafico_rfm(df)
            
            return df[['id_paciente', 'nombre_paciente', 'Recencia_Dias', 'Frecuencia', 'Segmento_RFM']]

        except Exception as e:
            print(f"❌ Error en Análisis RFM: {e}")
            return pd.DataFrame()

    def _generar_grafico_rfm(self, df):
        """Crea un gráfico de barras con el conteo de pacientes por segmento."""
        plt.figure(figsize=(9, 5))
        conteo = df['Segmento_RFM'].value_counts()
        colores = {'VIP / Leal': '#2ecc71', 'Nuevo / Ocasional': '#3498db', 
                   'En Riesgo de Abandono': '#f39c12', 'Tratamiento Abandonado': '#e74c3c'}
        
        ax = sns.barplot(x=conteo.index, y=conteo.values, palette=colores)
        plt.title('CRM: Segmentación RFM de Pacientes', fontsize=14, fontweight='bold', pad=15)
        plt.xlabel('Segmento de Paciente', fontsize=11)
        plt.ylabel('Cantidad de Pacientes', fontsize=11)
        plt.xticks(rotation=15)

        # Añadir etiquetas de valor sobre las barras
        for p in ax.patches:
            ax.annotate(f'{int(p.get_height())}', 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha='center', va='center', xytext=(0, 5), 
                        textcoords='offset points', fontweight='bold')

        ruta_archivo = os.path.join(self.ruta_guardado, "grafico_rfm_pacientes.png")
        plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"📊 [RFM ANALYTICS] Gráfico guardado: {ruta_archivo}")