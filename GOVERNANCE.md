
---

### **1. Texto para la "Regla Global" (Configuración del Agente)**

Copia y pega esto en la sección **"Rules" -> "+ Global"** de la configuración de Antigravity:

```text
DIRECTIVA PRIMARIA KYBERN:
1. Tu rol es actuar bajo el framework Kybern. Antes de planificar o ejecutar CUALQUIER cambio, DEBES leer el archivo `GOVERNANCE.md` en la raíz del proyecto.
2. `LOGIC.md` es la Fuente de Verdad inmutable. El código debe obedecer a la lógica, no al revés.
3. PRESERVACIÓN CRÍTICA: JAMÁS elimines, muevas o sobrescribas los archivos `GOVERNANCE.md`, `LOGIC.md`, `ROADMAP.md` o `.env` a menos que se te instruya explícitamente para actualizarlos. Estos archivos deben permanecer en la raíz o en `docs/`.
4. ESTÁNDAR NEXUS: El código fuente reside exclusivamente en `/src`. No crees carpetas de lógica en la raíz.
```

---

### **2. Archivo: `GOVERNANCE.md` (Versión Nexus Protocol)**

Este archivo define las nuevas reglas del juego (Google Stack + Monolito Modular). Guárdalo en la **raíz** del proyecto.

```markdown
# GOVERNANCE.md (Nexus Protocol Edition)

**Agent:** Antigravity
**Framework:** Kybern (DBBD + DirGen)
**Architecture:** Protocolo Nexus (Monolito Modular Local)
**Stack:** Google Cloud Native (Gemini + Chirp)

---

#### **1. Prime Directive: La Constitución del Código**
Tu propósito es traducir contratos lógicos inmutables en implementaciones técnicas. No asumes, verificas.

#### **2. Source of Truth (Fuente de Verdad)**
Existe un único documento que gobierna el comportamiento del sistema.
*   **Archivo:** `docs/LOGIC.md` (o en la raíz `LOGIC.md`).
*   **Regla:** Si el código contradice al LOGIC.md, el código es un bug.

#### **3. El Estándar "Protocolo Nexus"**

1.  **Estructura de Directorios (Inmutable):**
    *   Todo el código fuente vive en `/src`.
    *   `src/core`: Utilidades transversales (BD, Config, Auth).
    *   `src/modules/{dominio}`: Cajas negras lógicas.

2.  **Regla de Oro de la Comunicación:**
    *   Un módulo **NUNCA** debe importar modelos o lógica interna de otro módulo.
    *   La comunicación entre módulos ocurre **exclusivamente** a través de la función pública definida en `src/modules/{dominio}/service.py` (o `connector.py`).
    *   *Objetivo:* Facilitar la futura separación a microservices sin refactorizar lógica interna.

3.  **Stack Tecnológico (Google-Only):**
    *   **Inferencia (Razonamiento):** Google Gemini 1.5 Flash (vía `google-generativeai`).
    *   **Audio (Transcripción):** Google Cloud Speech-to-Text v2 "Chirp" (vía `google-cloud-speech`).
    *   **Infraestructura Local:** Ejecución directa con `python src/main.py`. Sin Docker para desarrollo diario.
    *   **Frontend (Regla de Fase 2):** "Frontend Ligero". Para el MVP Local, la UI se sirve como archivos estáticos (HTML/JS/CSS) desde `src/modules/web_ui` a través de FastAPI. No se permiten servidores de desarrollo separados (e.g. `npm run dev`) en esta fase.

#### **4. Protocolo de Ejecución**

1.  **Leer:** Consulta `LOGIC.md` para entender el requerimiento.
2.  **Verificar:** Revisa `requirements.txt` y `.env` para asegurar dependencias.
3.  **Implementar:** Escribe código limpio, tipado y documentado en `/src`.
4.  **Proteger:** Nunca borres documentación ni configuración de entorno.

---
**Mantra:** *La Lógica dirige, la Implementación obedece.*
```

---

### **3. Archivo: `LOGIC.md` (Versión Nexus Protocol)**

Este archivo define el flujo de negocio utilizando las herramientas de Google. Sugiero crear una carpeta `docs/` en la raíz y guardarlo allí como `docs/LOGIC.md` (o en la raíz si prefieres).

```markdown
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
```

**Siguientes pasos:**
1.  Agrega la Regla Global en Antigravity.
2.  Crea/Restaura `GOVERNANCE.md` en la raíz.
3.  Crea `docs/` y guarda allí `LOGIC.md`.
4.  (Opcional) Restaura `ROADMAP.md` y `ONBOARDING.md` en la raíz si también se perdieron.

Una vez hecho esto, podemos volver a ejecutar el **Prompt #1** (Reestructuración de carpetas) con la confianza de que el agente respetará estos documentos vitales.