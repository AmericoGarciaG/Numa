
---

### **Nombre del Archivo:** `ROADMAP.md`
**Ubicación sugerida:** Raíz del proyecto.

---

# 🗺️ Numa: Plan Maestro de Construcción (Protocolo Nexus Roadmap)

**Estado del Proyecto:** 🏗️ Fase 1 - MVP Local Real (En Progreso)
**Metodología:** Kybern (DBBD) + Protocolo Nexus
**Estrategia:** Local-First → Cloud Migration

Este documento rastrea la evolución del sistema Numa desde su concepción lógica hasta su despliegue en producción. Se divide en Fases de Maduración bajo el **Protocolo Nexus**.

---

## 📅 Fase 1: MVP Local Real (Monolito Modular)
**Objetivo:** Construir un prototipo funcional en `localhost` usando servicios reales de Google, sin Docker ni complejidad de infraestructura.

**Filosofía:** Local-First. Hacer que el sistema funcione en tu máquina antes de pensar en la nube.

### 1.1. Fundamentos del Protocolo Nexus ✅
- [x] **GOVERNANCE.md v3.0:** Definir el Protocolo Nexus y la Regla de Oro de la Comunicación.
- [x] **LOGIC.md v2.0:** Reescribir contratos de negocio para arquitectura modular con Google-only stack.
- [x] **ONBOARDING.md (Actualizado):** Guía Local-First para colaboradores.
- [x] **ROADMAP.md (Este documento):** Plan de fases alineado con Protocolo Nexus.

### 1.2. Estructura de Directorios Obligatoria
- [ ] **Crear `/src` como raíz del código:**
  - [ ] `/src/modules/gateway/` - Orquestador de negocio
  - [ ] `/src/modules/ai_brain/` - Cerebro de inferencia (Google AI)
  - [ ] `/src/modules/finance_core/` - Motor contable
  - [ ] `/src/core/` - Infraestructura compartida (DB, Auth, Config)
  - [ ] `/src/main.py` - Punto de entrada FastAPI

### 1.3. Módulo: Core (Infraestructura Compartida)
- [ ] **`core/config.py`:** Gestión de variables de entorno (`.env`)
- [ ] **`core/database.py`:** Conexión a SQLite local (desarrollo) con SQLAlchemy
- [ ] **`core/auth.py`:** Autenticación JWT (generación y validación de tokens)
- [ ] **Script de inicialización:** `python -m src.core.database init` para crear tablas

### 1.4. Módulo: AIBrain (El Cerebro de Inferencia)
**Responsabilidad:** Abstraer servicios de Google AI.

- [ ] **`ai_brain/service.py` (Interfaz Pública):**
  - [ ] `transcribe_audio(audio_bytes: bytes, language: str) -> str`
  - [ ] `extract_transaction_data(text: str) -> TransactionData`
  - [ ] `analyze_document(image_bytes: bytes) -> DocumentData`
  - [ ] `classify_category(concept: str, merchant: str) -> str`
  - [ ] `answer_query(query: str, context: dict) -> str`

- [ ] **`ai_brain/chirp_client.py`:** Cliente de Google Speech-to-Text v2
  - [ ] Configurar credenciales (`GOOGLE_APPLICATION_CREDENTIALS`)
  - [ ] Implementar transcripción con modelo `chirp` o `latest_long`
  - [ ] Manejo de errores (audio inaudible, formato inválido)

- [ ] **`ai_brain/gemini_client.py`:** Cliente de Google Gemini 1.5 Flash
  - [ ] Configurar SDK `google-generativeai`
  - [ ] Implementar extracción de datos con prompts estructurados
  - [ ] Implementar análisis multimodal (imágenes de recibos)
  - [ ] Implementar clasificación de categorías
  - [ ] Implementar respuestas conversacionales (RAG)

- [ ] **`ai_brain/schemas.py`:** DTOs para datos estructurados
  - [ ] `TransactionData` (amount, concept)
  - [ ] `DocumentData` (vendor, date, total_amount)
  - [ ] `CategoryData` (category, confidence)

### 1.5. Módulo: FinanceCore (El Motor Contable)
**Responsabilidad:** Lógica de negocio financiera y persistencia.

- [ ] **`finance_core/models.py`:** Modelos SQLAlchemy
  - [ ] `User` (id, email, hashed_password, created_at)
  - [ ] `Transaction` (id, user_id, amount, concept, status, merchant, transaction_date, category, created_at, verified_at)
  - [ ] Estados: `PROVISIONAL`, `VERIFIED`, `VERIFIED_MANUAL`

- [ ] **`finance_core/repository.py`:** Acceso a datos (Data Access Layer)
  - [ ] `create_transaction(user_id, amount, concept) -> Transaction`
  - [ ] `get_transaction_by_id(transaction_id, user_id) -> Transaction`
  - [ ] `update_transaction(transaction_id, data) -> Transaction`
  - [ ] `get_user_transactions(user_id, filters) -> List[Transaction]`
  - [ ] **Invariante:** Todas las consultas filtradas por `user_id`

- [ ] **`finance_core/service.py` (Interfaz Pública):**
  - [ ] `create_provisional_transaction(user_id, amount, concept) -> Transaction`
  - [ ] `verify_transaction_with_document(transaction_id, document_data) -> Transaction`
  - [ ] `verify_transaction_manually(transaction_id) -> Transaction`
  - [ ] `calculate_user_spending(user_id, filters) -> float`
  - [ ] `get_spending_breakdown(user_id, group_by) -> dict`

- [ ] **`finance_core/state_machine.py`:** Lógica de transiciones de estado
  - [ ] Validar transiciones permitidas (PROVISIONAL → VERIFIED)
  - [ ] Disparar auto-categorización al verificar

### 1.6. Módulo: Gateway (El Orquestador)
**Responsabilidad:** Exposición de API y orquestación de flujos.

- [ ] **`gateway/routes.py`:** Endpoints FastAPI
  - [ ] `POST /api/auth/register` - Registro de usuario
  - [ ] `POST /api/auth/login` - Login (devuelve JWT)
  - [ ] `POST /api/transactions/voice` - Ingesta de audio
  - [ ] `POST /api/transactions/{id}/verify-document` - Verificación documental
  - [ ] `POST /api/transactions/{id}/verify-manual` - Verificación manual
  - [ ] `GET /api/transactions` - Listar transacciones del usuario
  - [ ] `POST /api/chat` - Consulta conversacional

- [ ] **`gateway/service.py` (Interfaz Pública):**
  - [ ] `orchestrate_voice_transaction(user_id, audio_file) -> Transaction`
  - [ ] `orchestrate_document_verification(user_id, transaction_id, document) -> Transaction`
  - [ ] `get_user_transactions(user_id, filters) -> List[Transaction]`
  - [ ] `handle_chat_query(user_id, query) -> str`

- [ ] **`gateway/dependencies.py`:** Dependencias FastAPI
  - [ ] `get_current_user(token: str) -> User` - Validación JWT

### 1.7. Integración y Pruebas Locales
- [ ] **Flujo End-to-End: Voz → Transacción**
  - [ ] Grabar audio de prueba ("Gasté 500 pesos en el super")
  - [ ] Llamar a `POST /api/transactions/voice` con el audio
  - [ ] Verificar que se crea transacción `PROVISIONAL` en BD
  - [ ] Validar que `amount=500.0` y `concept` contiene "super"

- [ ] **Flujo End-to-End: Documento → Verificación**
  - [ ] Subir imagen de recibo de prueba
  - [ ] Llamar a `POST /api/transactions/{id}/verify-document`
  - [ ] Verificar que estado cambia a `VERIFIED`
  - [ ] Validar que `merchant`, `transaction_date` y `category` se actualizan

- [ ] **Flujo End-to-End: Consulta Conversacional**
  - [ ] Llamar a `POST /api/chat` con "¿Cuánto gasté este mes?"
  - [ ] Verificar que la respuesta contiene el monto calculado por SQL
  - [ ] Validar que NO hay alucinaciones (Regla de Alucinación Cero)

### 1.8. Documentación de API
- [ ] **Swagger UI:** Configurar FastAPI para exponer `/docs`
- [ ] **Ejemplos de Requests:** Agregar ejemplos en docstrings de endpoints
- [ ] **Postman Collection:** Exportar colección de pruebas

---

## 📅 Fase 2: Madurez y UI (Frontend Development)
**Objetivo:** Construir la interfaz de usuario para el usuario final.

**Prerequisito:** Fase 1 completada (API funcional en localhost).

### 2.1. Definición de UX (Logic Book Update)
- [ ] **Actualizar `LOGIC.md`:** Definir contratos de API para Frontend
- [ ] **Wireframes Lógicos:** Definir flujos de pantalla (no diseño visual, solo lógica)
  - [ ] Pantalla de Login/Registro
  - [ ] Pantalla de Grabación de Voz
  - [ ] Pantalla de Lista de Transacciones (Pendientes vs Verificadas)
  - [ ] Pantalla de Chat Conversacional
  - [ ] Pantalla de Reportes (Gastos por Categoría)

### 2.2. Construcción del Frontend
- [ ] **Inicializar Proyecto:** React Native / Flutter / Next.js (TBD)
- [ ] **Componentes Core:**
  - [ ] Grabadora de Voz (con visualización de onda)
  - [ ] Captura de Foto/Documento
  - [ ] Lista de Transacciones (con estados visuales)
  - [ ] Chat UI (WebSockets o Polling)
  - [ ] Gráficos de Gastos (Chart.js / Recharts)

- [ ] **Integración con API:**
  - [ ] Autenticación JWT (almacenar token en localStorage/SecureStorage)
  - [ ] Llamadas a endpoints de Gateway
  - [ ] Manejo de errores y estados de carga

### 2.3. Pruebas de Usuario (Alpha Testing)
- [ ] **Reclutamiento:** 5-10 usuarios beta
- [ ] **Métricas de UX:**
  - [ ] Tiempo promedio para crear transacción por voz
  - [ ] Tasa de éxito de transcripción
  - [ ] Satisfacción con auto-categorización
- [ ] **Iteración:** Ajustar prompts de Gemini basado en feedback

---

## 📅 Fase 3: Migración a la Nube (Protocolo Nexus - Cloud Split)
**Objetivo:** Separar el monolito modular en microservicios independientes en Google Cloud Platform.

**Prerequisito:** Fase 2 completada (Frontend + Backend funcional).

### 3.1. Preparación para Migración
- [ ] **Auditoría de Fronteras:** Verificar que NO hay importaciones cruzadas de código interno
- [ ] **Refactor de Interfaces:** Asegurar que todos los módulos exponen solo `service.py`
- [ ] **Configuración de Entornos:** Separar configs de `dev`, `staging`, `prod`

### 3.2. Infraestructura como Código (Terraform)
- [ ] **Red y Seguridad:**
  - [ ] Definir VPC privada
  - [ ] Configurar Cloud NAT (para salida a internet controlada)
  - [ ] Reglas de firewall (solo Gateway es público)

- [ ] **Persistencia:**
  - [ ] Provisionar Cloud SQL (PostgreSQL)
  - [ ] Configurar usuarios y permisos
  - [ ] Migrar datos de SQLite local a Cloud SQL

- [ ] **Registro de Contenedores:**
  - [ ] Configurar Artifact Registry
  - [ ] Crear repositorios para cada microservicio

- [ ] **Cómputo (Cloud Run):**
  - [ ] Servicio `gateway-service` (público)
  - [ ] Servicio `ai-brain-service` (privado, solo accesible desde VPC)
  - [ ] Servicio `finance-core-service` (privado, solo accesible desde VPC)

### 3.3. Containerización (Docker)
- [ ] **`gateway/Dockerfile`:** Imagen para Gateway
- [ ] **`ai_brain/Dockerfile`:** Imagen para AIBrain
- [ ] **`finance_core/Dockerfile`:** Imagen para FinanceCore
- [ ] **Scripts de Build:**
  - [ ] `build_and_push.sh` - Construir y subir imágenes a Artifact Registry

### 3.4. Refactor de Comunicación (Import → HTTP)
- [ ] **Gateway → AIBrain:**
  ```python
  # ANTES
  from modules.ai_brain.service import transcribe_audio
  text = transcribe_audio(audio_bytes)
  
  # DESPUÉS
  import httpx
  response = httpx.post("http://ai-brain-service/api/transcribe", files={"audio": audio_bytes})
  text = response.json()["text"]
  ```

- [ ] **Gateway → FinanceCore:**
  ```python
  # ANTES
  from modules.finance_core.service import create_provisional_transaction
  transaction = create_provisional_transaction(user_id, amount, concept)
  
  # DESPUÉS
  import httpx
  response = httpx.post("http://finance-core-service/api/transactions", json={...})
  transaction = response.json()
  ```

- [ ] **Implementar Clientes HTTP:** Abstraer llamadas en `gateway/clients/`

### 3.5. Despliegue y Validación
- [ ] **Pipeline de CI/CD:**
  - [ ] GitHub Actions / Cloud Build
  - [ ] Automatizar build → test → deploy

- [ ] **Despliegue Inicial:**
  - [ ] `terraform apply` para provisionar infraestructura
  - [ ] Desplegar servicios a Cloud Run
  - [ ] Configurar variables de entorno (secrets en Secret Manager)

- [ ] **Prueba de Humo en Nube:**
  - [ ] Validar que Gateway responde en URL pública
  - [ ] Validar que AIBrain y FinanceCore son accesibles solo desde VPC
  - [ ] Ejecutar flujo End-to-End en producción

### 3.6. Monitoreo y Observabilidad
- [ ] **Logging:** Cloud Logging (logs estructurados)
- [ ] **Métricas:** Cloud Monitoring (latencia, errores, costos)
- [ ] **Alertas:**
  - [ ] Latencia > 10s en flujo de voz
  - [ ] Tasa de error > 5%
  - [ ] Costos de Gemini/Chirp > umbral mensual

---

## 📊 Matriz de Estado de Módulos

| Módulo | Tipo | Ubicación | Estado Actual | Fase |
| :--- | :--- | :--- | :--- | :--- |
| **Core** | Infraestructura | `/src/core/` | 🔴 Pendiente | Fase 1 |
| **AIBrain** | Módulo Nexus | `/src/modules/ai_brain/` | 🔴 Pendiente | Fase 1 |
| **FinanceCore** | Módulo Nexus | `/src/modules/finance_core/` | 🔴 Pendiente | Fase 1 |
| **Gateway** | Módulo Nexus | `/src/modules/gateway/` | 🔴 Pendiente | Fase 1 |
| **Frontend** | App | TBD | ⚪ Futuro | Fase 2 |
| **Cloud Infrastructure** | Infra | GCP | ⚪ Futuro | Fase 3 |

**Leyenda:**
- 🔴 Pendiente
- 🟡 En Progreso
- 🟢 Completado
- ⚪ Futuro

---

## 🧪 Estrategia de Pruebas

### Fase 1 (Local):
1.  **Unitarias:** Pruebas de lógica de negocio en cada módulo (mockeando dependencias externas)
2.  **Integración:** Pruebas de flujos completos llamando a APIs reales de Google
3.  **End-to-End:** Pruebas del flujo completo `Audio → Transacción → BD`

### Fase 2 (Frontend):
1.  **Componentes:** Pruebas de componentes UI (Jest/React Testing Library)
2.  **Integración:** Pruebas de integración Frontend ↔ Backend
3.  **E2E:** Pruebas de flujos de usuario (Cypress/Playwright)

### Fase 3 (Cloud):
1.  **Smoke Tests:** Validar que servicios responden en producción
2.  **Load Testing:** Simular carga (100 requests/min) para validar auto-scaling
3.  **Chaos Engineering:** Simular fallos de servicios para validar resiliencia

---

## 🎯 Métricas de Éxito

### Fase 1 (MVP Local):
- ✅ Flujo de voz funcional en < 8 segundos (P95)
- ✅ Precisión de transcripción > 90%
- ✅ Precisión de extracción de datos > 85%
- ✅ Cero alucinaciones en consultas deterministas

### Fase 2 (UI):
- ✅ Tiempo de onboarding < 2 minutos
- ✅ Tasa de retención (7 días) > 40%
- ✅ NPS (Net Promoter Score) > 50

### Fase 3 (Cloud):
- ✅ Uptime > 99.5%
- ✅ Latencia P95 < 10 segundos
- ✅ Costo por transacción < $0.05 USD

---

## 📝 ¿Cómo usar este documento?

1.  **Planificación:** Antes de iniciar un Sprint, revisa qué casillas tocan marcar en la fase actual.
2.  **Ejecución:** Usa los prompts para instruir al Agente Antigravity sobre la tarea específica (ej. "Implementa el módulo AIBrain según Fase 1.4 del Roadmap").
3.  **Seguimiento:** Al terminar una tarea, actualiza este archivo con `[x]`.
4.  **Revisión:** Al completar una fase, revisa que todas las casillas estén marcadas antes de avanzar.

---

## 🚀 Mantra del Protocolo Nexus

> **"Módulos soberanos hoy, Microservicios mañana. Las fronteras son sagradas."**

La arquitectura de hoy es la de producción. Solo cambia el transporte.

---

**Versión:** 2.0 (Protocolo Nexus Edition)  
**Última Actualización:** 2025-12-21  
**Estado:** Activo y Vinculante

---