# Arquitectura del Módulo Inventario

Este documento define la estructura de módulos ("capitanes") y funcionalidades ("equipos tácticos") para el microservicio de **Gestión de Inventario**.

## Jerarquía de Módulos y Funcionalidades

### **Módulo 1: `catalogo_configuracion.py`**
-   Registro de productos/artículos (código, nombre, categoría).
-   Clasificación de productos (materias primas, insumos, productos terminados).
-   Gestión de unidades de medida (kg, litros, cajas, unidades).
-   Gestión de códigos de barras o QR por producto.
-   Definición de ubicaciones físicas (bodegas, estantes, pasillos).
-   Gestión de lotes (fecha de fabricación, vencimiento).
-   Gestión de series/números de serie únicos.

### **Módulo 2: `entradas_recepcion.py`**
-   Registro de entradas por compras a proveedores.
-   Registro de entradas por devoluciones de clientes.
-   Registro de entradas por ajustes de inventario positivos.
-   Validación de mercancía recibida contra órdenes de compra.
-   Procesos de control de calidad en la recepción.

### **Módulo 3: `salidas_despacho.py`**
-   Registro de salidas por ventas a clientes.
-   Registro de salidas por consumo interno.
-   Registro de devoluciones a proveedores.
-   Procesos de Picking (recolección de productos del almacén).
-   Procesos de Packing (empaquetado y preparación para envío).
-   Validación de mercancía despachada contra pedidos de venta.

### **Módulo 4: `movimientos_internos.py`**
-   Gestión de transferencias de stock entre bodegas y ubicaciones.
-   Registro de ajustes de inventario (sobrantes, faltantes).
-   Gestión y registro de mermas y desperdicios.

### **Módulo 5: `control_fisico.py`**
-   Carga de inventario inicial (al implementar el sistema).
-   Planificación y ejecución de conteos cíclicos.
-   Planificación y ejecución de inventarios físicos periódicos/generales.
-   Registro y conciliación de diferencias de inventario.
-   Generación y consulta del Kardex por producto.

### **Módulo 6: `valoracion_costeo.py`**
-   Aplicación de método de costeo PEPS (FIFO).
-   Aplicación de método de costeo UEPS (LIFO).
-   Aplicación de método de costeo Promedio Ponderado.
-   Aplicación de método de costeo Estándar o Último Costo.
-   Generación de reportes de valorización de inventario.

### **Módulo 7: `planificacion_alertas.py`**
-   Cálculo y configuración de niveles de stock (mínimo, máximo, seguridad).
-   Cálculo y gestión de puntos de reorden automáticos.
-   Generación de alertas automáticas de stock bajo.
-   Generación de alertas automáticas de sobrestock.

### **Módulo 8: `inventarios_especiales.py`**
-   Control y seguimiento de inventario en tránsito.
-   Control y seguimiento de inventario en consignación (propio o de terceros).
-   Gestión de inventario reservado o apartado para pedidos específicos.

### **Módulo 9: `trazabilidad_avanzada.py`**
-   Control de fechas de vencimiento para productos perecederos.
-   Alertas de vencimientos próximos.
-   Análisis de obsolescencia de productos sin rotación.
-   Trazabilidad completa de movimientos por lote o número de serie.
-   Consulta del historial de movimientos por producto.

### **Módulo 10: `reportes_analisis.py`**
-   Reporte de existencias en tiempo real (por producto, bodega, ubicación).
-   Reporte de rotación de productos (ABC).
-   Reporte de inventario valorizado detallado.
-   Reporte de diferencias de inventario post-conteo.
-   Reportes históricos y comparativos de niveles de inventario.
