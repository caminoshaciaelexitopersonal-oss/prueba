# SARITA - Sistema de Gestión Empresarial Inteligente

Este documento describe la arquitectura, funcionalidad y estado actual del proyecto SARITA, un sistema de gestión empresarial (ERP) impulsado por una arquitectura avanzada de agentes de Inteligencia Artificial.

## Visión General del Sistema

SARITA está diseñado como un sistema SaaS multi-módulo para la gestión integral de una empresa. La inteligencia del sistema se basa en un "ejército de agentes" jerárquico construido con LangChain y LangGraph, permitiendo procesar solicitudes en lenguaje natural y automatizar tareas complejas.

## Arquitectura de Componentes

El proyecto está organizado en módulos de negocio independientes, cada uno con su propia lógica, interfaz y ejército de agentes.

### Módulos Principales
*   **`contabilidad`**: El núcleo del sistema. Gestiona el plan de cuentas (PUC), la contabilidad NIIF, y los asientos contables.
*   **`activos_fijos`**: Gestiona el ciclo de vida de los activos fijos, desde su adquisición hasta su depreciación y baja.
*   **`inventario`**: Controla el stock de productos, gestiona el kardex a través de movimientos de compra/venta y calcula el costo promedio.
*   **`analisis_financiero`**: Calcula e interpreta una amplia gama de ratios financieros para evaluar la salud de la empresa.
*   **`Gestion operativa/Nomina`**: Gestiona empleados y realiza cálculos complejos de nómina según la ley colombiana.
*   **`Gestion operativa/SG-SST`**: Módulo para la gestión de Seguridad y Salud en el Trabajo.
*   **`Gestion-comercial`**: (Futuro) Módulo para la gestión de clientes, ventas, etc.

### Arquitectura de Agentes Jerárquicos (Implementado en `contabilidad`, `activos_fijos`, `analisis_financiero`)

Cada módulo implementa una cadena de mando de agentes para procesar las solicitudes de los usuarios:

1.  **General (Coronel):** Es el agente de más alto nivel de un módulo. Actúa como un **enrutador inteligente**. Su única función es analizar la solicitud del usuario y delegarla al Capitán especialista más adecuado.
2.  **Capitanes:** Son agentes especialistas que reciben órdenes del General. Cada Capitán tiene un dominio muy concreto (ej: "Reportería de Activos Fijos" o "Gestión de Stock").
3.  **Equipo Táctico (Herramientas):** Los Capitanes utilizan un conjunto de herramientas (`tools`) que se conectan directamente con la lógica de negocio del sistema para ejecutar la tarea final (ej: consultar la base de datos, realizar un cálculo).

Este diseño permite una alta especialización y escalabilidad. Añadir nuevas capacidades al sistema es tan simple como añadir un nuevo Capitán especialista y enseñarle al General a delegarle tareas.

## Avances Realizados en esta Fase

1.  **Refactorización y Estabilización del Proyecto:**
    *   Se reorganizó la estructura de directorios para seguir los estándares de Python, solucionando errores críticos de importación.
    *   Se reparó la suite de pruebas completa, garantizando la estabilidad del código base.

2.  **Implementación de la Arquitectura Jerárquica:**
    *   Se diseñó e implementó la cadena de mando "General -> Capitán" en los módulos de **Contabilidad, Activos Fijos y Análisis Financiero**.
    *   Cada uno de estos módulos ahora cuenta con un General que enruta las tareas y Capitanes especialistas que las ejecutan.

3.  **Evolución del Agente de Contabilidad (Capacidad de Escritura):**
    *   El agente de Contabilidad ahora no solo lee datos, sino que también puede **crear asientos contables** a partir de instrucciones en lenguaje natural, un avance clave hacia la automatización.

## Próximos Pasos (Bloqueo Actual)

El siguiente paso es replicar la arquitectura jerárquica en los módulos restantes (`Nomina`, `SG-SST`). Sin embargo, existe un **bloqueo técnico** con las herramientas del entorno que impiden crear archivos en directorios con espacios en el nombre, como `"Gestion operativa"`. Se requiere una acción manual para renombrar este directorio a `"operativa"` antes de poder continuar con la implementación en esos módulos.
