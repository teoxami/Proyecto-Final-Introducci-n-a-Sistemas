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
    """Convierte un DataFrame en una tabla limpia y perfectamente alineada."""
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
    
    productos_sim = scm.df_inventario.head(2)
    barcode_1 = productos_sim.iloc[0]['barcode']
    barcode_2 = productos_sim.iloc[1]['barcode']
    
    pos.procesar_dispensacion(
        id_factura=990001,
        barcode=barcode_1,
        cantidad=5,
        id_paciente="PAC-1005"
    )
    
    pos.procesar_dispensacion(
        id_factura=990002,
        barcode=barcode_2,
        cantidad=15,
        id_paciente="PAC-1012"
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
    
    print("\n✨ ¡Proceso completado con éxito! Revisa la carpeta 'analytics/' para ver el 'dashboard_gerencial.png'.\n")

if __name__ == "__main__":
    ejecutar_simulacion()

 