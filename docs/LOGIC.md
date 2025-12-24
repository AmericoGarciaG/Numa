# Numa - Logic Book
## Arquitectura de Finanzas Soberanas (Protocolo Nexus)

**Versión:** 3.2 (Kybern Deterministic Tree)
**Estado:** Activo
**Misión:** Actuar como un Director Financiero Personal (CFO) que interpreta el diálogo financiero del usuario para registrar, consultar, planificar y aconsejar, manteniendo la soberanía de los datos.

---

## PARTE I: Arquitectura del Sistema (Nexus)

### Capítulo 1: Módulos del Sistema
El sistema opera como un **Monolito Modular** en desarrollo local, diseñado para dividirse en microservicios en producción.

1.  **API Gateway (`src/modules/api_gateway`):**
    *   Punto de entrada HTTP (FastAPI).
    *   Gestiona autenticación y enruta peticiones a los módulos internos.
    *   **Responsabilidad Nueva:** Orquestar el flujo basado en la intención detectada (Router).
2.  **Finance Core (`src/modules/finance_core`):**
    *   Dueño de los datos (Usuarios, Transacciones, Cuentas, Metas).
    *   Gestiona la base de datos (SQLite local / Cloud SQL prod).
3.  **AI Brain (`src/modules/ai_brain`):**
    *   El conector con la inteligencia de Google.
    *   **No tiene estado (Stateless).** Solo procesa y devuelve.
    *   **Responsabilidad Nueva:** Clasificación semántica de intenciones (FIM).

---

## PARTE II: Contratos de Lógica de Negocio

### Capítulo 2: El Motor de Intención Financiera (FIM)

El sistema evoluciona de un simple receptor de comandos a un motor conversacional capaz de entender el contexto y la intención del usuario.

#### 2.1. Taxonomía de Intenciones
El sistema debe clasificar cualquier entrada del usuario en una de las siguientes intenciones principales:

1.  **Registro (Write/Log):**
    *   **Definición:** Declarar un hecho financiero que altera el estado del balance.
    *   **Ejemplos:** "Gasté 500 en comida", "Me pagaron la quincena", "Le debo 200 a Juan".
    *   **Subtipos:** `EXPENSE` (Gasto), `INCOME` (Ingreso), `DEBT` (Deuda).
    *   **Requisito Estricto:** Debe contener simultáneamente un concepto identificable y un monto explícito. Si falta el monto o el concepto, la entrada no se considera un WRITE_LOG ejecutable sino una solicitud de aclaración.

2.  **Consulta (Read/Query):**
    *   **Definición:** Pedir información del estado financiero actual o histórico.
    *   **Ejemplos:** "¿Cuánto he gastado hoy?", "¿Tengo dinero para salir?", "Dame mi balance del mes".
    *   **Salida:** Reportes, agregaciones, listas filtradas.

3.  **Planificación (Strategy/Future):**
    *   **Definición:** Definir una meta, presupuesto o intención a futuro.
    *   **Ejemplos:** "Quiero ahorrar para un viaje", "Avísame si gasto más de 1000 en Uber", "Crea un presupuesto de comida".

4.  **Consultoría (Reasoning/Advice):**
    *   **Definición:** Buscar sabiduría, análisis complejo o recomendaciones.
    *   **Ejemplos:** "¿Debería comprar esto?", "¿Cómo puedo ahorrar más?", "Analiza mis gastos hormiga".

5.  **Redirección (Steering):**
    *   **Definición:** Pivotar conversaciones no financieras hacia el dominio financiero o manejar saludos/errores.
    *   **Ejemplos:** "Hola", "¿Quién eres?", "Cuéntame un chiste" (Redirigir a finanzas).

6.  **Confirmación/Actualización (Confirm/Update - `CONFIRM_UPDATE`):**
    *   **Definición:** Confirmar o corregir información de transacciones ya registradas (típicamente provisionales).
    *   **Ejemplos:** "Confirmo todo", "El gasto de 500 fue en Walmart", "Cambia la categoría a Salud".

#### 2.3. Reglas de Inteligencia – Taxonomía de Categorías
El sistema utiliza una taxonomía cerrada de categorías. Toda transacción debe mapearse estrictamente a una de estas etiquetas:

1.  Esenciales:
    *   `Vivienda`
    *   `Servicios`
    *   `Despensa`
    *   `Transporte`
    *   `Salud`
    *   `Educación`
2.  Discrecionales:
    *   `Restaurantes`
    *   `Café/Snacks`
    *   `Ocio`
    *   `Compras`
    *   `Regalos`
3.  Movimientos financieros:
    *   `Deuda`
    *   `Inversión`
    *   `Ingreso`
    *   `Transferencia`

Regla de gastos hormiga:
* Si el gasto es pequeño (< $200 MXN) y ocurre en cafeterías, tiendas de conveniencia o kioscos, el sistema debe priorizar la clasificación como `Café/Snacks` o `Compras` para facilitar el análisis de gastos hormiga.

Reglas de inteligencia para entradas ambiguas (`AMBIGUOUS`):

1.  Una entrada se considera ambigua cuando el usuario solo pronuncia una palabra de tipo (`gasto`, `ingreso`, `deuda`) sin un objeto o concepto asociado (por ejemplo: "gasto", "ingreso", "deuda" como única palabra significativa).
2.  En estos casos, el Motor de Intención Financiera NO crea ninguna transacción ni infiere categorías. En su lugar, genera una respuesta de aclaración pidiendo detalles adicionales (ejemplo: "¿De qué fue el gasto y cuánto costó?").
3.  Mientras el input permanezca en estado `AMBIGUOUS`, el sistema debe comportarse como un chat guiado: solo hace preguntas de seguimiento hasta obtener un concepto concreto y opcionalmente un monto.

#### 2.4. Reglas de Persistencia e Integridad

1.  Integridad de Comercio:
    * Una transacción no puede pasar a estado `VERIFIED` o `VERIFIED_MANUAL` si `merchant` es NULL o cadena vacía.
    * En ese caso, la transacción debe permanecer en estado `PROVISIONAL` hasta que el comercio sea completado (por documento, corrección manual o confirmación por voz).

#### 2.2. Flujo de Procesamiento Lógico – Algoritmo de Decisión en Cascada
Todo input (Voz o Texto) pasa por un árbol de decisión determinista de 3 niveles. El objetivo es que, para cada entrada, exista exactamente un camino posible (función biyectiva sobre el espacio de estados).

**Paso 1 – Escucha y Transcripción:**
    *   El audio DEBE ser transformado a texto por el servicio de Transcripción (STT) dedicado antes de cualquier razonamiento.
    *   La única fuente de verdad para el motor de intención es el texto transcrito; el audio crudo no se usa como canal de razonamiento.

**Regla de fallo de transcripción:**
    *   Si el servicio de transcripción no retorna texto inteligible (silencio, ruido, cadena vacía o marcador de error), el flujo DEBE detenerse en este punto y notificar un error claro al usuario.
    *   Queda PROHIBIDO enviar audio crudo directamente al modelo de razonamiento (LLM, Gemini u otro) como mecanismo de fallback.

1.  **Nivel 1 – Validez (Filtro de ruido/vacío):**
    *   Detecta entradas vacías, ruido de fondo o texto sin contenido semántico suficiente (ej. silencio, onomatopeyas, cadenas muy cortas sin palabras significativas).
    *   Si el input se considera inválido, el sistema NO continúa a niveles siguientes.
    *   **Salida:** Respuesta de chat amigable explicando que no se entendió la instrucción y pidiendo que el usuario repita con más claridad.

2.  **Nivel 2 – Dominio (Clasificación Macro):**
    *   Clasifica la entrada en uno de tres dominios:
        *   `META`: Comandos de sistema o configuración (ej. "cambia el idioma", "borra mis datos", "reinicia la sesión").
        *   `SOCIAL`: Conversación general o social no directamente financiera (ej. "hola", "¿quién eres?", "cuéntame un chiste").
        *   `FINANCIERO`: Cualquier frase que haga referencia a dinero, gastos, ingresos, deudas, presupuestos o reportes.
    *   Solo las entradas clasificadas como `FINANCIERO` pasan al Nivel 3 de resolución financiera. `META` y `SOCIAL` se resuelven en el plano conversacional (chat) sin tocar `Finance Core`.

3.  **Nivel 3 – Resolución Financiera (Sub-clasificación estricta):**
    *   Este nivel solo aplica si el dominio es `FINANCIERO` y decide exactamente uno de estos estados:
        *   `READ` (Consulta):
            *   El usuario pide información sobre su historial o estado actual (ej. "¿Cuánto he gastado hoy?", "¿Tengo saldo para salir?").
            *   **Ruta:** Lectura determinista en `Finance Core` + posible humanización por `AI Brain`.
        *   `AMBIGUOUS` (Registro incompleto):
            *   El usuario expresa intención de registrar algo pero sin suficiente resolución semántica (ej. una sola palabra como "gasto" o "ingreso" sin objeto).
            *   **Ruta:** NO se crea ninguna transacción. El sistema responde con preguntas aclaratorias para obtener concepto y, si es posible, monto.
        *   `WRITE` (Registro válido):
            *   El usuario describe un movimiento con al menos un concepto identificable (ej. "camisa", "licuadora", "pago de luz") Y un monto explícito.
            *   Regla de monto: si existe concepto pero no se menciona un monto explícito, la entrada NO debe producir ninguna transacción y se trata como una solicitud de aclaración para completar los datos.
    *   Cada input financiero debe caer exactamente en uno de estos tres estados (`READ`, `AMBIGUOUS`, `WRITE`) sin solapamientos ni aleatoriedad.

---

## PARTE III: Modelo de Datos (Finance Core)

### Capítulo 3: Modelo de Dominio Financiero

El modelo de datos se expande para soportar una visión 360° de las finanzas personales.

#### 3.1. Entidad `Transaction` (Actualizada)
Representa un movimiento atómico de dinero.

*   `id`: UUID
*   `user_id`: UUID (FK)
*   `type`: Enum (`EXPENSE`, `INCOME`, `DEBT`) **[NUEVO]**
*   `amount`: Decimal
*   `concept`: String
*   `category`: String
*   `merchant`: String (Opcional)
*   `status`: Enum (`PROVISIONAL`, `VERIFIED`, `VERIFIED_MANUAL`)
*   `transaction_date`: DateTime
*   `created_at`: DateTime

#### 3.2. Entidad `Account` (Placeholder - Futuro)
Representa un contenedor de valor.
*   `id`: UUID
*   `name`: String (ej. "Banamex Débito", "Efectivo")
*   `type`: Enum (`BANK`, `CASH`, `CREDIT`, `INVESTMENT`)
*   `current_balance`: Decimal

#### 3.3. Entidad `Goal` (Placeholder - Futuro)
Representa un objetivo financiero.
*   `id`: UUID
*   `name`: String
*   `target_amount`: Decimal
*   `current_amount`: Decimal

---

## PARTE IV: Requerimientos No Funcionales (NFRs)

### Capítulo 4: Operación Local y Costos

1.  **Credenciales:** El sistema debe fallar elegantemente ("Fail Fast") si la variable `GOOGLE_APPLICATION_CREDENTIALS` no apunta a un archivo JSON válido.
2.  **Latencia:** La clasificación de intención debe ser < 500ms. La transcripción y ejecución total < 5s.
3.  **Costos:** Priorizar modelos "Flash" y "Chirp".
4.  **4.4 Integridad de Input:** El Router Semántico y los Agentes de Ejecución solo operan sobre input textual normalizado (JSON/String). Ningún componente de negocio debe tener acceso al archivo de audio original.

---

## PARTE V: Contrato de Interfaz de Usuario (Web Client)

### Capítulo 5: Flujo de Interacción del Usuario
Para el MVP (Fase 2), la interfaz es una **Web App Ligera** servida por el mismo backend.

#### 5.1. Flujo de Captura de Voz
La interacción principal ("Hoyo en Uno") debe ser extremadamente fluida:

1.  **Estado Inicial (Ready):**
    *   Botón de micrófono prominente.
2.  **Estado Grabando (Recording):**
    *   Feedback visual claro (pulsación roja).
    *   **Técnico:** Forzar `audio/webm` o detectar el mejor formato soportado.
3.  **Estado Procesando (Processing):**
    *   Feedback de Progreso: "Escuchando..." -> "Entendiendo intención..." -> "Ejecutando..."

#### 5.2. Respuesta Adaptativa
La UI debe adaptarse a la intención detectada:
*   **Intención WRITE:** Mostrar tarjetas de confirmación para cada transacción creada.
*   **Intención READ:** Mostrar dato solicitado (ej. "Gastaste $500") + Gráfica opcional.
*   **Intención ADVICE:** Mostrar respuesta de texto en formato chat.
