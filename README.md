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
PROYECTO FINAL ISI/
│
├── data/                       # Archivos de datos locales (CSV)
│   ├── productos_completo.csv
│   └── pacientes.csv
│
├── modulos/                    # Módulos satélites y Core POS
│   ├── __init__.py
│   ├── scm_inventario.py       # Control de Stock y Caducidades
│   ├── erp_finanzas.py         # Caja Chica y Libro Diario
│   ├── crm_pacientes.py        # Adherencia y Riesgo de Abandono
│   └── core_pos.py             # Orquestador Integrado de Ventas
│
├── analytics/                  # Inteligencia de Negocios y Dashboards
│   ├── __init__.py
│   ├── graficos.py             # Renderizado de gráficos (SCM y ERP)
│   ├── rfm_analysis.py         # Segmentación RFM de pacientes (CRM)
│   ├── dashboard.py            # Dashboard Gerencial Consolidado (2x2)
│   └── dashboard_gerencial.png # Salida gráfica del panel ejecutivo
│
├── setup_data.py               # Generador automatizado de datos iniciales
├── main.py                     # Ejecutable principal del sistema
└── README.md                   # Documentación técnica
---

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
