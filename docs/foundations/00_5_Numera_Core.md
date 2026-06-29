# NUMERA

## Documento 00.5 — Numera Core

**Versión:** 0.1  
**Estado:** Draft  
**Fecha:** 26 de junio de 2026  
**Documento relacionado:** 00_Vision_and_Philosophy.md  

---

# 1. Propósito del documento

Este documento define cómo debe pensar Numera.

No describe únicamente funcionalidades, pantallas o tecnologías. Describe el modelo cognitivo del sistema: la forma en la que Numera comprende información, recuerda contexto, razona, planifica, actúa, reflexiona y aprende.

Numera no debe ser un software tradicional al que se le añade inteligencia artificial como complemento. Numera debe ser una plataforma diseñada alrededor de la inteligencia artificial desde su origen.

Este documento servirá como referencia para el Product Requirements Document, la arquitectura técnica, el modelo de datos, el sistema de agentes, la experiencia de usuario y la estrategia de aprendizaje.

---

# 2. Principio rector

> Understand before automating.

Numera no debe automatizar un proceso que no comprende.

Antes de ejecutar una acción, Numera debe ser capaz de explicar qué información ha utilizado, qué contexto conoce, qué reglas ha aplicado, qué nivel de confianza tiene y qué riesgos existen.

La automatización sin comprensión genera errores invisibles. Numera debe evitar ese riesgo.

---

# 3. Lema externo

> Turn data into decisions.

El cliente no compra OCR, inteligencia artificial ni contabilidad automática.

El cliente compra mejores decisiones, menos errores y más tiempo disponible.

Numera debe transformar documentos, datos y eventos financieros en información útil para decidir.

---

# 4. Numera como sistema AI Native

Numera no será un ERP con IA añadida.

Numera será una capa de inteligencia financiera diseñada alrededor de un núcleo cognitivo.

La arquitectura conceptual será:

```text
Usuario
  ↓
Numera Core
  ↓
AI Orchestrator
  ↓
Knowledge Graph + Memory Engine
  ↓
Agentes especializados
  ↓
Servicios operativos
  ↓
ERP, Excel, bancos, AEAT e integraciones externas
```

La IA no será una función aislada. Será el mecanismo que coordina la comprensión, el razonamiento, la memoria, el aprendizaje y la ejecución.

---

# 5. Capacidades cognitivas principales

Numera Core se compone de siete capacidades fundamentales:

1. Understand
2. Remember
3. Reason
4. Plan
5. Execute
6. Reflect
7. Learn

Estas capacidades forman el ciclo cognitivo de Numera.

```text
Understand → Remember → Reason → Plan → Execute → Reflect → Learn
```

---

# 6. Understand — Comprender

Numera debe comprender antes de actuar.

Comprender significa identificar qué tipo de información se ha recibido, qué entidades participan, qué datos son fiables, qué datos faltan y qué implicaciones puede tener el documento o evento analizado.

Ejemplos de comprensión:

- detectar que un documento es una factura de compra;
- identificar proveedor, fecha, número de factura, base imponible, IVA y total;
- distinguir una factura de un albarán, un ticket, un contrato o un extracto bancario;
- reconocer si una factura pertenece a un proveedor habitual o nuevo;
- identificar si existen datos inconsistentes.

Numera no debe tratar los documentos como archivos. Debe tratarlos como eventos empresariales.

---

# 7. Remember — Recordar

La memoria es una de las capacidades diferenciales de Numera.

Numera no debe limitarse a procesar documentos de forma aislada. Debe recordar el contexto histórico de cada empresa.

La memoria empresarial debe incluir:

- proveedores habituales;
- clientes habituales;
- cuentas contables usadas anteriormente;
- correcciones realizadas por usuarios;
- incidencias pasadas;
- instrucciones específicas;
- preferencias de contabilización;
- excepciones recurrentes;
- patrones de pago;
- comportamiento histórico de precios;
- notas y decisiones internas.

Ejemplo:

Si un usuario indica que un proveedor debe revisarse siempre por incidencias previas, Numera deberá recordar esa instrucción y aplicarla en futuras facturas.

La memoria no debe ser opaca. El usuario debe poder consultar, editar, eliminar o desactivar recuerdos relevantes.

---

# 8. Reason — Razonar

Numera debe razonar sobre la información disponible.

Razonar significa conectar datos actuales con reglas, memoria, conocimiento contable y contexto empresarial.

Ejemplo de razonamiento:

- El proveedor es Vodafone.
- En 24 facturas anteriores se contabilizó como suministro telefónico.
- La cuenta habitual fue 628000.
- El IVA habitual fue 21%.
- El importe está dentro del rango esperado.
- No existen duplicados.

Conclusión:

Numera propone contabilizar la factura en la cuenta 628000 con un nivel alto de confianza.

Todo razonamiento debe ser explicable.

---

# 9. Plan — Planificar

Antes de actuar, Numera debe decidir el mejor flujo de acción.

Planificar significa determinar si una tarea puede ejecutarse automáticamente, si requiere revisión humana, si necesita información adicional o si debe bloquearse.

Ejemplos:

- contabilizar automáticamente una factura de bajo riesgo;
- dejar pendiente una factura con IVA inconsistente;
- solicitar al usuario una cuenta contable cuando no exista historial;
- marcar como posible duplicado una factura similar a otra ya registrada;
- dividir una factura compleja en varias líneas contables.

La planificación debe considerar riesgo, confianza, impacto y reversibilidad.

---

# 10. Execute — Actuar

Numera solo debe actuar cuando tenga permiso, confianza suficiente y una acción segura.

Acciones posibles:

- crear una propuesta de asiento;
- exportar datos;
- registrar una factura;
- marcar una incidencia;
- generar un informe;
- enviar una recomendación;
- actualizar una regla aprendida;
- integrarse con un ERP externo.

Las acciones críticas deberán requerir validación humana.

Numera nunca debe ejecutar acciones fiscales, bancarias o contables irreversibles sin autorización explícita.

---

# 11. Reflect — Reflexionar

Después de actuar, Numera debe evaluar el resultado.

La reflexión responde a preguntas como:

- ¿La propuesta fue aceptada?
- ¿El usuario la corrigió?
- ¿Qué parte fue modificada?
- ¿La confianza inicial era adecuada?
- ¿Debe ajustarse una regla?
- ¿Debe generarse un recuerdo?
- ¿Debe marcarse una excepción?

La reflexión convierte la experiencia en aprendizaje.

Sin reflexión, Numera solo procesa. Con reflexión, Numera mejora.

---

# 12. Learn — Aprender

Numera debe aprender de cada interacción relevante.

El aprendizaje puede producirse por:

- correcciones de usuarios;
- aprobaciones repetidas;
- rechazos;
- patrones históricos;
- incidencias detectadas;
- reglas creadas manualmente;
- comportamiento financiero recurrente.

El aprendizaje debe ser trazable.

Cada regla aprendida deberá indicar:

- origen;
- fecha;
- usuario o evento que la generó;
- ámbito de aplicación;
- nivel de confianza;
- posibilidad de revertirse.

Numera no debe aprender de forma descontrolada. Debe aprender de forma gobernada.

---

# 13. Knowledge Graph

El Knowledge Graph será la representación estructurada del conocimiento empresarial.

No solo almacenará datos. Representará relaciones.

Ejemplo:

```text
Proveedor → Facturas → Productos → Cuentas contables → IVA → Pagos → Incidencias
```

Este grafo permitirá responder preguntas complejas:

- ¿Qué proveedores han subido precios?
- ¿Qué gastos han aumentado sin explicación?
- ¿Qué clientes pagan tarde?
- ¿Qué facturas tienen IVA anómalo?
- ¿Qué cuentas contables se usan de forma inconsistente?

El Knowledge Graph será una pieza central de Numera Core.

---

# 14. Memory Engine

El Memory Engine será responsable de conservar contexto empresarial útil.

No toda información debe convertirse en memoria.

Una memoria debe ser:

- útil;
- verificable;
- trazable;
- editable;
- segura;
- contextual.

Tipos de memoria:

1. Memoria de proveedor.
2. Memoria de cliente.
3. Memoria contable.
4. Memoria fiscal.
5. Memoria de incidencias.
6. Memoria de usuario.
7. Memoria de empresa.
8. Memoria de instrucciones explícitas.

Ejemplo de memoria:

```text
Proveedor: Vodafone
Tipo: Incidencia recurrente
Instrucción: Revisar antes de contabilizar
Origen: Usuario
Fecha: 2026-06-26
Estado: Activa
```

---

# 15. AI Orchestrator

El AI Orchestrator coordinará los agentes especializados.

Su función no será hacer todo, sino decidir qué agente debe intervenir en cada momento.

Agentes iniciales:

- Document Agent;
- Accounting Agent;
- Tax Agent;
- Audit Agent;
- Banking Agent;
- Finance Agent;
- Memory Agent;
- Learning Agent;
- Integration Agent;
- Conversation Agent.

Cada agente tendrá responsabilidades delimitadas.

Ningún agente deberá actuar fuera de su ámbito sin supervisión del orquestador.

---

# 16. Niveles de confianza

Toda propuesta de Numera deberá incluir un nivel de confianza.

Ejemplo:

```text
Confianza 98% → puede automatizarse si la empresa lo permite.
Confianza 85% → puede proponerse con aviso.
Confianza 65% → requiere revisión humana.
Confianza <50% → no debe ejecutarse.
```

Los umbrales exactos deberán definirse por módulo, tipo de acción y política de la empresa.

La confianza nunca sustituye a la trazabilidad.

---

# 17. Riesgo y reversibilidad

Toda acción deberá evaluarse según su riesgo y reversibilidad.

Acciones de bajo riesgo:

- clasificar un documento;
- generar una sugerencia;
- preparar un asiento no aprobado;
- crear una alerta.

Acciones de riesgo medio:

- registrar una factura;
- modificar una regla;
- exportar información a un ERP.

Acciones de alto riesgo:

- enviar información fiscal;
- modificar contabilidad cerrada;
- ejecutar pagos;
- eliminar información crítica.

Las acciones de alto riesgo deberán requerir autorización explícita.

---

# 18. Human-in-the-loop

Numera debe mantener a la persona dentro del proceso cuando sea necesario.

El objetivo no es eliminar al usuario. El objetivo es evitar que el usuario pierda tiempo en tareas mecánicas.

El usuario debe intervenir cuando:

- el nivel de confianza sea bajo;
- exista riesgo relevante;
- falte información crítica;
- haya conflicto entre reglas;
- se detecte una anomalía;
- la decisión tenga impacto fiscal, legal o financiero relevante.

---

# 19. Auditoría y trazabilidad

Cada decisión importante debe quedar registrada.

El sistema debe poder responder:

- qué ocurrió;
- cuándo ocurrió;
- quién lo aprobó;
- qué datos se usaron;
- qué regla se aplicó;
- qué modelo intervino;
- qué nivel de confianza había;
- si hubo corrección posterior.

La trazabilidad no es opcional. Es parte del producto.

---

# 20. Conclusión

Numera Core define el cerebro del sistema.

Numera no debe limitarse a leer facturas ni a proponer asientos contables.

Debe comprender, recordar, razonar, planificar, actuar, reflexionar y aprender.

La memoria empresarial será una ventaja competitiva clave.

La arquitectura AI Native permitirá construir un producto diferente a un ERP tradicional.

La frase que guiará el diseño interno será:

> Understand before automating.

La frase que comunicará el valor externo será:

> Turn data into decisions.

Este documento queda establecido como referencia para los siguientes documentos del proyecto, especialmente el PRD, la arquitectura técnica, el diseño de IA y el modelo de datos.
