# Plan Detallado Actualizado para el Proyecto "SARITA"

**Objetivo:** Crear un sistema de gestión empresarial (ERP) completo para cualquier tipo de empresa en Colombia, que incluya los siguientes módulos:

1.  **Sistema Contable:** Componente principal del sistema, que debe ser muy completo y funcional, cumpliendo con las normas NIIF.
2.  **Sistema Comercial:** Integrado con el sistema contable, que incluye:
    *   Manejo de clientes: Clasificación de clientes potenciales.
    *   Gestión de redes sociales: Administración de redes sociales.
    *   Sistema de creación y edición de videos: Similar a Trevis AI, con LLM especializadas para crear, editar y enviar videos a diferentes redes sociales.
3.  **Sistema Operativo:** Integrado con el sistema contable, que incluye:
    *   RRHH: Gestión de recursos humanos.
    *   SG SST: Sistema de gestión de seguridad y salud en el trabajo.
    *   Inventarios: Gestión de inventarios.
    *   Módulos para turismo:
        *   Gestión de mesas, habitaciones, vehículos y guías.
        *   Gestión de paquetes turísticos.
        *   Inventarios de atractivos turísticos.
        *   Inventarios de elementos turísticos.
        *   Gestión de menús.
        *   Gestión de pedidos.
4.  **Sistema de Gestión de Archivos:** Transversal a todos los módulos (Comercial, Operativo, Contable y Análisis Financiero), que permite gestionar archivos en cada uno de ellos.
5.  **Sistema de Gestión de Facturación Electrónica:** Integrado con el sistema contable.
6.  **Análisis Financiero:** Cálculo de ratios e indicadores financieros.
7.  **Informes y Reportes:** Generación de reportes personalizados.
8.  **Auditoría y Soporte:** Historial de cambios y logs.

**Prioridades:**

1.  **Sistema Contable:** Implementar la funcionalidad para registrar comprobantes y movimientos contables de acuerdo con las normas NIIF.
2.  **Catálogo Contable (PUC):** Gestionar el Plan Único de Cuentas (PUC) para Colombia, permitiendo agregar, modificar y eliminar cuentas contables.
3.  **Sistema Comercial - Manejo de Clientes:** Implementar la funcionalidad para clasificar clientes potenciales.
4.  **Sistema de Gestión de Archivos:** Implementar la funcionalidad transversal para gestionar archivos en los módulos principales.

**Diagrama de Componentes del Sistema "SARITA":**

```mermaid
graph LR
    A[Sistema Contable] --> F[Sistema de Gestión de Archivos];
    B[Sistema Comercial] --> F;
    C[Sistema Operativo] --> F;
    D[Sistema de Gestión de Facturación Electrónica] --> A;
    E[Análisis Financiero] --> F;
    A --> G[Informes y Reportes];
    A --> H[Auditoría y Soporte];
    B --> I[Manejo de Clientes];
    B --> J[Gestión de Redes Sociales];
    B --> K[Creación y Edición de Videos];
    C --> L[RRHH];
    C --> M[SG SST];
    C --> N[Inventarios];
    C --> O[Módulos para Turismo];