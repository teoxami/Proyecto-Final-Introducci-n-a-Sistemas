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
    # 2. CREACIÓN DE PACIENTES RECURRENTES (CRM)
    # -------------------------------------------------------------
    print("👥 Generando 'data/pacientes.csv'...")
    
    invoices_unicas = df['Invoice'].unique()
    n_invoices = len(invoices_unicas)
    
    # Crear una lista simulada de 500 pacientes recurrentes
    pacientes_ids = [f"PAC-{i+1000}" for i in range(500)]
    
    # Asignar aleatoriamente las facturas a los pacientes
    mapa_pacientes = np.random.choice(pacientes_ids, size=n_invoices)
    df_factura_paciente = pd.DataFrame({
        'Invoice': invoices_unicas,
        'id_paciente': mapa_pacientes
    })
    
    # Cruzar con las fechas para obtener la última compra de cada paciente
    df_merged = df.merge(df_factura_paciente, on='Invoice')
    df_merged['addeddate'] = pd.to_datetime(df_merged['addeddate'])
    
    pacientes_resumen = df_merged.groupby('id_paciente').agg(
        nombre_paciente=('id_paciente', lambda x: f"Paciente {x.iloc[0]}"),
        ultima_compra=('addeddate', 'max'),
        total_compras=('Invoice', 'nunique')
    ).reset_index()
    
    pacientes_resumen['ultima_compra'] = pacientes_resumen['ultima_compra'].dt.strftime('%Y-%m-%d')
    
    # Guardar en data/pacientes.csv
    pacientes_resumen.to_csv("data/pacientes.csv", index=False)
    print(f"✅ 'data/pacientes.csv' generado con {len(pacientes_resumen)} registros de pacientes.\n")
    print("🎉 ¡Proceso completado! Archivos auxiliares listos.")

if __name__ == "__main__":
    preparar_datos_base()