import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os

class DashboardGerencial:
    def __init__(self, ruta_analytics="analytics/"):
        self.ruta_analytics = ruta_analytics

    def compilar_dashboard(self):
        """Unifica los gráficos individuales en un único Dashboard Gerencial (2x2)."""
        fig, axs = plt.subplots(2, 2, figsize=(16, 11))
        fig.suptitle('🏥 DASHBOARD INTEGRADO DE GESTIÓN FARMACÉUTICA Y SALUD', fontsize=18, fontweight='bold', y=0.98)

        graficos = [
            ("grafico_caducidades.png", "1. SCM: Estado de Caducidades", (0, 0)),
            ("grafico_flujo_caja.png", "2. ERP: Flujo de Caja en Tiempo Real", (0, 1)),
            ("grafico_rfm_pacientes.png", "3. CRM: Segmentación RFM de Pacientes", (1, 0)),
        ]

        for img_name, titulo, pos in graficos:
            path = os.path.join(self.ruta_analytics, img_name)
            if os.path.exists(path):
                img = mpimg.imread(path)
                axs[pos[0], pos[1]].imshow(img)
                axs[pos[0], pos[1]].axis('off')
            else:
                axs[pos[0], pos[1]].text(0.5, 0.5, f"Gráfico no encontrado:\n{img_name}", 
                                         ha='center', va='center', fontsize=12)
                axs[pos[0], pos[1]].axis('off')

        # Cuadrante 4: Resumen Ejecutivo / Métricas Clave (KPIs)
        ax_kpi = axs[1, 1]
        ax_kpi.axis('off')
        
        texto_kpi = (
            "📌 RESUMEN EJECUTIVO (KPIs)\n"
            "───────────────────────────────\n"
            "• Módulo SCM: Alertas automatizadas por caducidad y stock.\n"
            "• Módulo ERP: Contabilidad y caja actualizada en tiempo real.\n"
            "• Módulo CRM: Control de deserción de tratamiento mediante RFM.\n"
            "• Core POS: Orquestación inter-módulos en cada venta.\n\n"
            "✅ Sistema Operativo y Validado para Presentación."
        )
        
        ax_kpi.text(0.1, 0.5, texto_kpi, fontsize=13, verticalalignment='center',
                    bbox=dict(boxstyle='round,pad=1', facecolor='#ebf5fb', edgecolor='#2980b9', alpha=0.9))

        plt.tight_layout()
        ruta_final = os.path.join(self.ruta_analytics, "dashboard_gerencial.png")
        plt.savefig(ruta_final, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"🚀 [DASHBOARD] Panel Gerencial Consolidado guardado en: {ruta_final}")