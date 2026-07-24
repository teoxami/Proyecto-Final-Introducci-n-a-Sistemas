import os
import pandas as pd
from datetime import datetime

class ModuloCRM:
    def __init__(self, ruta_pacientes="data/pacientes.csv", dias_umbral_riesgo=30):
        self.ruta_pacientes = ruta_pacientes
        self.dias_umbral = dias_umbral_riesgo
        self.cargar_pacientes()

    def cargar_pacientes(self):
        """Lee el archivo CSV desde el disco o inicializa la estructura si no existe."""
        try:
            if os.path.exists(self.ruta_pacientes) and os.path.getsize(self.ruta_pacientes) > 0:
                self.df_pacientes = pd.read_csv(self.ruta_pacientes)
                
                # Normalizar IDs como strings limpios
                self.df_pacientes['id_paciente'] = (
                    self.df_pacientes['id_paciente']
                    .astype(str)
                    .str.split('.')
                    .str[0]
                    .str.strip()
                )
            else:
                # Estructura base en caso de que el archivo no exista o esté vacío
                self.df_pacientes = pd.DataFrame(columns=[
                    'id_paciente', 'nombre_paciente', 'ultima_compra', 'total_compras'
                ])
        except Exception as e:
            print(f"❌ Error al cargar pacientes CRM: {e}")
            self.df_pacientes = pd.DataFrame(columns=[
                'id_paciente', 'nombre_paciente', 'ultima_compra', 'total_compras'
            ])

    def actualizar_interaccion_paciente(self, id_paciente, nombre_nuevo=None):
        """Actualiza la interacción de un paciente existente o registra uno nuevo."""
        # Forzar sincronización desde el CSV antes de buscar
        self.cargar_pacientes()
        
        id_paciente = str(id_paciente).split('.')[0].strip()
        mask = self.df_pacientes['id_paciente'] == id_paciente
        fecha_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if mask.any():
            self.df_pacientes.loc[mask, 'ultima_compra'] = fecha_str
            self.df_pacientes.loc[mask, 'total_compras'] = (
                pd.to_numeric(self.df_pacientes.loc[mask, 'total_compras'], errors='coerce').fillna(0) + 1
            )
            print(f"  👤 [CRM] Historial actualizado para paciente registrado: {id_paciente}")
        else:
            nombre_final = nombre_nuevo.strip() if nombre_nuevo and nombre_nuevo.strip() else f"Paciente {id_paciente}"
            nuevo_paciente = {
                'id_paciente': id_paciente,
                'nombre_paciente': nombre_final,
                'ultima_compra': fecha_str,
                'total_compras': 1
            }
            self.df_pacientes = pd.concat([self.df_pacientes, pd.DataFrame([nuevo_paciente])], ignore_index=True)
            print(f"  👤 [CRM] Registrado nuevo paciente: {nombre_final} ({id_paciente})")

        self.guardar_pacientes()

    def obtener_pacientes_en_riesgo(self):
        """Devuelve los pacientes que superan el umbral de días inactivos."""
        self.cargar_pacientes()
        if self.df_pacientes.empty or 'ultima_compra' not in self.df_pacientes.columns:
            return pd.DataFrame()

        hoy = datetime.now()
        df_temp = self.df_pacientes.copy()
        
        df_temp['ultima_compra_dt'] = pd.to_datetime(df_temp['ultima_compra'], errors='coerce')
        df_temp['dias_inactivo'] = (hoy - df_temp['ultima_compra_dt']).dt.days
        
        en_riesgo = df_temp[df_temp['dias_inactivo'] > self.dias_umbral].copy()
        en_riesgo['estado_alerta'] = "ALERTA: Paciente en Riesgo de Deserción"
        
        return en_riesgo.sort_values(by='dias_inactivo', ascending=False)

    def guardar_pacientes(self):
        """Guarda limpia la información en el CSV de pacientes."""
        # Asegurar creación del directorio data/ si no existe
        os.makedirs(os.path.dirname(self.ruta_pacientes), exist_ok=True)
        
        df_to_save = self.df_pacientes.copy()
        
        # Eliminar columnas temporales de cálculo antes de guardar
        cols_a_borrar = ['ultima_compra_dt', 'dias_inactivo', 'estado_alerta']
        df_to_save = df_to_save.drop(columns=[col for col in cols_a_borrar if col in df_to_save.columns])
            
        df_to_save.to_csv(self.ruta_pacientes, index=False)