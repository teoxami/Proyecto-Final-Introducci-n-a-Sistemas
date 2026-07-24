# 🏥 Sistema Integrado de Gestión Farmacéutica y Salud (ERP - SCM - CRM - POS)

Un sistema integral desarrollado en Python para la optimización de procesos operativos, financieros y relacionales en la industria farmacéutica y centros de salud.

---

## 🎯 Retos de Negocio Resueltos

1. **Gestión de Caducidades y Reabastecimiento (SCM):** Monitoreo automatizado de inventarios con control de caducidades a 30 días e identificación de mermas.
2. **Finanzas y Contabilidad en Tiempo Real (ERP):** Control de caja chica, generación de asientos contables automáticos por ventas e impacto inmediato de mermas por productos vencidos.
3. **Adherencia y Alertas de Deserción de Tratamiento (CRM):** Rastrear la frecuencia de consumo de medicamentos en pacientes recurrentes, emitiendo alertas de riesgo de deserción y segmentación mediante la metodología **RFM** (Recencia, Frecuencia y Valor Monetario).
4. **Punto de Venta e Integración (Core POS):** Orquestación central que conecta SCM, ERP y CRM en cada dispensación en tiempo real.

---

## 🏗️ Arquitectura del Proyecto

```text
PROYECTO-FINAL-INTRODUCCION-A-SISTEMAS/
│
├── analytics/
│   ├── __pycache__/
│   ├── __init__.py
│   ├── dashboard.py
│   ├── dashboard_gerencial.png
│   ├── grafico_caducidades.png
│   ├── grafico_flujo_caja.png
│   ├── grafico_rfm_pacientes.png
│   ├── graficos.py
│   └── rfm_analysis.py
│
├── data/
│   ├── facturas.csv
│   ├── global_test_set.csv
│   ├── inventario_lotes.csv
│   ├── libro_diario.csv
│   └── pacientes.csv
│
├── modulos/
│   ├── __pycache__/
│   ├── __init__.py
│   ├── core_pos.py
│   ├── crm_pacientes.py
│   ├── erp_finanzas.py
│   └── scm_inventario.py
│
├── .gitignore
├── README.md
├── main.py
├── requirements.txt
└── setup_data.py
---
```

# Requisitos

- Python 3.13 o superior
- Dependencias definidas en `requirements.txt`

## Instalación

Clonar el repositorio:

```bash
git clone https://github.com/teoxami/Proyecto-Final-Introducci-n-a-Sistemas.git
cd Proyecto-Final-Introducci-n-a-Sistemas
```

Instalar las dependencias:

```bash
python -m pip install -r requirements.txt
```

Ejecutar el sistema:

```bash
python main.py

```
## 🛡️ FASE 3.2: Auditoría Web y Despliegue Cloud

Si la plataforma fuera desplegada en un entorno de producción en la nube (ej. AWS / Azure), se establecen las siguientes directrices de auditoría y rendimiento:

### 1. KPIs de Desempeño Web (Core Web Vitals)
* **LCP (Largest Contentful Paint) < 2.5s:** Carga rápida de la interfaz del Punto de Venta (POS) y catálogo visual de productos.
* **FID / INP (Interaction to Next Paint) < 200ms:** Respuesta inmediata al escanear un código de barras o ingresar un paciente en el POS.
* **CLS (Cumulative Layout Shift) < 0.1:** Estabilidad visual durante la selección de medicamentos y generación de facturas contables.

### 2. Seguridad y Protocolos en la Nube
* **Cifrado de Datos:** Tránsito mediante HTTPS/TLS 1.3 y reposo utilizando cifrado AES-256 para la base de datos de pacientes (cumplimiento de confidencialidad de datos de salud).
* **Control de Acceso Basado en Roles (RBAC):** Roles independientes para Cajero (POS), Administrador de Inventario (SCM/ERP) y Analista BI (CRM/Analytics).
* **Trazabilidad de Asientos:** Registro inalterable (*Audit Logs*) de cada movimiento contable generado en la caja chica para prevención de fraudes.
