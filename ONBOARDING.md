
---

### **Nombre del Archivo:** `ONBOARDING.md`
**Ubicación sugerida:** Raíz del proyecto.

---

# 🚀 Numa: Manifiesto de Abordaje (Protocolo Nexus)
### Guía Conceptual y Arquitectónica para Colaboradores Humanos

**Bienvenido al Proyecto Numa.**

Si estás leyendo esto, te has unido al equipo para construir el futuro de las finanzas personales. Este documento no contiene código. Su propósito es darte la visión completa del "Qué", el "Por qué" y el "Dónde", para que puedas navegar el proyecto con autonomía desde el primer día.

---

## 1. La Visión: ¿Qué es Numa?

El mercado está saturado de apps de finanzas que te obligan a ser contador: capturar gastos manualmente, categorizar línea por línea, conectar cuentas bancarias (riesgo de seguridad). **Eso es fricción.**

**Numa es el Antídoto.**
Es un asistente financiero de **"Cero-Fricción"**.
*   **La Promesa:** El usuario no trabaja para la app; la app trabaja para el usuario.
*   **La Interacción:** El usuario simplemente "arroja" su realidad financiera al sistema: un audio ("gasté 50 en café"), una foto de un recibo arrugado, o un PDF.
*   **La Magia:** Numa procesa ese caos, extrae la verdad contable y la organiza.
*   **La Privacidad:** Somos **Soberanos**. Los datos financieros y la voz del usuario permanecen dentro de nuestra infraestructura controlada (Google Cloud Project).

---

## 2. Nuestra Metodología: Kybern + Protocolo Nexus

En este proyecto, no programamos "a mano" al estilo tradicional. Usamos un marco de trabajo llamado **Kybern** con el **Protocolo Nexus**.

### Las Reglas del Juego:
1.  **Tú eres el Director, la IA es el Constructor:** Tu trabajo no es picar código, es definir **Lógica**. Usamos un agente de IA (llamado *Antigravity*) para escribir la implementación técnica.
2.  **El `LOGIC.md` es la Constitución:** Todo lo que el sistema hace debe estar escrito primero en el archivo `services/numa-api/Context/LOGIC.md`. Si no está en el libro, no existe.
3.  **Cajas Negras Lógicas (Módulos Nexus):** Organizamos el código en módulos que se comportan como microservicios internos, pero viven en un solo repositorio. Esto facilita el desarrollo local y la migración futura a la nube.

**Tu flujo de trabajo será:**
*   Pensar la solución → Escribirla en el Logic Book → Instruir al Agente → Validar el resultado.

---

## 3. La Arquitectura: Monolito Modular (Protocolo Nexus)

Para lograr privacidad, potencia y facilidad de desarrollo, usamos una arquitectura de **Monolito Modular** que puede evolucionar a microservicios sin refactorización.

Imagínalo como una oficina con tres departamentos en el mismo edificio (por ahora):

### 🏢 1. Gateway (El Orquestador)
*   **Qué es:** El cerebro del negocio.
*   **Su trabajo:** Habla con el usuario (App/Web), guarda los datos en la base de datos, gestiona la seguridad (JWT) y orquesta los flujos de negocio.
*   **Lo que NO hace:** No "piensa" ni transcribe audios. Delega eso a los expertos.
*   **Ubicación:** `/src/modules/gateway/`
*   **Tecnología:** Python (FastAPI).

### 🧠 2. AIBrain (El Cerebro de Inferencia)
*   **Qué es:** El módulo de Inteligencia Artificial.
*   **Su trabajo:** 
    *   Transcribir audio a texto usando **Google Chirp** (Speech-to-Text v2)
    *   Extraer datos estructurados usando **Google Gemini 1.5 Flash**
    *   Clasificar transacciones y responder consultas
*   **Por qué existe:** Abstrae la complejidad de los servicios de Google AI. Si mañana cambiamos de modelo, el resto del sistema ni se entera.
*   **Ubicación:** `/src/modules/ai_brain/`
*   **Restricción Crítica:** **Stateless**. No guarda datos de usuario, solo procesa lo que recibe.

### 💰 3. FinanceCore (El Motor Contable)
*   **Qué es:** El corazón de la lógica de negocio financiera.
*   **Su trabajo:** 
    *   Gestionar el ciclo de vida de transacciones (PROVISIONAL → VERIFIED)
    *   Aplicar reglas de reconciliación
    *   Calcular agregaciones financieras (gastos totales, reportes)
*   **Ubicación:** `/src/modules/finance_core/`
*   **Seguridad:** Todas las consultas a BD están filtradas por `user_id` (JWT).

---

## 4. El Protocolo Nexus: La Regla de Oro

> **REGLA INMUTABLE:**  
> Un módulo **NUNCA** debe importar código interno (modelos, repositorios) de otro módulo.  
> La comunicación entre módulos **SOLO** ocurre a través de la **Interfaz Pública** (`service.py`).

**¿Por qué esta disciplina?**

Cuando llegue el momento de migrar a microservicios en la nube, solo necesitaremos cambiar las importaciones locales por llamadas HTTP. **Cero refactorización arquitectónica.**

**Ejemplo:**
```python
# HOY (Monolito Local)
from modules.ai_brain.service import transcribe_audio
text = transcribe_audio(audio_bytes)

# MAÑANA (Microservicio en Cloud Run)
import httpx
response = httpx.post("https://ai-brain-service.run.app/transcribe", files={"audio": audio_bytes})
text = response.json()["text"]
```

**La arquitectura de hoy es la de producción. Solo cambia el transporte.**

---

## 5. El Stack Tecnológico: Google-Only

Para el MVP local, usamos **exclusivamente** servicios de Google:

### Servicios de IA:
*   **Google Chirp (Speech-to-Text v2):** Transcripción de audio
*   **Google Gemini 1.5 Flash:** Extracción de datos, clasificación, análisis multimodal

### Infraestructura (Futuro):
*   **Cloud Run:** Contenedores serverless
*   **Cloud SQL:** Base de datos PostgreSQL gestionada
*   **VPC:** Red privada virtual

### ¿Por qué Google-Only?
*   **Soberanía de Datos:** Todo permanece en nuestro GCP Project
*   **Integración Nativa:** Los servicios de Google se hablan entre sí sin fricciones
*   **Escalabilidad:** Cuando migremos a la nube, ya estaremos usando la misma infraestructura

---

## 6. El Flujo de Vida de un Dato (Ejemplo)

Para que entiendas cómo se conectan las piezas, sigue el viaje de un audio:

1.  **Usuario:** Graba "Compré gasolina, 500 pesos".
2.  **Gateway:** Recibe el archivo. Llama a `AIBrain.transcribe_audio()`.
3.  **AIBrain:** Envía el audio a **Google Chirp** (Speech-to-Text v2).
4.  **Google Chirp:** Procesa el audio y devuelve texto: "Compré gasolina, 500 pesos".
5.  **AIBrain:** Recibe el texto. Llama a **Google Gemini** con un prompt estructurado: "Extrae monto y concepto en JSON".
6.  **Google Gemini:** Devuelve `{"amount": 500.0, "concept": "Gasolina"}`.
7.  **Gateway:** Recibe el JSON. Llama a `FinanceCore.create_provisional_transaction()`.
8.  **FinanceCore:** Guarda en la Base de Datos como transacción "PROVISIONAL".
9.  **Usuario:** Ve en su pantalla la transacción lista para confirmar.

---

## 7. ¿Dónde vive todo? (Estructura del Proyecto)

```
Numa/
├── src/                          # ← TODO EL CÓDIGO VIVE AQUÍ
│   ├── modules/                  # ← Módulos Nexus (Cajas Negras Lógicas)
│   │   ├── gateway/              # Orquestador de negocio
│   │   │   ├── service.py        # ← INTERFAZ PÚBLICA
│   │   │   ├── routes.py         # Endpoints FastAPI
│   │   │   └── ...
│   │   ├── ai_brain/             # Cerebro de IA
│   │   │   ├── service.py        # ← INTERFAZ PÚBLICA
│   │   │   ├── gemini_client.py  # Cliente de Google Gemini
│   │   │   ├── chirp_client.py   # Cliente de Google Chirp
│   │   │   └── ...
│   │   └── finance_core/         # Motor contable
│   │       ├── service.py        # ← INTERFAZ PÚBLICA
│   │       ├── models.py         # Modelos SQLAlchemy
│   │       ├── repository.py     # Acceso a datos
│   │       └── ...
│   ├── core/                     # Infraestructura compartida
│   │   ├── database.py           # Conexión a BD
│   │   ├── auth.py               # Autenticación JWT
│   │   └── config.py             # Configuración global
│   └── main.py                   # ← PUNTO DE ENTRADA (FastAPI app)
├── services/numa-api/Context/    # Documentación de lógica
│   ├── LOGIC.md                  # ← LA CONSTITUCIÓN
│   └── GOVERNANCE.md             # ← EL PROTOCOLO NEXUS
├── requirements.txt              # Dependencias Python
└── README.md
```

**Nota:** Por ahora, ignora las carpetas `services/mcp-server` y `services/model-server`. Son legacy de la arquitectura anterior. El nuevo código vive en `/src`.

---

## 8. ¿Por dónde empiezo? (Día 1)

### Paso 1: Clonar el Repositorio
```bash
git clone https://github.com/tu-org/numa.git
cd numa
```

### Paso 2: Instalar Dependencias
```bash
pip install -r requirements.txt
```

### Paso 3: Configurar Google Cloud
Necesitas autenticarte con Google Cloud para que el código local pueda llamar a Gemini y Chirp:

```bash
# Instalar Google Cloud SDK (si no lo tienes)
# https://cloud.google.com/sdk/docs/install

# Autenticarte
gcloud auth application-default login

# Configurar el proyecto (reemplaza con tu GCP Project ID)
gcloud config set project numa-mvp-local
```

Esto creará credenciales en tu máquina que el SDK de Google usará automáticamente.

### Paso 4: Configurar Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto:

```bash
# Base de Datos (SQLite para desarrollo local)
DATABASE_URL=sqlite:///./numa_local.db

# Google Cloud
GCP_PROJECT_ID=numa-mvp-local
GCP_REGION=us-central1

# JWT (genera una clave secreta aleatoria)
JWT_SECRET_KEY=tu-clave-secreta-super-segura-aqui
```

### Paso 5: Inicializar la Base de Datos
```bash
# Crear las tablas
python -m src.core.database init
```

### Paso 6: Ejecutar el Servidor
```bash
python src/main.py
```

Deberías ver:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Paso 7: Probar la API
Abre tu navegador en `http://127.0.0.1:8000/docs` para ver la documentación interactiva de la API (Swagger UI).

---

## 9. Entendiendo el Protocolo Nexus (Para Desarrolladores)

### ¿Por qué organizamos las carpetas así?

El **Protocolo Nexus** es una estrategia de arquitectura que nos permite:

1.  **Desarrollar Rápido Localmente:** Todo el código está en un solo repositorio. No necesitas Docker, Kubernetes o múltiples terminales.

2.  **Migrar Fácilmente a la Nube:** Cuando el MVP local funcione, cada módulo en `/src/modules/{dominio}` se convertirá en un microservicio independiente en Cloud Run.

3.  **Mantener Fronteras Claras:** Aunque todo está en un solo repo, los módulos se comportan como microservicios internos. Esto previene el "código espagueti".

### La Regla de Oro en la Práctica:

**✅ CORRECTO:**
```python
# modules/gateway/service.py
from modules.ai_brain.service import transcribe_audio  # ✅ Interfaz pública

def process_voice(audio_bytes):
    text = transcribe_audio(audio_bytes)  # ✅ Llamada limpia
    return text
```

**❌ PROHIBIDO:**
```python
# modules/gateway/service.py
from modules.ai_brain.gemini_client import GeminiClient  # ❌ Código interno

def process_voice(audio_bytes):
    client = GeminiClient()  # ❌ Violación de fronteras
    text = client.transcribe(audio_bytes)
    return text
```

**¿Por qué es importante?**

Cuando migremos a microservicios, el primer ejemplo solo requiere cambiar la importación por una llamada HTTP. El segundo ejemplo requeriría refactorizar toda la lógica.

---

## 10. Próximos Pasos

1.  **Lee la Lógica:** Ve a `services/numa-api/Context/LOGIC.md`. Ahí están las reglas del negocio.
2.  **Lee la Gobernanza:** Ve a `services/numa-api/Context/GOVERNANCE.md`. Ahí está el Protocolo Nexus completo.
3.  **Explora el Código:** Navega por `/src/modules/` para ver cómo están implementados los módulos.
4.  **Prueba el Sistema:** Usa la documentación interactiva en `/docs` para hacer llamadas a la API.
5.  **Consulta el Roadmap:** Ve a `ROADMAP.md` para ver qué estamos construyendo a continuación.

---

## 11. Filosofía de Desarrollo

### Local-First (MVP)
*   **Prioridad:** Hacer que el sistema funcione en `localhost` primero.
*   **Realidad, no Mocks:** El entorno local llama a las APIs reales de Google (Gemini, Chirp).
*   **Simplicidad:** Sin Docker, sin Kubernetes, sin complejidad innecesaria en el Día 1.

### Cloud-Ready (Producción)
*   **Migración Trivial:** Cuando el MVP funcione, la migración a Cloud Run será mecánica.
*   **Infraestructura como Código:** Usaremos Terraform para provisionar la nube.
*   **Escalabilidad:** Los microservicios en Cloud Run escalarán automáticamente.

---

Bienvenido a la ingeniería dirigida por lógica.  
Bienvenido al **Protocolo Nexus**.  
**Bienvenido a Numa.**

---