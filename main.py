import os
import pandas as pd
from tabulate import tabulate
from modulos.scm_inventario import ModuloSCM
from modulos.erp_finanzas import ModuloERP
from modulos.crm_pacientes import ModuloCRM
from modulos.core_pos import SistemaCorePOS
from analytics.graficos import GeneradorAnalitica
from analytics.rfm_analysis import AnalisisRFM
from analytics.dashboard import DashboardGerencial

def formatear_tabla(df):
    """Convierte un DataFrame en una tabla limpia y perfectamente alineada para la terminal."""
    df_clean = df.copy()
    if 'barcode' in df_clean.columns:
        df_clean['barcode'] = df_clean['barcode'].apply(
            lambda x: f"{float(x):.0f}" if 'E+' in str(x) or 'e+' in str(x) else str(x)
        )
    return tabulate(df_clean, headers='keys', tablefmt='psql', showindex=False)

def ejecutar_simulacion():
    print("="*75)
    print("🏥 SISTEMA INTEGRADO DE GESTIÓN FARMACÉUTICA Y SALUD")
    print("="*75)
    
    # 1. Inicialización de Módulos
    print("\n⚙️ [INICIALIZACIÓN] Cargando módulos del sistema...")
    scm = ModuloSCM()
    erp = ModuloERP(saldo_inicial=10000.0)
    crm = ModuloCRM(dias_umbral_riesgo=30)
    pos = SistemaCorePOS(modulo_scm=scm, modulo_erp=erp, modulo_crm=crm)
    
    # 2. Evaluación Inicial SCM: Caducidades y Medicamentos
    print("\n" + "="*75)
    print("📋 1. MÓDULO SCM - VERIFICACIÓN DE CADUCIDADES Y VENCIMIENTOS")
    print("="*75)
    vencidos, por_vencer = scm.verificar_caducidades(dias_umbral=30)
    
    print(f"🚨 Medicamentos CADUCADOS detectados: {len(vencidos)}")
    if not vencidos.empty:
        print("  Ejemplo de medicamentos vencidos a retirar:\n")
        df_v = vencidos[['barcode', 'name', 'fecha_caducidad', 'stock_actual']].head(3)
        print(formatear_tabla(df_v))
        print()
        
        # Registrar merma contable
        prod_ejemplo = vencidos.iloc[0]
        monto_perdida = prod_ejemplo['stock_actual'] * prod_ejemplo['precio_unitario']
        erp.registrar_asiento_merma(prod_ejemplo['name'], monto_perdida)

    print(f"\n⚠️ Medicamentos Próximos a Vencer (<= 30 días): {len(por_vencer)}")
    if not por_vencer.empty:
        df_pv = por_vencer[['barcode', 'name', 'fecha_caducidad', 'stock_actual']].head(3)
        print(formatear_tabla(df_pv))

    # 3. Simulación de Transacciones en el CORE POS
    print("\n" + "="*75)
    print("🛒 2. SIMULACIÓN DE DISPENSACIÓN Y VENTAS EN TIEMPO REAL (CORE POS)")
    print("="*75)
    
    # Extraer 5 productos del inventario
    productos_sim = scm.df_inventario.head(5)
    
    # Lista de 5 transacciones para simular
    simulaciones = [
        {"factura": 990001, "barcode": productos_sim.iloc[0]['barcode'], "cantidad": 5, "paciente": "PAC-1005"},
        {"factura": 990002, "barcode": productos_sim.iloc[1]['barcode'], "cantidad": 2, "paciente": "PAC-1012"},
        {"factura": 990003, "barcode": productos_sim.iloc[2]['barcode'], "cantidad": 1, "paciente": None}, # Consumidor Final
        {"factura": 990004, "barcode": productos_sim.iloc[3]['barcode'], "cantidad": 3, "paciente": "PAC-1020"},
        {"factura": 990005, "barcode": productos_sim.iloc[4]['barcode'], "cantidad": 4, "paciente": None}, # Consumidor Final
    ]

    for sim in simulaciones:
        pos.procesar_dispensacion(
            id_factura=sim["factura"],
            barcode=sim["barcode"],
            cantidad=sim["cantidad"],
            id_paciente=sim["paciente"]
        )

    # 4. Evaluación CRM: Riesgo de Deserción / Abandono
    print("\n" + "="*75)
    print("👥 3. MÓDULO CRM - ALERTAS DE DESERCIÓN Y ABANDONO DE TRATAMIENTO")
    print("="*75)
    pacientes_riesgo = crm.obtener_pacientes_en_riesgo()
    print(f"🚨 Pacientes en Riesgo de Deserción (>30 días inactivos): {len(pacientes_riesgo)}\n")
    if not pacientes_riesgo.empty:
        df_pr = pacientes_riesgo[['id_paciente', 'nombre_paciente', 'ultima_compra', 'dias_inactivo', 'estado_alerta']].head(5)
        print(formatear_tabla(df_pr))

    # 5. Estado Financiero Final ERP
    print("\n" + "="*75)
    print("💵 4. MÓDULO ERP - ESTADO DE CAJA Y LIBRO DIARIO CONTABLE")
    print("="*75)
    df_libros = erp.obtener_resumen_financiero()
    print(formatear_tabla(df_libros))
    print(f"\n💰 SALDO FINAL EN CAJA CHICA: ${erp.caja_chica:.2f}")

    # 6. Módulo Avanzado RFM & Generación de Dashboard
    print("\n" + "="*75)
    print("🎨 5. ANALYTICS - GENERANDO GRÁFICOS Y DASHBOARD GERENCIAL")
    print("="*75)
    
    # Generar gráficos individuales
    generador = GeneradorAnalitica()
    generador.generar_grafico_caducidades(scm.df_inventario)
    generador.generar_grafico_finanzas(df_libros)
    
    # Ejecutar análisis RFM de pacientes
    rfm = AnalisisRFM()
    rfm.ejecutar_analisis_rfm()
    
    # Compilar Dashboard Gerencial Unificado
    dash = DashboardGerencial()
    dash.compilar_dashboard()
    
    print("\n✨ ¡Simulación inicial completada con éxito!")
    return pos

def menu_interactivo(pos):
    """Menú en consola para ingresar ventas y consultar datos dinámicamente."""
    while True:
        print("\n" + "="*50)
        print("🏥 MENÚ INTERACTIVO - SISTEMA FARMACÉUTICO")
        print("="*50)
        print("1. 🛒 Registrar nueva dispensación (POS)")
        print("2. 📄 Ver historial de Facturas guardadas (CSV)")
        print("3. 📦 Consultar stock de un producto (SCM)")
        print("4. 💵 Consultar saldo y libro diario (ERP)")
        print("5. 📊 Re-generar Dashboard Gerencial")
        print("6. 🚪 Salir")
        
        opcion = input("\nSeleccione una opción (1-6): ").strip()

        if opcion == "1":
            print("\n--- 🛒 REGISTRAR VENTA EN PUNTO DE VENTA ---")
            id_factura = input("Ingrese ID de Factura (ej. F-100): ").strip()
            barcode = input("Ingrese Código de Barras (ej. 789012345601): ").strip()
            
            try:
                cantidad = int(input("Ingrese Cantidad a comprar: "))
            except ValueError:
                print("❌ Cantidad inválida.")
                continue
                
            id_paciente = input("Ingrese ID de Paciente (opcional, Enter para omitir): ").strip()
            nombre_paciente = None

            if id_paciente:
                # Verificar si el paciente ya existe en el CRM
                existe = id_paciente in pos.crm.df_pacientes['id_paciente'].values
                if not existe:
                    print(f"✨ Detectado ID '{id_paciente}' como paciente nuevo en el sistema.")
                    nombre_paciente = input("Ingrese Nombre y Apellido del Paciente: ").strip()

            # Procesar la dispensación guardando el nombre real
            pos.procesar_dispensacion(id_factura, barcode, cantidad, id_paciente, nombre_paciente)

        elif opcion == "2":
            ruta_csv = getattr(pos, 'ruta_csv', 'data/facturas.csv')
            if os.path.exists(ruta_csv):
                df_f = pd.read_csv(ruta_csv)
                print("\n📄 --- HISTORIAL DE FACTURAS GUARDADAS EN CSV ---")
                print(formatear_tabla(df_f))
            else:
                print("\n⚠️ Aún no se han generado facturas en el sistema.")

        elif opcion == "3":
            barcode = input("\nIngrese el Código de Barras del producto: ").strip()
            prod = pos.scm.df_inventario[pos.scm.df_inventario['barcode'] == barcode]
            if not prod.empty:
                print(f"\n📌 Producto: {prod.iloc[0]['name']}")
                print(f"   Stock actual: {prod.iloc[0]['stock_actual']} unidades")
                print(f"   Precio: ${prod.iloc[0]['precio_unitario']}")
            else:
                print("❌ Producto no encontrado.")

        elif opcion == "4":
            print(f"\n💰 Saldo actual en Caja Chica: ${pos.erp.caja_chica:.2f}")
            print(f"📖 Total de asientos contables registrados: {len(pos.erp.libro_diario)}")

        elif opcion == "5":
            print("\n🎨 Generando Dashboard actualizado...")
            dash = DashboardGerencial()
            dash.compilar_dashboard()

        elif opcion == "6":
            print("\n👋 ¡Saliendo del sistema!")
            break
        else:
            print("❌ Opción no válida. Intente de nuevo.")

if __name__ == "__main__":
    pos_instancia = ejecutar_simulacion()
    menu_interactivo(pos_instancia)