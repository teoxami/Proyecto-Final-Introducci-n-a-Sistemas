import pandas as pd
from datetime import datetime

class ModuloCRM:
    def __init__(self, ruta_pacientes="data/pacientes.csv", dias_umbral_riesgo=30):
        self.ruta_pacientes = ruta_pacientes
        self.dias_umbral = dias_umbral_riesgo
        self.cargar_pacientes()

    def cargar_pacientes(self):
        """Carga la base de pacientes desde el archivo CSV."""
        try:
            self.df_pacientes = pd.read_csv(self.ruta_pacientes)
            self.df_pacientes['ultima_compra'] = pd.to_datetime(self.df_pacientes['ultima_compra'])
        except Exception as e:
            print(f"❌ Error al cargar pacientes CRM: {e}")

    def actualizar_interaccion_paciente(self, id_paciente):
        """
        Disparador CRM: Actualiza la fecha de última compra cuando un paciente
        vuelve a comprar su tratamiento en la farmacia.
        """
        idx = self.df_pacientes[self.df_pacientes['id_paciente'] == id_paciente].index
        hoy = datetime.now()
        
        if not idx.empty:
            i = idx[0]
            self.df_pacientes.loc[i, 'ultima_compra'] = hoy
            self.df_pacientes.loc[i, 'total_compras'] += 1
            print(f"  👤 [CRM ACTUALIZACIÓN] Interacción registrada para {id_paciente}. Tratamiento actualizado.")
            self.guardar_pacientes()
        else:
            # Si el paciente es nuevo, se registra
            nuevo_paciente = pd.DataFrame([{
                'id_paciente': id_paciente,
                'nombre_paciente': f"Paciente {id_paciente}",
                'ultima_compra': hoy,
                'total_compras': 1
            }])
            self.df_pacientes = pd.concat([self.df_pacientes, nuevo_paciente], ignore_index=True)
            print(f"  👤 [CRM NUEVO] Paciente {id_paciente} registrado exitosamente.")
            self.guardar_pacientes()

    def obtener_pacientes_en_riesgo(self):
        """
        Consulta automatizada: Aisla y retorna a los pacientes que superan 
        el umbral de días sin comprar (Riesgo de Deserción / Abandono).
        """
        hoy = datetime.now()
        self.df_pacientes['dias_inactivo'] = (hoy - self.df_pacientes['ultima_compra']).dt.days
        
        # Filtrar pacientes en riesgo
        en_riesgo = self.df_pacientes[self.df_pacientes['dias_inactivo'] > self.dias_umbral].copy()
        en_riesgo['estado_alerta'] = "ALERTA: Paciente en Riesgo de Deserción"
        
        return en_riesgo.sort_values(by='dias_inactivo', ascending=False)

    def guardar_pacientes(self):
        """Guarda la información de pacientes en el CSV."""
        df_to_save = self.df_pacientes.copy()
        df_to_save['ultima_compra'] = df_to_save['ultima_compra'].dt.strftime('%Y-%m-%d')
        if 'dias_inactivo' in df_to_save.columns:
            df_to_save = df_to_save.drop(columns=['dias_inactivo'])
        df_to_save.to_csv(self.ruta_pacientes, index=False)