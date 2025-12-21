# Numa AI - Protocolo Nexus Edition

**Personal Finance Assistant with Zero Friction**

Numa es un asistente financiero conversacional que organiza tus finanzas sin fricción, garantizando privacidad absoluta mediante tecnología Google-Only.

## 🏗️ Arquitectura: Protocolo Nexus (Monolito Modular)

Este proyecto sigue el **Protocolo Nexus**, una arquitectura de monolito modular diseñada para migrar trivialmente a microservicios en producción.

### Estructura del Proyecto

```
Numa/
├── src/                          # ← TODO EL CÓDIGO VIVE AQUÍ
│   ├── modules/                  # Módulos Nexus (Cajas Negras Lógicas)
│   │   ├── api_gateway/          # Orquestador HTTP
│   │   ├── ai_brain/             # Cerebro de IA (Google Gemini/Chirp)
│   │   └── finance_core/         # Motor contable
│   ├── core/                     # Infraestructura compartida
│   │   ├── database.py           # Conexión a BD
│   │   ├── auth.py               # Autenticación JWT
│   │   └── config.py             # Configuración
│   └── main.py                   # ← PUNTO DE ENTRADA
├── services/numa-api/Context/    # Documentación de lógica
│   ├── LOGIC.md                  # ← LA CONSTITUCIÓN
│   └── GOVERNANCE.md             # ← EL PROTOCOLO NEXUS
├── requirements.txt              # Dependencias Python
├── .env.example                  # Template de variables de entorno
├── ONBOARDING.md                 # Guía de incorporación
└── ROADMAP.md                    # Plan de desarrollo
```

## 🚀 Inicio Rápido (Local-First)

### Paso 1: Clonar el Repositorio
```bash
git clone https://github.com/AmericoGarciaG/Numa.git
cd Numa
```

### Paso 2: Instalar Dependencias
```bash
pip install -r requirements.txt
```

### Paso 3: Configurar Variables de Entorno
```bash
# Copiar el template
cp .env.example .env

# Editar .env con tus valores
# Mínimo requerido:
# - DATABASE_URL (default: sqlite:///./numa.db)
# - SECRET_KEY (genera una clave aleatoria)
```

### Paso 4: Configurar Google Cloud (Opcional para MVP)
```bash
# Instalar Google Cloud SDK
# https://cloud.google.com/sdk/docs/install

# Autenticarte
gcloud auth application-default login

# Configurar proyecto
gcloud config set project numa-mvp-local
```

### Paso 5: Ejecutar el Servidor
```bash
python src/main.py
```

El servidor estará disponible en `http://localhost:8000`

### Paso 6: Explorar la API
Abre tu navegador en `http://localhost:8000/docs` para ver la documentación interactiva (Swagger UI).

## 📋 Regla de Oro del Protocolo Nexus

> **REGLA INMUTABLE:**  
> Un módulo **NUNCA** debe importar código interno (modelos, repositorios) de otro módulo.  
> La comunicación entre módulos **SOLO** ocurre a través de la **Interfaz Pública** (`service.py`).

**Ejemplo Correcto:**
```python
# modules/api_gateway/service.py
from src.modules.ai_brain.service import transcribe_audio  # ✅ CORRECTO

text = transcribe_audio(audio_bytes)
```

**Ejemplo PROHIBIDO:**
```python
# modules/api_gateway/service.py
from src.modules.ai_brain.gemini_client import GeminiClient  # ❌ PROHIBIDO

client = GeminiClient()
```

## 🔵 Stack Tecnológico (Google-Only)

- **Framework:** FastAPI + Uvicorn
- **Base de Datos:** SQLite (local) / Cloud SQL (producción)
- **Autenticación:** JWT (python-jose)
- **IA - Transcripción:** Google Cloud Speech-to-Text v2 (Chirp/USM)
- **IA - Inferencia:** Google Gemini 1.5 Flash
- **IA - Documentos:** Google Cloud Document AI (futuro)

## 📚 Documentación

- **[GOVERNANCE.md](services/numa-api/Context/GOVERNANCE.md)** - Protocolo Nexus y reglas de desarrollo
- **[LOGIC.md](services/numa-api/Context/LOGIC.md)** - Lógica de negocio y contratos
- **[ONBOARDING.md](ONBOARDING.md)** - Guía para nuevos colaboradores
- **[ROADMAP.md](ROADMAP.md)** - Plan de desarrollo por fases

## 🧪 Testing

```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=src
```

## 🚢 Migración a Microservicios (Fase 3)

Cuando el MVP local funcione, la migración a Cloud Run será **mecánica**:

```python
# ANTES (Monolito)
from src.modules.ai_brain.service import transcribe_audio
text = transcribe_audio(audio_bytes)

# DESPUÉS (Microservicio)
import httpx
response = httpx.post("https://ai-brain-service.run.app/transcribe", 
                     files={"audio": audio_bytes})
text = response.json()["text"]
```

**Cero cambios en la lógica de negocio. Solo cambia el transporte.**

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE) para más detalles.

## 🤝 Contribuir

Lee [ONBOARDING.md](ONBOARDING.md) para entender la metodología Kybern + Protocolo Nexus.

---

**Mantra del Protocolo Nexus:**  
*"Módulos soberanos hoy, Microservicios mañana. Las fronteras son sagradas."*