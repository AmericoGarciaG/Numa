# GOVERNANCE.md (Protocolo Nexus)

**Agent:** Antigravity
**Framework:** Kybern (DBBD + DirGen) + Protocolo Nexus
**Version:** 3.0 - Modular Monolith Edition
**Estrategia:** Monolito Modular para MVP Local → Microservicios en Producción

---

## **PARTE I: El Protocolo Nexus - Fundamentos**

### **1. Prime Directive: La Constitución del Código**
Tu propósito es actuar como el brazo ejecutor de la metodología Kybern bajo el **Protocolo Nexus**. No escribes código basado en "vibes" o suposiciones; traduces contratos lógicos inmutables en implementaciones modulares que pueden evolucionar de monolito a microservicios sin refactorización arquitectónica.

### **2. Source of Truth (Fuente de Verdad)**
Existe un único documento que gobierna el comportamiento del sistema.
*   **Archivo:** `services/numa-api/Context/LOGIC.md`
*   **Regla Inmutable:** Si el código contradice al LOGIC.md, el código es un bug, sin excepciones.

---

## **PARTE II: Arquitectura - Monolito Modular (Protocolo Nexus)**

### **3. Filosofía del Protocolo Nexus**
El **Protocolo Nexus** establece una arquitectura de **Monolito Modular** para el MVP local, diseñada para migrar trivialmente a microservicios en producción. La clave es la **disciplina de fronteras**: los módulos se comportan como microservicios internos.

#### **3.1. Estructura de Directorios Obligatoria**
Todo el código fuente del sistema DEBE vivir bajo `/src` con la siguiente estructura:

```
/src
├── modules/
│   ├── {dominio_1}/
│   │   ├── service.py          # ← INTERFAZ PÚBLICA (único punto de entrada)
│   │   ├── models.py           # ← Modelos internos (PRIVADO)
│   │   ├── schemas.py          # ← Schemas internos (PRIVADO)
│   │   ├── repository.py       # ← Acceso a datos (PRIVADO)
│   │   └── utils.py            # ← Utilidades internas (PRIVADO)
│   ├── {dominio_2}/
│   │   └── ...
│   └── {dominio_n}/
│       └── ...
├── core/
│   ├── database.py             # Conexión a BD compartida
│   ├── auth.py                 # Autenticación JWT
│   └── config.py               # Configuración global
└── main.py                     # Punto de entrada FastAPI
```

**Dominios Iniciales Obligatorios:**
- `transactions` - Gestión del ciclo de vida de transacciones
- `audio` - Procesamiento de audio y transcripción
- `documents` - Análisis de recibos/documentos
- `chat` - Asistente conversacional
- `categories` - Auto-categorización

#### **3.2. La Regla de Oro de la Comunicación (CRÍTICA)**

> **REGLA INMUTABLE:**  
> Un módulo **NUNCA** debe importar código interno (modelos, utilidades, repositorios) de otro módulo.  
> La comunicación entre módulos **SOLO** ocurre a través de la **Interfaz Pública del Servicio** (`service.py` en la raíz del módulo).

**Motivo:** Esta disciplina garantiza que separar los módulos a microservicios en el futuro sea trivial: cambiar una importación local (`from modules.transactions.service import create_transaction`) por una llamada HTTP (`POST /transactions`) requiere **cero cambios arquitectónicos**.

**Ejemplo Correcto:**
```python
# modules/chat/service.py
from modules.transactions.service import get_user_spending  # ✅ CORRECTO

def answer_query(user_id: int, query: str):
    total = get_user_spending(user_id)  # Llamada a interfaz pública
    return f"Has gastado ${total}"
```

**Ejemplo PROHIBIDO:**
```python
# modules/chat/service.py
from modules.transactions.models import Transaction  # ❌ PROHIBIDO
from modules.transactions.repository import TransactionRepo  # ❌ PROHIBIDO

def answer_query(user_id: int):
    repo = TransactionRepo()  # ❌ Violación de fronteras
    transactions = repo.get_all(user_id)
```

#### **3.3. Anatomía de un Módulo**

Cada módulo DEBE seguir esta estructura:

1. **`service.py` (Interfaz Pública):**
   - Única superficie de API del módulo
   - Funciones puras que representan casos de uso
   - No expone modelos internos (usa DTOs/Schemas públicos si es necesario)

2. **Archivos Internos (PRIVADOS):**
   - `models.py` - Modelos SQLAlchemy (solo para este módulo)
   - `schemas.py` - Pydantic schemas para validación interna
   - `repository.py` - Acceso a base de datos
   - `utils.py` - Funciones auxiliares del dominio

**Invariante:** Los archivos internos NUNCA deben ser importados desde fuera del módulo.

---

## **PARTE III: Stack Tecnológico (Google-Only)**

### **4. Tecnologías Obligatorias**

El **Protocolo Nexus** establece un stack tecnológico exclusivo de Google para el MVP local:

#### **4.1. Inferencia de Texto y Datos**
- **Modelo:** Google Gemini 1.5 Flash
- **SDK:** `google-generativeai` (Python)
- **Uso:** Extracción de datos estructurados, clasificación, NLU, generación de respuestas

#### **4.2. Audio y Transcripción**
- **Servicio:** Google Cloud Speech-to-Text v2
- **Modelo:** Chirp / Universal Speech Model (USM)
- **Uso:** Transcripción de audio a texto para ingesta de transacciones

#### **4.3. Análisis de Documentos (Futuro)**
- **Servicio:** Google Cloud Document AI (cuando se implemente)
- **Uso:** Extracción de datos de recibos/facturas

**Prohibiciones:**
- ❌ OpenAI (GPT-4, Whisper)
- ❌ Anthropic (Claude)
- ❌ Modelos locales (Ollama, Llama, etc.)
- ❌ Servicios de terceros no-Google

---

## **PARTE IV: Directivas de Desarrollo**

### **5. Reglas de Implementación**

#### **5.1. Directiva de "Realidad Local"**
> **PROHIBIDO:** Usar mocks, simulaciones o stubs para los flujos principales en el entorno de desarrollo local.

**Regla:** El entorno local DEBE llamar a las APIs reales de Google (Gemini, Speech-to-Text) usando credenciales de desarrollo. Esto garantiza:
- Detección temprana de problemas de integración
- Validación realista de latencias y costos
- Paridad entre desarrollo y producción

**Excepción:** Solo se permiten mocks para tests unitarios automatizados, nunca para desarrollo manual.

#### **5.2. Apego Estricto al LOGIC.md**
*   Antes de implementar cualquier función, consulta el capítulo correspondiente en `LOGIC.md`.
*   Ejemplo: Si vas a modificar el chat, verifica las reglas de "Alucinación Cero" en el Capítulo 3.

#### **5.3. Fungibilidad del Código**
*   El código de implementación (`.py`, `.tf`) es desechable. La lógica de negocio (`.md`) es el activo.
*   No te apegues al código existente si una refactorización limpia alinea mejor con el Logic Book o el Protocolo Nexus.

#### **5.4. Protocolo de Clarificación**
*   Si el `LOGIC.md` es ambiguo o el Protocolo Nexus entra en conflicto con una implementación existente, **DETENTE**.
*   No infieras. Solicita al Director Humano que actualice el Logic Book antes de continuar.

---

## **PARTE V: Flujo de Trabajo Operativo**

### **6. The Nexus Cycle (Ciclo de Desarrollo)**

1.  **Leer:** Analizar `LOGIC.md` para entender el contrato del estado actual.
2.  **Ubicar:** Determinar qué módulo (`/src/modules/{dominio}`) debe modificarse o crearse.
3.  **Diseñar:** Definir la interfaz pública (`service.py`) que expondrá el módulo.
4.  **Ejecutar:** Implementar la lógica interna cumpliendo los invariantes (ej. `WHERE user_id = X`).
5.  **Verificar:** Asegurar que:
    - La implementación cumple la Post-condición del Logic Book
    - No hay importaciones cruzadas de código interno entre módulos
    - Las llamadas a Google APIs funcionan en entorno local real

---

## **PARTE VI: Migración a Microservicios (Futuro)**

### **7. Path to Production: De Monolito a Microservicios**

El **Protocolo Nexus** garantiza que la migración sea mecánica, no arquitectónica:

**Paso 1:** Cada módulo en `/src/modules/{dominio}` se convierte en un servicio independiente.

**Paso 2:** Reemplazar importaciones locales por llamadas HTTP:
```python
# ANTES (Monolito)
from modules.transactions.service import create_transaction
result = create_transaction(data)

# DESPUÉS (Microservicio)
import httpx
response = httpx.post("http://transactions-service/api/transactions", json=data)
result = response.json()
```

**Paso 3:** Cada microservicio mantiene su propia base de datos (si es necesario) o comparte la BD existente con aislamiento por `user_id`.

**Invariante:** Si seguiste la Regla de Oro de la Comunicación, esta migración NO requiere cambios en la lógica de negocio, solo en el transporte (local → HTTP).

---

## **PARTE VII: Mantra y Principios Finales**

**Mantra Principal:**  
*La Lógica dirige, la Implementación obedece.*

**Mantra del Protocolo Nexus:**  
*Módulos soberanos hoy, Microservicios mañana. Las fronteras son sagradas.*

**Principios Cardinales:**
1. **Soberanía de Módulos:** Cada módulo es una caja negra con interfaz pública.
2. **Google-Only:** Cero dependencias de proveedores externos no-Google.
3. **Realidad Local:** Desarrollo contra APIs reales, no mocks.
4. **Migración Trivial:** La arquitectura de hoy es la de producción, solo cambia el transporte.

---

**Versión:** 3.0 (Protocolo Nexus - Modular Monolith Edition)  
**Última Actualización:** 2025-12-21  
**Estado:** Activo y Vinculante