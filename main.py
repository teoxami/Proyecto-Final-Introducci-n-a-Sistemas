import os
import random
import pandas as pd
from datetime import datetime
from tabulate import tabulate

from modulos.scm_inventario import ModuloSCM
from modulos.erp_finanzas import ModuloERP
from modulos.crm_pacientes import ModuloCRM
from modulos.core_pos import SistemaCorePOS
from analytics.graficos import GeneradorAnalitica
from analytics.rfm_analysis import AnalisisRFM
from analytics.dashboard import DashboardGerencial


def formatear_tabla(df, max_colwidth=22, show_index=False):
    """
    Convierte un DataFrame en una tabla limpia, alineada y adaptada a la terminal.
    """
    if df is None or df.empty:
        return "No hay datos registrados para mostrar."
    
    df_clean = df.copy()

    # Renombrar columnas a un formato estilizado
    renombres = {
        'pos': '#',
        'barcode': 'Código',
        'name': 'Producto',
        'precio_unitario': 'Precio',
        'stock_actual': 'Stock',
        'fecha_caducidad': 'Caducidad',
        'lote': 'Lote',
        'id_paciente': 'ID Pac.',
        'nombre_paciente': 'Paciente',
        'ultima_compra': 'Últ. Compra',
        'total_compras': 'Compras',
        'dias_inactivo': 'Días Inact.',
        'estado_alerta': 'Estado',
        'monto': 'Monto',
        'descripcion': 'Descripción',
        'tipo': 'Tipo'
    }
    df_clean = df_clean.rename(columns={k: v for k, v in renombres.items() if k in df_clean.columns})

    # Formatear columnas
    if 'Código' in df_clean.columns:
        df_clean['Código'] = df_clean['Código'].apply(
            lambda x: f"{float(x):.0f}" if 'E+' in str(x) or 'e+' in str(x) else str(x)
        )
    
    if 'Precio' in df_clean.columns:
        df_clean['Precio'] = df_clean['Precio'].apply(lambda x: f"${float(x):.2f}" if pd.notnull(x) else "$0.00")

    if 'Monto' in df_clean.columns:
        df_clean['Monto'] = df_clean['Monto'].apply(lambda x: f"${float(x):.2f}" if pd.notnull(x) else "$0.00")

    if 'total' in df_clean.columns:
        df_clean['total'] = df_clean['total'].apply(lambda x: f"${float(x):.2f}" if pd.notnull(x) else "$0.00")

    # Truncar textos demasiado largos
    for col in df_clean.columns:
        df_clean[col] = df_clean[col].astype(str).apply(
            lambda x: (x[:max_colwidth-3] + '...') if len(x) > max_colwidth else x
        )

    return tabulate(df_clean, headers='keys', tablefmt='fancy_grid', showindex=show_index)


def mostrar_menu_tabla():
    """Genera el menú principal estilizado dentro de una tabla."""
    opciones_menu = [
        {"Opc": "1", "Módulo": "POS", "Acción": "Registrar nueva dispensación"},
        {"Opc": "2", "Módulo": "POS", "Acción": "Ver historial de Facturas guardadas (CSV)"},
        {"Opc": "3", "Módulo": "SCM", "Acción": "Consultar y/o ajustar stock de producto"},
        {"Opc": "4", "Módulo": "ERP", "Acción": "Consultar saldo y libro diario"},
        {"Opc": "5", "Módulo": "SCM", "Acción": "Auditar caducidades de medicamentos"},
        {"Opc": "6", "Módulo": "SCM", "Acción": "Dar de baja producto vencido (Manual)"},
        {"Opc": "7", "Módulo": "CRM", "Acción": "Consultar pacientes en riesgo (RFM)"},
        {"Opc": "8", "Módulo": "BI",  "Acción": "Generar/Actualizar Dashboard Gerencial"},
        {"Opc": "9", "Módulo": "SYS", "Acción": "Salir del Sistema"}
    ]
    df_menu = pd.DataFrame(opciones_menu)
    print("\n" + tabulate(df_menu, headers='keys', tablefmt='fancy_grid', showindex=False))


def buscar_producto_interactivo(scm, termino_busqueda):
    """Busca productos mostrando de forma clara la columna de Posición (#)."""
    termino = str(termino_busqueda).strip().lower()
    df_inv = scm.df_inventario.copy()
    
    df_inv['barcode_str'] = df_inv['barcode'].astype(str).str.split('.').str[0].str.strip()
    coincidencia_exacta = df_inv[df_inv['barcode_str'] == termino]
    
    if not coincidencia_exacta.empty:
        return coincidencia_exacta.iloc[0]['barcode_str']

    coincidencias = df_inv[df_inv['name'].str.lower().str.contains(termino, na=False)].copy()
    
    if coincidencias.empty:
        print("No se encontraron productos que coincidan con la búsqueda.")
        return None
    elif len(coincidencias) == 1:
        prod = coincidencias.iloc[0]
        print(f"✅ Producto encontrado: {prod['name']} (Stock: {prod['stock_actual']} | Precio: ${prod['precio_unitario']})")
        return prod['barcode_str']
    else:
        print(f"\nSe encontraron {len(coincidencias)} productos coincidentes:")
        
        # Preparar datos con columna de posición (#) explícita
        coincidencias_reset = coincidencias.reset_index(drop=True)
        coincidencias_reset['pos'] = range(1, len(coincidencias_reset) + 1)
        
        # Mostrar las primeras 10 coincidencias en tabla
        coincidencias_view = coincidencias_reset[['pos', 'barcode', 'name', 'stock_actual', 'precio_unitario']].head(10)
        print(formatear_tabla(coincidencias_view))
        
        while True:
            sel = input("\nIngrese la Posición (#) o Código exacto ('c' para cancelar): ").strip()
            if sel.lower() == 'c':
                return None
            
            if sel.isdigit():
                num_sel = int(sel)
                if 1 <= num_sel <= len(coincidencias_reset):
                    return coincidencias_reset.iloc[num_sel - 1]['barcode_str']
            
            if sel in coincidencias_reset['barcode_str'].values:
                return sel
                
            print("Selección no válida. Intente con el número de posición (#) mostrado en la tabla.")


def consultar_y_reportar_caducidades(scm):
    """Muestra la lista de medicamentos caducados y próximos a caducar."""
    vencidos, por_vencer = scm.verificar_caducidades(dias_umbral=30)
    
    print("\n" + "="*60)
    print("🚨 MÓDULO SCM - AUDITORÍA DE CADUCIDADES")
    print("="*60)
    
    if not vencidos.empty:
        print(f"\nMEDICAMENTOS CADUCADOS DETECTADOS ({len(vencidos)} en total):")
        df_v = vencidos[['barcode', 'name', 'lote', 'fecha_caducidad', 'stock_actual', 'precio_unitario']].head(8)
        print(formatear_tabla(df_v))
        print("💡 Consejo: Usa la Opción 6 para dar de baja manualmente los productos vencidos.")
    else:
        print("\nNo hay medicamentos caducados en el inventario.")

    if not por_vencer.empty:
        print(f"\nMEDICAMENTOS PRÓXIMOS A VENCER (<= 30 días - {len(por_vencer)} en total):")
        df_pv = por_vencer[['barcode', 'name', 'lote', 'fecha_caducidad', 'stock_actual']].head(8)
        print(formatear_tabla(df_pv))


def dar_de_baja_producto_vencido(scm, erp):
    """Permite al usuario retirar manualmente un producto vencido del inventario."""
    vencidos, _ = scm.verificar_caducidades(dias_umbral=0)
    
    if vencidos.empty:
        print("No hay productos vencidos en el inventario actualmente.")
        return

    print("\n--- ELIMINACIÓN MANUAL DE MEDICAMENTOS VENCIDOS ---")
    termino = input("Ingrese el Código de Barras o Nombre del producto a dar de baja: ").strip()
    
    barcode = buscar_producto_interactivo(scm, termino)
    if not barcode:
        return

    barcode_str = str(barcode).split('.')[0].strip()
    idx = scm.df_inventario[scm.df_inventario['barcode'].astype(str).str.split('.').str[0].str.strip() == barcode_str].index

    if idx.empty:
        print("No se encontró el producto especificado.")
        return

    fila_prod = scm.df_inventario.loc[idx[0]]
    nombre_prod = fila_prod['name']
    stock_actual = int(fila_prod['stock_actual'])
    precio_unitario = float(fila_prod['precio_unitario'])

    confirmacion = input(f"¿Está seguro de eliminar '{nombre_prod}' (Stock: {stock_actual} un.)? (s/n): ").strip().lower()
    if confirmacion == 's':
        monto_perdida = stock_actual * precio_unitario
        erp.registrar_asiento_merma(nombre_prod, monto_perdida)

        scm.df_inventario = scm.df_inventario.drop(idx).reset_index(drop=True)
        scm.guardar_inventario()

        print(f"Se ha eliminado correctamente '{nombre_prod}' de 'inventario_lotes.csv'.")
        print(f"Pérdida registrada en el ERP: -${monto_perdida:.2f}")
    else:
        print("Operación cancelada.")


def consultar_y_ajustar_stock(scm):
    """Consulta el stock de un producto y permite modificar la cantidad."""
    termino = input("\nIngrese Código de Barras o Nombre del producto a consultar: ").strip()
    barcode = buscar_producto_interactivo(scm, termino)
    
    if not barcode:
        return

    barcode_str = str(barcode).split('.')[0].strip()
    idx = scm.df_inventario[scm.df_inventario['barcode'].astype(str).str.split('.').str[0].str.strip() == barcode_str].index

    if idx.empty:
        print("No se encontró el producto en el inventario.")
        return

    i = idx[0]
    prod = scm.df_inventario.loc[[i]][['barcode', 'name', 'stock_actual', 'precio_unitario', 'fecha_caducidad']]
    print("\nDETALLE DEL PRODUCTO SELECCIONADO:")
    print(formatear_tabla(prod))

    print("\n¿Desea modificar el stock de este producto?")
    print(" 1. Añadir unidades (Ingreso / Reposición)")
    print(" 2. Remover unidades (Ajuste / Pérdida)")
    print(" 3. Volver al menú principal (Sin cambios)")
    
    opc = input("\nSeleccione una opción (1-3): ").strip()

    if opc == "1":
        try:
            cant = int(input("Ingrese la cantidad de unidades a AÑADIR: "))
            if cant <= 0:
                print("La cantidad debe ser mayor a cero.")
                return
            
            scm.df_inventario.loc[i, 'stock_actual'] += cant
            scm.guardar_inventario()
            print(f"¡Stock actualizado! Nuevo stock: {scm.df_inventario.loc[i, 'stock_actual']} unidades.")
        except ValueError:
            print("Entrada no válida.")

    elif opc == "2":
        try:
            cant = int(input("Ingrese la cantidad de unidades a REMOVER: "))
            if cant <= 0:
                print("La cantidad debe ser mayor a cero.")
                return
            
            stock_actual = int(scm.df_inventario.loc[i, 'stock_actual'])
            if cant > stock_actual:
                print(f"No se puede remover {cant} unidades. El stock disponible es solo {stock_actual}.")
                return
            
            scm.df_inventario.loc[i, 'stock_actual'] -= cant
            scm.guardar_inventario()
            print(f"¡Stock actualizado! Nuevo stock: {scm.df_inventario.loc[i, 'stock_actual']} unidades.")
        except ValueError:
            print("Entrada no válida.")

    elif opc == "3":
        print("Sin modificaciones en el stock.")
    else:
        print("Opción no válida.")


def inicializar_sistema():
    """Inicializa los módulos principales del sistema."""
    print("="*75)
    print("SISTEMA INTEGRADO DE GESTIÓN FARMACÉUTICA Y SALUD")
    print("="*75)
    print("\n[INICIALIZACIÓN] Cargando módulos del sistema...")
    
    scm = ModuloSCM()
    erp = ModuloERP(saldo_inicial=10000.0)
    crm = ModuloCRM(dias_umbral_riesgo=30)
    pos = SistemaCorePOS(modulo_scm=scm, modulo_erp=erp, modulo_crm=crm)
    
    vencidos, _ = scm.verificar_caducidades(dias_umbral=0)
    if not vencidos.empty:
        print(f"[ATENCIÓN] Hay {len(vencidos)} lote(s) de medicamentos caducados en inventario. Revisa la Opción 5 para auditarlos.")
    
    print("Sistema listo para operar de manera interactiva.\n")
    return pos


def menu_interactivo(pos):
    """Menú principal en consola con tabla estéticamente integrada."""
    while True:
        mostrar_menu_tabla()
        opcion = input("\nSeleccione una opción (1-9): ").strip()

        if opcion == "1":
            print("\n---REGISTRAR VENTA EN PUNTO DE VENTA (POS)---")
            id_factura = f"F-{random.randint(10000, 99999)}"
            print(f"ID de Factura generado automáticamente: {id_factura}")
            
            termino = input("Ingrese Código de Barras o Nombre del producto: ").strip()
            barcode_seleccionado = buscar_producto_interactivo(pos.scm, termino)
            
            if not barcode_seleccionado:
                print("Operación cancelada o producto no seleccionado.")
                continue

            try:
                cantidad = int(input("Ingrese Cantidad a comprar: "))
                if cantidad <= 0:
                    print("La cantidad debe ser mayor a cero.")
                    continue
            except ValueError:
                print("Cantidad inválida.")
                continue
                
            id_paciente = input("Ingrese ID de Paciente (opcional, Enter para omitir): ").strip()
            nombre_paciente = None

            if id_paciente:
                pos.crm.cargar_pacientes()
                lista_ids = pos.crm.df_pacientes['id_paciente'].astype(str).str.strip().tolist()
                id_clean = str(id_paciente).strip()
                
                if id_clean in lista_ids:
                    fila = pos.crm.df_pacientes[pos.crm.df_pacientes['id_paciente'].astype(str).str.strip() == id_clean]
                    nombre_paciente = fila.iloc[0]['nombre_paciente']
                    print(f"Paciente detectado en sistema: {nombre_paciente}")
                else:
                    print(f"Detectado ID '{id_clean}' como paciente nuevo en el sistema.")
                    nombre_paciente = input("Ingrese Nombre y Apellido del Paciente: ").strip()

            # La dispensación se encarga de registrar/actualizar al paciente de forma limpia (+1 compra)
            pos.procesar_dispensacion(id_factura, barcode_seleccionado, cantidad, id_paciente, nombre_paciente)

        elif opcion == "2":
            ruta_csv = getattr(pos, 'ruta_csv', 'data/facturas.csv')
            if os.path.exists(ruta_csv) and os.path.getsize(ruta_csv) > 0:
                df_f = pd.read_csv(ruta_csv)
                print("\n--- HISTORIAL DE FACTURAS GUARDADAS EN CSV ---")
                print(formatear_tabla(df_f))
            else:
                print("\nAún no se han generado facturas en el sistema.")

        elif opcion == "3":
            consultar_y_ajustar_stock(pos.scm)

        elif opcion == "4":
            print("\n---CONSULTAR SALDO Y LIBRO DIARIO (ERP) ---")
            print(f"Saldo actual en Caja Chica: ${pos.erp.caja_chica:.2f}")
            df_libros = pos.erp.obtener_resumen_financiero()
            print(formatear_tabla(df_libros))

        elif opcion == "5":
            consultar_y_reportar_caducidades(pos.scm)

        elif opcion == "6":
            dar_de_baja_producto_vencido(pos.scm, pos.erp)

        elif opcion == "7":
            print("\n---MÓDULO CRM - ALERTAS DE DESERCIÓN Y PACIENTES ---")
            pacientes_riesgo = pos.crm.obtener_pacientes_en_riesgo()
            print(f"Pacientes en Riesgo (>30 días inactivos): {len(pacientes_riesgo)}\n")
            if not pacientes_riesgo.empty:
                df_pr = pacientes_riesgo[['id_paciente', 'nombre_paciente', 'ultima_compra', 'dias_inactivo', 'estado_alerta']].head(8)
                print(formatear_tabla(df_pr))

        elif opcion == "8":
            print("\nGenerando Dashboard Gerencial...")
            generador = GeneradorAnalitica()
            generador.generar_grafico_caducidades(pos.scm.df_inventario)
            generador.generar_grafico_finanzas(pos.erp.obtener_resumen_financiero())
            
            rfm = AnalisisRFM()
            rfm.ejecutar_analisis_rfm()
            
            dash = DashboardGerencial()
            dash.compilar_dashboard()
            print("¡Dashboard y gráficos generados exitosamente!")

        elif opcion == "9":
            print("\n¡Saliendo del sistema!")
            break
        else:
            print("Opción no válida. Intente de nuevo.")

if __name__ == "__main__":
    pos_instancia = inicializar_sistema()
    menu_interactivo(pos_instancia)