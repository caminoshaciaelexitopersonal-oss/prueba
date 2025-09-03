# Arquitectura del Módulo SG-SST

Este documento define la estructura de módulos ("capitanes") y funcionalidades ("equipos tácticos") para el microservicio de **Sistema de Gestión de Seguridad y Salud en el Trabajo (SG-SST)**.

## Jerarquía de Módulos y Funcionalidades

### **Módulo 1: `matriz_peligros.py` (8 Tácticas)**
1.  Registro de actividades, procesos y tareas.
2.  Identificación de peligros (físicos, químicos, biológicos, ergonómicos, psicosociales).
3.  Valoración del nivel de riesgo (probabilidad x severidad).
4.  Clasificación de riesgos por criticidad.
5.  Determinación de controles existentes.
6.  Recomendación de controles adicionales.
7.  Actualización periódica de la matriz.
8.  Exportación de la matriz en formatos oficiales.

### **Módulo 2: `planes_procedimientos.py` (7 Tácticas)**
9.  Registro de planes de acción (preventivos y correctivos).
10. Creación de procedimientos de trabajo seguro por tarea.
11. Gestión de planes de emergencia (evacuación, incendio, primeros auxilios).
12. Seguimiento al cumplimiento de planes y programas.
13. Cronogramas de implementación de medidas.
14. Asignación de responsables por actividad.
15. Carga y gestión de evidencia documental de ejecución.

### **Módulo 3: `documentacion_formatos.py` (5 Tácticas)**
16. Gestión central de políticas de seguridad y salud.
17. Registro centralizado de formatos oficiales (checklists, inspecciones, etc.).
18. Control de versiones de toda la documentación.
19. Gestión de acceso por perfiles de usuario (lectura/escritura).
20. Almacenamiento centralizado de evidencias (PDF, fotos, firmas digitales).

### **Módulo 4: `capacitacion_entrenamiento.py` (6 Tácticas)**
21. Registro de capacitaciones programadas y ejecutadas.
22. Control de asistencia y participación de trabajadores.
23. Creación y gestión de evaluaciones de conocimientos (pre y post test).
24. Emisión y almacenamiento de certificados de capacitación.
25. Mantenimiento del registro histórico de capacitación por trabajador.
26. Sistema de alertas para capacitaciones pendientes o vencidas.

### **Módulo 5: `incidentes_investigacion.py` (6 Tácticas)**
27. Registro de incidentes y accidentes de trabajo.
28. Clasificación de incidentes por gravedad y tipo.
29. Aplicación de metodologías de investigación de causas (árbol de causas / Ishikawa).
30. Registro y seguimiento de medidas correctivas post-incidente.
31. Seguimiento a la eficacia de las medidas implementadas.
32. Generación de reportes obligatorios para autoridades regulatorias.

### **Módulo 6: `indicadores_dashboards.py` (5 Tácticas)**
33. Cálculo automático del indicador de frecuencia de accidentes.
34. Cálculo automático del indicador de severidad de accidentes.
35. Medición y análisis de la tasa de ausentismo laboral.
36. Dashboard en tiempo real con los principales KPIs del SG-SST.
37. Generación de gráficos comparativos por periodos, áreas o sedes.

### **Módulo 7: `biblioteca_normatividad.py` (3 Tácticas)**
38. Biblioteca digital de normas y legislación SST (locales e internacionales).
39. Sistema de alertas sobre actualizaciones normativas.
40. Herramienta de mapeo entre la normativa y los controles aplicados en la empresa.

### **Módulo 8: `condiciones_trabajo_epp.py` (8 Tácticas)**
41. Programación y ejecución de inspecciones planeadas de seguridad.
42. Gestión de checklists digitales para inspecciones.
43. Registro fotográfico georreferenciado de hallazgos.
44. Creación y seguimiento de planes de mejora derivados de inspecciones.
45. Registro de entrega y reposición de EPP a trabajadores.
46. Control del ciclo de vida útil y fechas de vencimiento de los EPP.
47. Alertas automáticas para reposición de EPP.
48. Registro de evidencia (firma, foto) de uso de EPP en tareas críticas.

### **Módulo 9: `salud_ocupacional.py` (4 Tácticas)**
49. Gestión de exámenes médicos ocupacionales (ingreso, periódicos, retiro).
50. Seguimiento centralizado a restricciones y recomendaciones médicas.
51. Administración de programas de vigilancia epidemiológica (PVE).
52. Control, reporte y análisis de enfermedades laborales.

### **Módulo 10: `emergencias_brigadas.py` (4 Tácticas)**
53. Registro y gestión de la conformación de brigadistas de emergencia.
54. Cronograma y planificación de simulacros (evacuación, incendios, etc.).
55. Formulario de evaluación y registro de resultados de simulacros.
56. Digitalización y acceso rápido al plan de atención de primeros auxilios.

### **Módulo 11: `participacion_cultura.py` (8 Tácticas)**
57. Registro de comités paritarios (COPASST), actas y seguimiento de compromisos.
58. Gestión del buzón de reportes de actos y condiciones inseguras.
59. Planificación y seguimiento de campañas de cultura preventiva y bienestar.
60. Creación y gestión de encuestas de clima de seguridad.
61. Administración de programas de reconocimientos e incentivos.
62. Programación y registro de diálogos de seguridad trabajador-empresa.
63. Gestión de programas de liderazgo visible en seguridad para la gerencia.
64. Despliegue y seguimiento de protocolos de manejo de acoso laboral.

### **Módulo 12: `evaluaciones_diagnosticos.py` (4 Tácticas)**
65. Herramienta para ejecutar el diagnóstico inicial del SG-SST (línea base).
66. Checklist para la evaluación anual de cumplimiento legal y normativo.
67. Herramienta para la aplicación de la evaluación de riesgo psicosocial.
68. Metodología para la evaluación ergonómica de puestos de trabajo.

### **Módulo 13: `gestion_contratistas.py` (8 Tácticas)**
69. Homologación y registro documental de contratistas y proveedores.
70. Gestión de la inducción en SST para personal tercero.
71. Control digital de permisos de trabajo de alto riesgo para contratistas.
72. Evaluación periódica del desempeño en seguridad de contratistas.
73. Programación de auditorías de seguridad a proveedores críticos.
74. Registro y validación de subcontratistas autorizados.
75. Seguimiento en campo del cumplimiento de normas SST por contratista.
76. Evaluación anual de proveedores en el sistema de gestión.

### **Módulo 14: `programas_preventivos.py` (4 Tácticas)**
77. Gestión del programa de prevención de consumo de alcohol y drogas.
78. Gestión del programa de pausas activas y prevención ergonómica.
79. Gestión de campañas de promoción de la salud (nutrición, actividad física).
80. Gestión de programas de salud mental y manejo del estrés.

### **Módulo 15: `tecnologia_seguimiento_digital.py` (4 Tácticas)**
81. Desarrollo o integración de app móvil para reporte de incidentes.
82. Módulo de georreferenciación de riesgos en mapas de la planta o campo.
83. Plataforma de control y seguimiento de capacitaciones en modalidad e-learning.
84. Integración de firma electrónica en documentos clave del SST.

### **Módulo 16: `auditoria_mejora_continua.py` (4 Tácticas)**
85. Módulo para la programación y gestión de auditorías internas del SG-SST.
86. Registro y clasificación de hallazgos y no conformidades.
87. Creación y seguimiento de planes de acciones correctivas y preventivas (PAC/PAP).
88. Dashboard de seguimiento al ciclo de mejora continua (PHVA).

### **Módulo 17: `bienestar_laboral.py` (3 Tácticas)**
89. Desarrollo de estrategias y programas de balance vida-trabajo.
90. Creación de talleres de autocuidado y resiliencia para empleados.
91. (Este módulo puede expandirse con más tácticas de bienestar).

### **Módulo 18: `analitica_predictiva.py` (4 Tácticas)**
92. Implementación de dashboard predictivo de riesgos con Machine Learning.
93. Integración con sensores IoT (gases, temperatura, ruido, vibraciones).
94. Uso de Realidad Aumentada o VR para entrenamientos de alto riesgo.
95. Sistema de alertas automáticas (SMS/email) sobre riesgos críticos o desviaciones.
