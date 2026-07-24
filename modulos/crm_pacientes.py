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

    def actualizar_interaccion_paciente(self, id_paciente, nombre_nuevo=None):
        """
        Actualiza la fecha de última compra y la frecuencia.
        Si el paciente no existe y se provee un nombre, lo crea.
        """
        id_paciente = str(id_paciente).strip()
        mask = self.df_pacientes['id_paciente'] == id_paciente

        if mask.any():
            self.df_pacientes.loc[mask, 'ultima_compra'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.df_pacientes.loc[mask, 'total_compras'] += 1
            print(f"  👤 [CRM] Historial actualizado para paciente registrado: {id_paciente}")
        else:
            nombre_final = nombre_nuevo if nombre_nuevo else f"Paciente {id_paciente}"
            nuevo_paciente = {
                'id_paciente': id_paciente,
                'nombre_paciente': nombre_final,
                'ultima_compra': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'total_compras': 1
            }
            self.df_pacientes = pd.concat([self.df_pacientes, pd.DataFrame([nuevo_paciente])], ignore_index=False)
            print(f"  👤 [CRM] Registrar nuevo paciente: {nombre_final} ({id_paciente})")

        self.df_pacientes.to_csv("data/pacientes.csv", index=False)

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