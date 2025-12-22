# Numa - Logic Book
## Arquitectura de Finanzas Soberanas (Protocolo Nexus)

**Versión:** 2.0 (Google Cloud Stack)
**Estado:** Activo
**Misión:** Asistente financiero Cero-Fricción potenciado por Google Cloud AI.

---

## PARTE I: Arquitectura del Sistema (Nexus)

### Capítulo 1: Módulos del Sistema
El sistema opera como un **Monolito Modular** en desarrollo local, diseñado para dividirse en microservicios en producción.

1.  **API Gateway (`src/modules/api_gateway`):**
    *   Punto de entrada HTTP (FastAPI).
    *   Gestiona autenticación y enruta peticiones a los módulos internos.
2.  **Finance Core (`src/modules/finance_core`):**
    *   Dueño de los datos (Usuarios, Transacciones).
    *   Gestiona la base de datos (SQLite local / Cloud SQL prod).
3.  **AI Brain (`src/modules/ai_brain`):**
    *   El conector con la inteligencia de Google.
    *   **No tiene estado (Stateless).** Solo procesa y devuelve.

---

## PARTE II: Contratos de Lógica de Negocio

### Capítulo 2: Flujo de Ingesta por Voz (The Nexus Flow)

#### 2.1. Entrada
*   El usuario sube un archivo de audio al endpoint `/transactions/voice`.

#### 2.2. Proceso de Transcripción (Google Chirp)
*   **Actor:** `AI Brain`.
*   **Acción:** Envía el audio crudo a la API **Google Cloud Speech-to-Text v2**.
*   **Modelo:** Debe solicitar explícitamente el modelo **"chirp"** (o "long") para español de México (`es-MX`).
*   **Salida:** Texto literal (String).

#### 2.3. Proceso de Razonamiento (Google Gemini)
*   **Actor:** `AI Brain`.
*   **Acción:** Envía el texto transcrito a **Gemini 1.5 Flash**.
*   **Prompt del Sistema:** "Eres un experto financiero. Extrae entidades en JSON estricto: `{amount, concept, merchant, date, category}`".
*   **Salida:** Objeto JSON validado.

#### 2.4. Persistencia
*   **Actor:** `Finance Core`.
*   **Acción:** Recibe el JSON del `AI Brain`.
*   **Regla:** Crea una transacción con estado **`PROVISIONAL`**.
*   **Validación:** El `amount` es obligatorio. Si Gemini no encuentra monto, marca la transacción como "Requiere Revisión".

---

## PARTE III: Requerimientos No Funcionales (NFRs)

### Capítulo 3: Operación Local y Costos

1.  **Credenciales:** El sistema debe fallar elegantemente ("Fail Fast") si la variable `GOOGLE_APPLICATION_CREDENTIALS` no apunta a un archivo JSON válido.
2.  **Latencia:** La transcripción y extracción combinadas no deben exceder los 10 segundos para audios cortos (< 30s).
3.  **Costos:** El uso de modelos "Flash" y "Chirp" debe priorizarse para mantener el consumo dentro de la capa gratuita o de bajo costo de GCP durante el desarrollo.

---