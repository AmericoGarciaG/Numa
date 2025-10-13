
---
### **`LOGIC.md` - El Libro de Lógica de Numa (v0.1)**

**Producto:** Numa
**Versión de Lógica:** 0.1
**Misión del Producto:** Ser el asistente financiero más intuitivo que organiza las finanzas del usuario a través de la conversación, sin comprometer su privacidad.

---

#### **Parte I: Lógica del Núcleo de Transacciones**

**1. Entidades Fundamentales:**
    *   **`User`**: Representa al propietario de los datos financieros. Todo está asociado a un `User`.
    *   **`Transaction`**: Representa un único movimiento financiero (gasto o ingreso).
    *   **`SourceDocument`**: Representa el comprobante original de una transacción (imagen, PDF, etc.).

**2. Lógica de Creación de Transacciones (El Corazón de Numa):**

    *   **Regla 2.1 (Creación Provisional por Voz):**
        *   **Input:** Un comando de voz del `User` describiendo un gasto o ingreso.
        *   **Acción:**
            1.  El sistema debe transcribir el audio a texto.
            2.  Un LLM debe extraer del texto las entidades mínimas: `Monto` y `Concepto` (descripción).
            3.  Se debe crear una `Transaction` con el `Monto` y `Concepto` extraídos.
            4.  La `Transaction` debe tener el estado **`provisional`**.
            5.  El sistema debe confirmar verbalmente y por texto al usuario la creación de la transacción provisional.
        *   **Output:** Una nueva `Transaction` en estado `provisional`.

    *   **Regla 2.2 (Verificación por Comprobante):**
        *   **Input:** Un `SourceDocument` (ej. una imagen de un recibo) asociado a una `Transaction` `provisional`.
        *   **Acción:**
            1.  Un LLM multimodal debe analizar el `SourceDocument`.
            2.  El LLM debe extraer los datos detallados: `Monto Exacto`, `Comercio`, `Fecha`, `Hora`.
            3.  El sistema debe actualizar la `Transaction` existente con esta información precisa.
            4.  El estado de la `Transaction` debe cambiar de `provisional` a **`verified`**.
            5.  El `SourceDocument` debe quedar vinculado a la `Transaction`.
        *   **Output:** Una `Transaction` actualizada en estado `verified`.

    *   **Regla 2.3 (Creación Verificada Manualmente):**
        *   **Input:** Un comando de voz del `User` indicando que no existe comprobante.
        *   **Acción:**
            1.  Se sigue el flujo de la Regla 2.1 para crear la `Transaction` provisional.
            2.  Si el `User` confirma que no hay comprobante, el estado de la `Transaction` cambia inmediatamente a **`verified_manual`**.
        *   **Output:** Una nueva `Transaction` en estado `verified_manual`.

    *   **Regla 2.4 (Categorización Automática):**
        *   **Trigger:** Después de que una `Transaction` alcanza el estado `verified` o `verified_manual`.
        *   **Acción:**
            1.  El sistema debe usar un LLM para analizar el `Comercio` y el `Concepto` de la `Transaction`.
            2.  Basándose en el historial de categorización del `User` y en el conocimiento general, el LLM debe asignar una categoría (ej. "Supermercado", "Transporte", "Restaurantes").
            3.  Si es un comercio nuevo, la categoría sugerida debe ser presentada al `User` para confirmación la primera vez.
        *   **Output:** La `Transaction` actualizada con un campo `category`.

---

#### **Parte II: Lógica del Asistente Conversacional**

**3. Consultas Básicas de Gastos:**

    *   **Regla 3.1 (Consulta de Gasto Total):**
        *   **Input:** Una pregunta del `User` en lenguaje natural sobre sus gastos totales en un período de tiempo (ej. "¿Cuánto he gastado esta semana?").
        *   **Acción:**
            1.  El sistema debe interpretar la pregunta para identificar el `período de tiempo`.
            2.  Debe buscar todas las `Transactions` de tipo "gasto" para ese `User` dentro de ese período.
            3.  Debe sumar los `Montos` de las transacciones encontradas.
        *   **Output:** Una respuesta en lenguaje natural indicando el monto total gastado en el período solicitado.

    *   **Regla 3.2 (Consulta de Gasto por Categoría):**
        *   **Input:** Una pregunta del `User` sobre sus gastos en una categoría específica (ej. "¿Cuánto gasté en restaurantes este mes?").
        *   **Acción:**
            1.  El sistema debe interpretar la pregunta para identificar el `período de tiempo` y la `categoría`.
            2.  Debe buscar todas las `Transactions` de tipo "gasto" para ese `User` que coincidan con la `categoría` y el `período`.
            3.  Debe sumar los `Montos`.
        *   **Output:** Una respuesta en lenguaje natural con el monto total de la categoría.

---
