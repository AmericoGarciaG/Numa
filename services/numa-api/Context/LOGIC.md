# Numa - Logic Book (Protocolo Nexus Edition)
## Arquitectura de Finanzas Soberanas y Experiencia Cero-Fricción

**Versión:** 2.0 (Protocolo Nexus - Modular Monolith)
**Estado:** Activo y Vinculante
**Última Actualización:** 2025-12-21
**Misión del Sistema:** Eliminar la fricción de la gestión financiera personal mediante una interfaz conversacional y multimodal, garantizando privacidad absoluta (Sovereign AI) y rigor contable.

---

## PARTE I: Visión y Arquitectura Nexus

### Capítulo 1: Filosofía del Sistema
Numa invierte la carga de trabajo: el usuario "arroja evidencia" (caos), y el sistema "produce contabilidad" (orden).

**Principio Fundamental:** El sistema es un **Monolito Modular** diseñado para migrar trivialmente a microservicios. Los módulos son "Cajas Negras Lógicas" dentro de un solo repositorio, comunicándose exclusivamente a través de interfaces públicas.

---

### Capítulo 2: Arquitectura de Cajas Negras Lógicas (Módulos Nexus)

El sistema se compone de **tres módulos soberanos** bajo el Protocolo Nexus. La implementación interna es fungible; la comunicación externa es contractual.

#### 2.1. Gateway (El Orquestador de Negocio)
**Ubicación:** `/src/modules/gateway/`

**Responsabilidades:**
- Gestión de estado persistente (Base de Datos)
- Autenticación y autorización (JWT)
- Orquestación de flujos de negocio
- Exposición de API REST/GraphQL al cliente

**Restricciones:**
- ❌ **PROHIBIDO:** Realizar inferencia de IA directamente
- ❌ **PROHIBIDO:** Importar modelos internos de otros módulos
- ✅ **OBLIGATORIO:** Delegar procesamiento de IA al módulo `AIBrain`
- ✅ **OBLIGATORIO:** Filtrar todas las consultas DB por `user_id` (JWT)

**Interfaz Pública (`service.py`):**
```python
def orchestrate_voice_transaction(user_id: int, audio_file: bytes) -> Transaction
def orchestrate_document_verification(user_id: int, transaction_id: int, document: bytes) -> Transaction
def get_user_transactions(user_id: int, filters: dict) -> List[Transaction]
```

---

#### 2.2. AIBrain (El Cerebro de Inferencia)
**Ubicación:** `/src/modules/ai_brain/`

**Responsabilidades:**
- Abstraer la complejidad de los servicios de Google AI
- Transcripción de audio (Google Chirp)
- Extracción de datos estructurados (Google Gemini)
- Clasificación y análisis multimodal

**Restricciones:**
- ❌ **PROHIBIDO:** Acceder a la base de datos
- ❌ **PROHIBIDO:** Mantener estado de usuario
- ❌ **PROHIBIDO:** Usar servicios no-Google (OpenAI, Anthropic, Ollama)
- ✅ **OBLIGATORIO:** Stateless (solo procesa ventana de contexto inmediata)
- ✅ **OBLIGATORIO:** Usar credenciales `GOOGLE_APPLICATION_CREDENTIALS`

**Interfaz Pública (`service.py`):**
```python
def transcribe_audio(audio_bytes: bytes, language: str = "es-MX") -> str
def extract_transaction_data(text: str) -> TransactionData  # {amount, concept}
def analyze_document(image_bytes: bytes) -> DocumentData  # {vendor, date, total_amount}
def classify_category(concept: str, merchant: str = None) -> str
def answer_query(query: str, context: dict) -> str
```

**Contratos de Servicio Google:**

##### 2.2.1. Google Chirp (Speech-to-Text v2)
- **Entrada:** Audio bytes (formato: WAV, MP3, FLAC)
- **Salida:** Texto transcrito (string)
- **Modelo:** `chirp` o `latest_long` (Universal Speech Model)
- **Configuración:** `language_code="es-MX"`, `enable_automatic_punctuation=True`

##### 2.2.2. Google Gemini 1.5 Flash
- **Entrada:** Texto o imagen + prompt estructurado
- **Salida:** JSON estructurado o texto generado
- **Modelo:** `gemini-1.5-flash`
- **Uso Principal:**
  - Extracción de datos: `{amount: float, concept: string}`
  - Clasificación: `{category: string, confidence: float}`
  - Análisis multimodal de recibos
  - Respuestas conversacionales (con RAG)

---

#### 2.3. FinanceCore (El Motor Contable)
**Ubicación:** `/src/modules/finance_core/`

**Responsabilidades:**
- Gestión del ciclo de vida de transacciones (State Machine)
- Lógica de reconciliación y validación
- Cálculos financieros deterministas (agregaciones, reportes)
- Aplicación de reglas de negocio contables

**Restricciones:**
- ❌ **PROHIBIDO:** Llamar directamente a servicios de IA
- ✅ **OBLIGATORIO:** Delegar procesamiento de IA al módulo `AIBrain` vía `Gateway`
- ✅ **OBLIGATORIO:** Garantizar invariantes de estado (ej. solo `PROVISIONAL` → `VERIFIED`)

**Interfaz Pública (`service.py`):**
```python
def create_provisional_transaction(user_id: int, amount: float, concept: str) -> Transaction
def verify_transaction_with_document(transaction_id: int, document_data: DocumentData) -> Transaction
def verify_transaction_manually(transaction_id: int) -> Transaction
def calculate_user_spending(user_id: int, filters: dict) -> float
def get_spending_breakdown(user_id: int, group_by: str) -> dict
```

---

### Capítulo 3: La Regla de Oro de la Comunicación (Reforzada)

> **REGLA INMUTABLE (Protocolo Nexus):**  
> Un módulo **NUNCA** debe importar código interno (modelos, repositorios, utilidades) de otro módulo.  
> La comunicación entre módulos **SOLO** ocurre a través de la **Interfaz Pública del Servicio** (`service.py`).

**Ejemplo de Flujo Correcto (Voz → Transacción):**

```python
# modules/gateway/service.py
from modules.ai_brain.service import transcribe_audio, extract_transaction_data  # ✅
from modules.finance_core.service import create_provisional_transaction  # ✅

def orchestrate_voice_transaction(user_id: int, audio_file: bytes) -> Transaction:
    # Paso 1: Transcripción (delega a AIBrain)
    text = transcribe_audio(audio_file, language="es-MX")
    
    # Paso 2: Extracción (delega a AIBrain)
    data = extract_transaction_data(text)
    
    # Paso 3: Persistencia (delega a FinanceCore)
    transaction = create_provisional_transaction(
        user_id=user_id,
        amount=data.amount,
        concept=data.concept
    )
    
    return transaction
```

**Ejemplo PROHIBIDO:**
```python
# modules/gateway/service.py
from modules.finance_core.models import Transaction  # ❌ PROHIBIDO
from modules.finance_core.repository import TransactionRepository  # ❌ PROHIBIDO

def orchestrate_voice_transaction(user_id: int, audio_file: bytes):
    repo = TransactionRepository()  # ❌ Violación de fronteras
    transaction = repo.create(...)  # ❌ Acceso directo a internos
```

**Motivo:** Esta disciplina garantiza que separar los módulos a microservicios sea trivial (cambiar import local → HTTP call).

---

## PARTE II: Requerimientos Funcionales (User Stories & Flows)

### Capítulo 4: El Ciclo de Vida de la Transacción (State Machine)

#### 4.1. Estado 1: Ingesta Provisional (El Contrato de Voz)

**User Story:**  
*"Como usuario, quiero decir 'Gasté 500 pesos en el super' y que el sistema cree una transacción provisional sin fricción."*

**Entrada:**
- Archivo de audio (bytes)
- `user_id` (derivado de JWT)

**Lógica de Procesamiento (Secuencia Obligatoria):**

1. **Transcripción (AIBrain → Google Chirp):**
   - **Input:** Audio bytes
   - **Output:** Texto literal (ej. "Gasté quinientos pesos en el súper")
   - **Latencia Esperada:** < 3 segundos

2. **Extracción (AIBrain → Google Gemini):**
   - **Input:** Texto transcrito
   - **Prompt Template:**
     ```
     Extrae los datos de esta transacción financiera:
     "{texto}"
     
     Devuelve JSON: {"amount": float, "concept": string}
     ```
   - **Output:** `{amount: 500.0, concept: "Compra en el super"}`
   - **Latencia Esperada:** < 2 segundos

3. **Persistencia (FinanceCore):**
   - Creación de registro en BD con estado `PROVISIONAL`

**Post-condición (Contrato de Salida):**
- Entidad `Transaction` creada con:
  - `id` (UUID)
  - `user_id` (int)
  - `amount` (float) - **OBLIGATORIO**
  - `concept` (string) - **OBLIGATORIO**
  - `status` = `"PROVISIONAL"`
  - `created_at` (timestamp)
  - `merchant` = `NULL`
  - `transaction_date` = `NULL`
  - `category` = `NULL`

**Invariantes:**
- `amount > 0`
- `concept` no vacío
- `user_id` válido (existe en tabla `users`)

---

#### 4.2. Estado 2: Verificación Documental (El Contrato de Evidencia)

**User Story:**  
*"Como usuario, quiero subir una foto del recibo para que el sistema valide y complete los datos de mi transacción."*

**Entrada:**
- Imagen/PDF del recibo (bytes)
- `transaction_id` (UUID)
- `user_id` (derivado de JWT)

**Lógica de Procesamiento:**

1. **Validación de Estado (FinanceCore):**
   - **Invariante:** Solo una transacción con estado `PROVISIONAL` puede ser verificada
   - **Validación de Propiedad:** `transaction.user_id == user_id` (seguridad)

2. **Análisis Multimodal (AIBrain → Google Gemini Vision):**
   - **Input:** Imagen del recibo
   - **Prompt Template:**
     ```
     Analiza este recibo y extrae:
     - vendor (nombre del comercio)
     - date (fecha de la transacción, formato ISO)
     - total_amount (monto total)
     
     Devuelve JSON: {"vendor": string, "date": string, "total_amount": float}
     ```
   - **Output:** `{vendor: "Walmart", date: "2025-12-21", total_amount: 485.50}`
   - **Latencia Esperada:** < 4 segundos

3. **Reconciliación (FinanceCore):**
   - **Regla de Fuente de Verdad:** El `amount` del documento **sobrescribe** al provisional
   - El `concept` de voz se **preserva** (representa la intención del usuario)
   - Se actualizan: `merchant`, `transaction_date`

**Post-condición (Contrato de Salida):**
- Estado cambia a `"VERIFIED"`
- Campos actualizados:
  - `merchant` = "Walmart"
  - `transaction_date` = "2025-12-21"
  - `amount` = 485.50 (sobrescrito)
  - `verified_at` = timestamp actual
- **Disparo Automático:** Proceso de Auto-Categorización

---

#### 4.3. Estado 3: Verificación Manual (El Contrato de Confianza)

**User Story:**  
*"Como usuario, quiero confirmar una transacción sin subir recibo porque confío en mi registro de voz."*

**Entrada:**
- `transaction_id` (UUID)
- `user_id` (derivado de JWT)
- Confirmación explícita (boolean)

**Lógica de Procesamiento:**

1. **Validación de Estado (FinanceCore):**
   - **Invariante:** Solo una transacción `PROVISIONAL` puede ser verificada manualmente
   - **Validación de Propiedad:** `transaction.user_id == user_id`

**Post-condición (Contrato de Salida):**
- Estado cambia a `"VERIFIED_MANUAL"`
- `verified_at` = timestamp actual
- **Disparo Automático:** Auto-Categorización (basado solo en `concept`)

---

#### 4.4. Lógica de Auto-Categorización

**Disparador:** Al alcanzar estado `VERIFIED` o `VERIFIED_MANUAL`

**Lógica (AIBrain → Google Gemini):**
- **Input:** `concept` + `merchant` (si existe)
- **Prompt Template:**
  ```
  Clasifica esta transacción en una categoría:
  Concepto: "{concept}"
  Comercio: "{merchant}"
  
  Categorías válidas: ["Alimentación", "Transporte", "Servicios", "Ocio", "Salud", "Educación", "Otros"]
  
  Devuelve JSON: {"category": string, "confidence": float}
  ```
- **Output:** `{category: "Alimentación", confidence: 0.95}`

**Invariante:** Toda transacción verificada DEBE tener una categoría asignada.

**Regla de Confianza:**
- Si `confidence < 0.7` → Categoría = "Otros" (requiere revisión manual)
- Si `confidence >= 0.7` → Categoría asignada automáticamente

---

## PARTE III: Contrato de Experiencia e Interacción (UX Logic)

### Capítulo 5: El Asistente Conversacional (RAG Determinista)

#### 5.1. Interpretación de Intención (NLU)

**Objetivo:** Clasificar la entrada del usuario en dos tipos de consulta.

**Tipos de Consulta:**

1. **Consulta Determinista (SQL-backed):**
   - Preguntas sobre hechos numéricos o históricos
   - Ejemplos: "¿Cuánto gasté este mes?", "¿Qué compré en Starbucks?", "¿Cuál fue mi gasto más alto?"
   - **Procesamiento:** SQL agregación + LLM humanización

2. **Consulta Generativa (LLM-backed):**
   - Solicitudes de consejo, explicación o análisis
   - Ejemplos: "¿Cómo puedo ahorrar más?", "¿Por qué gasté tanto en ocio?", "Dame consejos financieros"
   - **Procesamiento:** RAG (contexto de transacciones) + LLM generación

**Clasificación (AIBrain → Google Gemini):**
```python
def classify_query_intent(query: str) -> QueryType:
    prompt = f"""
    Clasifica esta consulta:
    "{query}"
    
    Tipos:
    - "deterministic": Pregunta sobre datos específicos (montos, fechas, transacciones)
    - "generative": Solicitud de consejo o análisis
    
    Devuelve JSON: {{"type": string, "confidence": float}}
    """
    # Llamada a Gemini...
```

---

#### 5.2. Contrato de Respuesta Determinista (Regla de Alucinación Cero)

> **REGLA INMUTABLE:**  
> Para consultas sobre montos, fechas o datos específicos, el sistema **JAMÁS** debe confiar en el cálculo mental del LLM.

**Flujo de Ejecución:**

1. **Cálculo Determinista (FinanceCore):**
   - El backend ejecuta agregación SQL (SUM, COUNT, AVG, MAX, MIN)
   - Ejemplo: `SELECT SUM(amount) FROM transactions WHERE user_id = X AND created_at >= '2025-12-01'`
   - **Output:** `{total: 15420.50, count: 23}`

2. **Inyección de Contexto:**
   - El resultado numérico se inyecta en el prompt del sistema
   - **Prompt Template:**
     ```
     El usuario preguntó: "{query}"
     
     Datos calculados (FUENTE DE VERDAD):
     - Total gastado: $15,420.50
     - Número de transacciones: 23
     
     Humaniza esta respuesta de forma conversacional. NO calcules nada, solo presenta los datos.
     ```

3. **Humanización (AIBrain → Google Gemini):**
   - El LLM solo "viste" el dato calculado, no lo inventa
   - **Output:** "Este mes has gastado $15,420.50 en 23 transacciones. ¡Vas bien!"

**Invariante:** El LLM **NUNCA** tiene acceso directo a la BD. Solo recibe datos pre-calculados.

---

#### 5.3. Contrato de Respuesta Generativa (RAG)

**Flujo de Ejecución:**

1. **Recuperación de Contexto (FinanceCore):**
   - Obtener transacciones relevantes del usuario
   - Calcular métricas agregadas (gasto por categoría, tendencias)

2. **Construcción de Prompt (AIBrain):**
   ```
   Contexto del usuario:
   - Gasto total este mes: $15,420.50
   - Categoría con más gasto: Alimentación ($6,200)
   - Tendencia: +15% vs mes anterior
   
   Pregunta del usuario: "{query}"
   
   Proporciona consejo financiero personalizado basado en estos datos.
   ```

3. **Generación (AIBrain → Google Gemini):**
   - Respuesta contextualizada y personalizada

---

## PARTE IV: Requerimientos No Funcionales (NFRs)

### Capítulo 6: Latencia y Rendimiento

#### 6.1. Expectativas de Latencia

**Flujo de Voz → Transacción (End-to-End):**
- **Objetivo:** < 8 segundos (P95)
- **Desglose:**
  - Transcripción (Chirp): < 3s
  - Extracción (Gemini): < 2s
  - Persistencia (DB): < 500ms
  - Overhead de red: < 1s

**Flujo de Documento → Verificación:**
- **Objetivo:** < 10 segundos (P95)
- **Desglose:**
  - Análisis multimodal (Gemini Vision): < 4s
  - Reconciliación (DB): < 1s

**Consultas Conversacionales:**
- **Deterministas:** < 2 segundos
- **Generativas:** < 5 segundos

#### 6.2. Estrategias de Optimización

- **Caché de Transcripciones:** Almacenar texto transcrito para evitar re-procesamiento
- **Batch Processing:** Agrupar múltiples llamadas a Gemini cuando sea posible
- **Streaming:** Usar streaming de Gemini para respuestas conversacionales largas

---

### Capítulo 7: Costos y Cuotas (Google Cloud)

#### 7.1. Monitoreo de Cuotas

**Servicios a Monitorear:**
- **Speech-to-Text v2 (Chirp):**
  - Cuota gratuita: 60 minutos/mes
  - Costo adicional: ~$0.024 USD/minuto
  - **Límite de Alerta:** 50 minutos/mes

- **Gemini 1.5 Flash:**
  - Cuota gratuita: 15 RPM (requests per minute)
  - Costo por token (input): ~$0.00001875 USD/1K tokens
  - **Límite de Alerta:** 10,000 requests/día

#### 7.2. Estrategias de Reducción de Costos

- **Prompts Optimizados:** Minimizar tokens en prompts de sistema
- **Caché de Resultados:** Evitar re-procesar datos idénticos
- **Rate Limiting:** Limitar requests por usuario (ej. 10 transacciones/día en MVP)

---

### Capítulo 8: Seguridad y Credenciales

#### 8.1. Manejo de `GOOGLE_APPLICATION_CREDENTIALS`

**Regla de Configuración:**
- **Desarrollo Local:** Variable de entorno apuntando a Service Account JSON
  ```bash
  export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
  ```
- **Producción (GCP):** Usar Workload Identity (sin archivos de credenciales)

**Restricciones del Service Account:**
- **Permisos Mínimos:**
  - `roles/speech.client` (Speech-to-Text)
  - `roles/aiplatform.user` (Gemini API)
- ❌ **PROHIBIDO:** Permisos de administrador o acceso a otros servicios

#### 8.2. Aislamiento de Inquilinos (Multi-tenancy)

**Invariante Crítica:**  
Cada consulta a la base de datos (lectura o escritura) DEBE estar filtrada por `user_id`, derivado estrictamente del token JWT autenticado.

**Implementación Obligatoria:**
```python
# modules/finance_core/repository.py
def get_transactions(user_id: int, filters: dict) -> List[Transaction]:
    # ✅ OBLIGATORIO: Filtro por user_id
    query = db.query(Transaction).filter(Transaction.user_id == user_id)
    # ... aplicar otros filtros
    return query.all()
```

**Ejemplo PROHIBIDO:**
```python
# ❌ PROHIBIDO: Consulta sin filtro de user_id
def get_all_transactions() -> List[Transaction]:
    return db.query(Transaction).all()  # ❌ Violación de seguridad
```

---

#### 8.3. Principio de Mínimo Privilegio en IA

**Regla:** El módulo `AIBrain` es ciego al contexto del usuario.

**Restricciones:**
- ❌ **PROHIBIDO:** Acceder a la base de datos
- ❌ **PROHIBIDO:** Retener memoria entre requests
- ✅ **OBLIGATORIO:** Solo procesar la ventana de contexto inmediata

**Motivo:** Limitar la superficie de ataque. Si el módulo de IA es comprometido, no puede acceder a datos históricos del usuario.

---

#### 8.4. Soberanía de Datos (Google Cloud)

**Regla Inmutable:**  
Ningún dato financiero, clip de audio o imagen de recibo puede salir de la infraestructura controlada (GCP Project).

**Implementación:**
- **Región de Datos:** `us-central1` (o región específica del usuario)
- **Encriptación en Tránsito:** TLS 1.3 para todas las llamadas a Google APIs
- **Encriptación en Reposo:** Google-managed encryption keys (o CMEK para mayor control)

**Prohibiciones:**
- ❌ **PROHIBIDO:** Enviar datos a servicios de terceros (analytics, logging externo)
- ❌ **PROHIBIDO:** Almacenar datos en servicios fuera de GCP

---

## PARTE V: Gobernanza y Evolución

### Capítulo 9: Migración a Microservicios (Futuro)

**Path to Production:**

Cuando el MVP local demuestre tracción, la migración a microservicios será **mecánica**, no arquitectónica:

**Paso 1:** Cada módulo en `/src/modules/{dominio}` se convierte en un servicio independiente.

**Paso 2:** Reemplazar importaciones locales por llamadas HTTP:
```python
# ANTES (Monolito)
from modules.ai_brain.service import transcribe_audio
text = transcribe_audio(audio_bytes)

# DESPUÉS (Microservicio)
import httpx
response = httpx.post("http://ai-brain-service/api/transcribe", files={"audio": audio_bytes})
text = response.json()["text"]
```

**Paso 3:** Cada microservicio despliega en Cloud Run con auto-scaling.

**Invariante:** Si seguiste la Regla de Oro de la Comunicación, esta migración NO requiere cambios en la lógica de negocio.

---

### Capítulo 10: Principios Finales y Mantras

**Mantra Principal:**  
*La Lógica dirige, la Implementación obedece.*

**Mantra del Protocolo Nexus:**  
*Módulos soberanos hoy, Microservicios mañana. Las fronteras son sagradas.*

**Principios Cardinales:**
1. **Soberanía de Módulos:** Cada módulo es una caja negra con interfaz pública (`service.py`)
2. **Google-Only:** Cero dependencias de proveedores externos no-Google
3. **Realidad Local:** Desarrollo contra APIs reales, no mocks (excepto tests unitarios)
4. **Alucinación Cero:** Datos numéricos siempre calculados por SQL, nunca por LLM
5. **Seguridad Multi-tenant:** Filtro `user_id` en TODAS las consultas DB
6. **Migración Trivial:** La arquitectura de hoy es la de producción, solo cambia el transporte

---

**Versión:** 2.0 (Protocolo Nexus - Modular Monolith Edition)  
**Última Actualización:** 2025-12-21  
**Estado:** Activo y Vinculante  
**Documento Vinculado:** `GOVERNANCE.md` (Protocolo Nexus v3.0)