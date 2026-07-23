import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def preparar_datos_base():
    print("⏳ Cargando 'global_test_set.csv'...")
    try:
        df = pd.read_csv("data/global_test_set.csv")
    except FileNotFoundError:
        print("❌ Error: No se encontró 'data/global_test_set.csv'. Verifica la ruta.")
        return

    # Limpiar columnas principales
    df['barcode'] = df['barcode'].astype(str)
    
    # -------------------------------------------------------------
    # 1. CREACIÓN DE INVENTARIO Y LOTES (SCM / Caducidades)
    # -------------------------------------------------------------
    print("📦 Generando 'data/inventario_lotes.csv'...")
    
    # Extraer catálogo de productos únicos por código de barras
    productos_unicos = df[['barcode', 'name', 'dosage_form', 'type']].drop_duplicates(subset=['barcode']).copy()
    
    # Generar precios, stock y fechas de caducidad aleatorias pero realistas
    np.random.seed(42) # Semilla para consistencia de datos
    n_productos = len(productos_unicos)
    
    # Precios simulados entre $1.50 y $45.00
    productos_unicos['precio_unitario'] = np.round(np.random.uniform(1.50, 45.00, size=n_productos), 2)
    # Stock disponible actual
    productos_unicos['stock_actual'] = np.random.randint(1, 50, size=n_productos)
    # Stock mínimo para alerta de reposición SCM
    productos_unicos['stock_minimo'] = 5
    
    # Generar Fechas de Caducidad (7 opciones = 7 probabilidades ajustadas)
    hoy = datetime.now()
    dias_vencimiento = np.random.choice(
        [-15, 10, 25, 60, 180, 365, 720], # 7 opciones de días
        size=n_productos,
        p=[0.05, 0.10, 0.15, 0.20, 0.20, 0.15, 0.15] # 7 probabilidades que suman 1.0
    )
    
    fechas_caducidad = [(hoy + timedelta(days=int(d))).strftime('%Y-%m-%d') for d in dias_vencimiento]
    productos_unicos['fecha_caducidad'] = fechas_caducidad
    productos_unicos['lote'] = [f"LOTE-2024-{i+1000}" for i in range(n_productos)]
    
    # Guardar en data/inventario_lotes.csv
    productos_unicos.to_csv("data/inventario_lotes.csv", index=False)
    print(f"✅ 'data/inventario_lotes.csv' generado con {n_productos} productos e información de vencimiento.")

    # -------------------------------------------------------------
    # 2. CREACIÓN DE PACIENTES RECURRENTES DIVERSIFICADOS (CRM / RFM)
    # -------------------------------------------------------------
    print("👥 Generando 'data/pacientes.csv' con distribución RFM equilibrada...")
    
    n_pacientes = 500
    pacientes_ids = [f"PAC-{i+1000}" for i in range(n_pacientes)]
    
    nombres = ["Carlos", "María", "Juan", "Ana", "Luis", "Elena", "Pedro", "Sofía", "Diego", "Lucía"]
    apellidos = ["Gómez", "Pérez", "Rodríguez", "López", "Martínez", "García", "Fernández", "Torres"]
    
    lista_pacientes = []
    
    for id_pac in pacientes_ids:
        nombre_completo = f"{np.random.choice(nombres)} {np.random.choice(apellidos)}"
        
        # Distribución intencional de la última compra para balancear el gráfico RFM:
        # 30% Compraron recientemente (0 a 14 días atrás) -> VIP / Leales
        # 35% Compraron hace un mes (15 a 45 días atrás)  -> En Riesgo
        # 35% Compraron hace mucho (46 a 180 días atrás) -> Abandono
        r = np.random.rand()
        if r < 0.30:
            dias_atras = np.random.randint(0, 15)
            compras = np.random.randint(5, 12)  # Frecuencia alta
        elif r < 0.65:
            dias_atras = np.random.randint(15, 45)
            compras = np.random.randint(2, 6)   # Frecuencia media
        else:
            dias_atras = np.random.randint(46, 180)
            compras = np.random.randint(1, 3)   # Frecuencia baja

        fecha_compra = (hoy - timedelta(days=dias_atras)).strftime('%Y-%m-%d %H:%M:%S')
        
        lista_pacientes.append({
            "id_paciente": id_pac,
            "nombre_paciente": nombre_completo,
            "ultima_compra": fecha_compra,
            "total_compras": compras
        })
    
    pacientes_resumen = pd.DataFrame(lista_pacientes)
    
    # Guardar en data/pacientes.csv
    pacientes_resumen.to_csv("data/pacientes.csv", index=False)
    print(f"✅ 'data/pacientes.csv' generado con {len(pacientes_resumen)} registros balanceados.\n")
    print("🎉 ¡Proceso completado! Archivos auxiliares listos.")

if __name__ == "__main__":
    preparar_datos_base()