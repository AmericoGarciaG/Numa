# Numa - Sistema de IA Soberana para Finanzas Personales

## Arquitectura de Microservicios

Numa ahora utiliza una arquitectura de 3 servicios para máxima flexibilidad y soberanía de datos:

### 📊 `numa-api` (Puerto 8000)
- **Propósito**: API principal de Numa con autenticación JWT
- **Tecnología**: FastAPI + SQLAlchemy
- **Responsabilidades**: Gestión de usuarios, transacciones, y lógica de negocio

### 🔗 `mcp-server` (Puerto 8001)
- **Propósito**: Enrutador inteligente para modelos de IA
- **Tecnología**: Model Context Protocol (MCP)
- **Responsabilidades**: Abstracción y enrutamiento de peticiones a modelos

### 🧠 `model-server` (Puerto 11434)
- **Propósito**: Servidor de modelos de IA open source
- **Tecnología**: Ollama
- **Modelos**: Llama 3 (lenguaje) + Whisper (transcripción)

## Inicio Rápido

1. **Clonar y configurar:**
   ```bash
   git clone [repo-url]
   cd Numa
   ```

2. **Seguir la guía de configuración:**
   ```bash
   # Lee el archivo TESTING_GUIDE.md para configuración completa
   cat TESTING_GUIDE.md
   ```

3. **Lanzar sistema completo:**
   ```bash
   docker-compose up --build
   ```

4. **Probar en navegador:**
   ```
   http://localhost:8000/docs
   ```

## Beneficios de esta Arquitectura

- 🔒 **Soberanía Total**: Todos los modelos ejecutan localmente
- ⚡ **Escalabilidad**: Cada servicio puede escalarse independientemente
- 🔄 **Flexibilidad**: Fácil intercambio de modelos y proveedores
- 🛡️ **Privacidad**: Zero datos salen del entorno local

## Estructura del Proyecto

```
Numa/
├── services/
│   ├── numa-api/          # FastAPI application
│   ├── mcp-server/        # Model Context Protocol server
│   └── model-server/      # Ollama + AI models
├── docker-compose.yml     # Orchestration
└── TESTING_GUIDE.md      # Complete setup guide
```

## Siguiente Paso

👉 **Lee `TESTING_GUIDE.md`** para configurar y probar todo el sistema end-to-end.