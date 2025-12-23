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

#### 2.2. Proceso de Transcripción (Google Chirp V2)
*   **Actor:** `AI Brain`.
*   **Acción:** Envía el audio crudo a la API **Google Cloud Speech-to-Text v2**.
*   **Modelo:** Se utiliza el modelo **`latest_long`** (Reconocedor V2) para soporte óptimo de español de México (`es-MX`). El modelo "chirp" puede estar restringido por regiones.
*   **Salida:** Texto literal (String).

#### 2.3. Proceso de Razonamiento (Google Vertex AI)
*   **Actor:** `AI Brain`.
*   **Acción:** Envía el texto transcrito al modelo **Gemini 2.0 Flash Experimental** (`gemini-2.0-flash-exp`) a través de Vertex AI.
*   **Prompt del Sistema:** "Eres un experto financiero. Extrae entidades en JSON estricto: `{amount, concept, merchant, date, category}`".
*   **Nota Técnica:** Se prefiere Vertex AI sobre AI Studio (`google.generativeai`) para compatibilidad robusta con cuentas de servicio.
*   **Salida:** Objeto JSON validado.

#### 2.4. Persistencia
*   **Actor:** `Finance Core`.
*   **Acción:** Recibe el JSON del `AI Brain`.
*   **Regla:** Crea una transacción con estado **`PROVISIONAL`**.
*   **Mejora de Inteligencia:** Si el modelo detecta `merchant` (Comercio), `category` (Categoría) o `date` con confianza, **ESTOS DATOS SE PERSISTEN** inmediatamente en el registro provisional. No se deben descartar.
*   **Validación:** El `amount` es estricamente obligatorio. Si no existe, se marca error o se requiere intervención manual.

---

## PARTE III: Requerimientos No Funcionales (NFRs)

### Capítulo 3: Operación Local y Costos

1.  **Credenciales:** El sistema debe fallar elegantemente ("Fail Fast") si la variable `GOOGLE_APPLICATION_CREDENTIALS` no apunta a un archivo JSON válido.
2.  **Latencia:** La transcripción y extracción combinadas no deben exceder los 10 segundos para audios cortos (< 30s).
3.  **Costos:** El uso de modelos "Flash" y "Chirp" debe priorizarse para mantener el consumo dentro de la capa gratuita o de bajo costo de GCP durante el desarrollo.

---

## PARTE IV: Contrato de Interfaz de Usuario (Web Client)

### Capítulo 4: Flujo de Interacción del Usuario
Para el MVP (Fase 2), la interfaz es una **Web App Ligera** servida por el mismo backend.

#### 4.1. Flujo de Captura de Voz
La interacción principal ("Hoyo en Uno") debe ser extremadamente fluida:

1.  **Estado Inicial (Ready):**
    *   Botón de micrófono prominente y central.
    *   Texto auxiliar: "Presiona para registrar un gasto".
2.  **Estado Grabando (Recording):**
    *   Feedback visual claro (onda de audio o pulsación roja).
    *   La captura de audio sucede en el navegador usando **MediaRecorder API**.
    *   Botón cambia a acción "Detener / Enviar".
3.  **Estado Procesando (Processing):**
    *   **Bloqueo de UI:** El usuario no debe poder grabar otra vez mientras se procesa.
    *   **Feedback de Progreso:** Mostrar mensajes de estado derivados de la latencia esperada:
        *   "Enviando audio..." -> "Transcribiendo (Google Chirp)..." -> "Analizando (Gemini)..."

#### 4.2. Visualización de Resultados
Cuando el backend responde con **201 Created**:
*   **NO mostrar JSON crudo.**
*   Renderizar una **"Tarjeta de Transacción"** o notificación temporal con:
    *   **Concepto:** Título principal (ej. "Cena").
    *   **Monto:** Destacado grande (ej. "$350.00").
    *   **Categoría:** Badge/Etiqueta de color (ej. "Alimentación").
    *   **Fecha:** Discreta (ej. "Hoy").

#### 4.3. Reporte en Tiempo Real
*   **Auto-Refresh:** Inmediatamente después de una inserción exitosa, la UI debe consultar el endpoint `GET /api/transactions` (o actualizar su estado local) para reflejar el nuevo gasto en la lista histórica / dashboard sin que el usuario recargue la página.
