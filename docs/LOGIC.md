# Numa - Logic Book
## Arquitectura de Finanzas Soberanas (Protocolo Nexus)

**Versión:** 3.1 (Kybern FIM Standard)
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

#### 2.3. Reglas de Razonamiento – Taxonomía de Categorías
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

#### 2.4. Reglas de Persistencia e Integridad

1.  Integridad de Comercio:
    * Una transacción no puede pasar a estado `VERIFIED` o `VERIFIED_MANUAL` si `merchant` es NULL o cadena vacía.
    * En ese caso, la transacción debe permanecer en estado `PROVISIONAL` hasta que el comercio sea completado (por documento, corrección manual o confirmación por voz).

#### 2.2. Flujo de Procesamiento Lógico
Todo input (Voz o Texto) sigue este flujo orquestado:

1.  **Escucha (Ingesta):**
    *   Recepción de Audio (Whisper/Chirp) o Texto directo.
    *   Normalización de entrada.

2.  **Router Semántico (Clasificación):**
    *   **Actor:** `AI Brain`.
    *   **Acción:** Analiza el texto para determinar la `intent` (Taxonomía 2.1) y extraer `entities` relevantes.
    *   **Contrato de Salida (JSON):**
        ```json
        [
          {
            "intent": "WRITE_LOG",
            "sub_intent": "EXPENSE",
            "entities": {
                "amount": 500,
                "concept": "comida",
                "category": "Alimentación"
            },
            "confidence": 0.98
          }
        ]
        ```
    *   **Regla de Multiplicidad:** El Router SIEMPRE devuelve una lista (array) de objetos JSON, incluso si solo hay una intención detectada. Esto soporta "Gasté 100 en luz y 200 en agua".
    *   **Regla de Persistencia:** Para intenciones de tipo `WRITE_LOG`, el Orquestador debe iterar sobre cada elemento de la lista y crear una transacción independiente en `Finance Core`.

3.  **Ejecución Especializada (Routing):**
    *   **Actor:** `API Gateway` (Orquestador).
    *   **Acción:** Basado en el `intent`, despacha la petición al servicio correcto:
        *   `WRITE_LOG` -> `Finance Core` (Crear Transacción).
        *   `READ_QUERY` -> `Finance Core` (Query SQL Determinista) + `AI Brain` (Resumen natural).
        *   `ADVICE` -> `AI Brain` (RAG + Razonamiento).

4.  **Síntesis (Respuesta):**
    *   Generación de respuesta final al usuario (Texto + UI Data).
    *   Feedback visual acorde a la intención (ej. Tarjeta de Gasto vs. Gráfica de Reporte).

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
