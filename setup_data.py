import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def limpiar_barcode(val):
    """Convierte notación científica (ej. 8.90425E+12) o flotantes a string de entero limpio."""
    if pd.isna(val):
        return ""
    val_str = str(val).strip()
    try:
        num = float(val_str)
        return f"{int(num):d}"
    except (ValueError, OverflowError):
        return val_str

def preparar_datos_base():
    print("⏳ Cargando 'data/global_test_set.csv'...")
    try:
        df = pd.read_csv("data/global_test_set.csv")
    except FileNotFoundError:
        print("❌ Error: No se encontró 'data/global_test_set.csv'. Verifica la ruta.")
        return

    # 1. Limpieza correcta de Barcodes
    df['barcode'] = df['barcode'].apply(limpiar_barcode)
    
    # -------------------------------------------------------------
    # 1. CREACIÓN DE INVENTARIO Y LOTES (SCM / Caducidades)
    # -------------------------------------------------------------
    print("📦 Generando 'data/inventario_lotes.csv'...")
    
    # Extraer catálogo de productos únicos por código de barras real
    productos_unicos = df[['barcode', 'name', 'dosage_form', 'type']].drop_duplicates(subset=['barcode']).copy()
    
    np.random.seed(42) # Semilla para consistencia
    n_productos = len(productos_unicos)
    
    # Precios simulados entre $1.50 y $45.00
    productos_unicos['precio_unitario'] = np.round(np.random.uniform(1.50, 45.00, size=n_productos), 2)
    # Stock disponible actual
    productos_unicos['stock_actual'] = np.random.randint(1, 50, size=n_productos)
    # Stock mínimo para alerta
    productos_unicos['stock_minimo'] = 5
    
    # Fechas de Caducidad
    hoy = datetime.now()
    dias_vencimiento = np.random.choice(
        [-15, 10, 25, 60, 180, 365, 720],
        size=n_productos,
        p=[0.05, 0.10, 0.15, 0.20, 0.20, 0.15, 0.15]
    )
    
    fechas_caducidad = [(hoy + timedelta(days=int(d))).strftime('%Y-%m-%d') for d in dias_vencimiento]
    productos_unicos['fecha_caducidad'] = fechas_caducidad
    productos_unicos['lote'] = [f"LOTE-2024-{i+1000}" for i in range(n_productos)]
    
    # Guardar en data/inventario_lotes.csv
    productos_unicos.to_csv("data/inventario_lotes.csv", index=False)
    print(f"✅ 'data/inventario_lotes.csv' generado con {n_productos} productos con códigos de barra únicos reales.")

    # -------------------------------------------------------------
    # 2. CREACIÓN DE PACIENTES RECURRENTES (CRM)
    # -------------------------------------------------------------
    print("👥 Generando 'data/pacientes.csv'...")
    
    n_pacientes = 500
    pacientes_ids = [f"PAC-{i+1000}" for i in range(n_pacientes)]
    nombres = ["Carlos", "María", "Juan", "Ana", "Luis", "Elena", "Pedro", "Sofía", "Diego", "Lucía"]
    apellidos = ["Gómez", "Pérez", "Rodríguez", "López", "Martínez", "García", "Fernández", "Torres"]
    
    lista_pacientes = []
    for id_pac in pacientes_ids:
        nombre_completo = f"{np.random.choice(nombres)} {np.random.choice(apellidos)}"
        r = np.random.rand()
        if r < 0.30:
            dias_atras = np.random.randint(0, 15)
            compras = np.random.randint(5, 12)
        elif r < 0.65:
            dias_atras = np.random.randint(15, 45)
            compras = np.random.randint(2, 6)
        else:
            dias_atras = np.random.randint(46, 180)
            compras = np.random.randint(1, 3)

        fecha_compra = (hoy - timedelta(days=dias_atras)).strftime('%Y-%m-%d %H:%M:%S')
        
        lista_pacientes.append({
            "id_paciente": id_pac,
            "nombre_paciente": nombre_completo,
            "ultima_compra": fecha_compra,
            "total_compras": compras
        })
    
    pacientes_resumen = pd.DataFrame(lista_pacientes)
    pacientes_resumen.to_csv("data/pacientes.csv", index=False)
    print(f"✅ 'data/pacientes.csv' generado correctamente.")

if __name__ == "__main__":
    preparar_datos_base()