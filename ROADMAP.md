# 🗺️ Numa: Plan Maestro de Construcción (Protocolo Nexus Roadmap)

**Estado del Proyecto:** 🏗️ Fase 2 - Implementación FIM (En Progreso)
**Metodología:** Kybern (DBBD) + Protocolo Nexus
**Estrategia:** Local-First → Cloud Migration

Este documento rastrea la evolución del sistema Numa desde su concepción lógica hasta su despliegue en producción. Se divide en Fases de Maduración bajo el **Protocolo Nexus**.

---

## 📅 Fase 1: MVP Local Real (Monolito Modular)
**Objetivo:** Construir un prototipo funcional en `localhost` usando servicios reales de Google, sin Docker ni complejidad de infraestructura.

**Filosofía:** Local-First. Hacer que el sistema funcione en tu máquina antes de pensar en la nube.

> **✅ FASE COMPLETADA:** 21/12/2025.
> Validado exitosamente con Google Speech V2 (`latest_long`) y Vertex AI (`gemini-2.0-flash-exp`). Persistencia inteligente activa.

### 1.1. Fundamentos del Protocolo Nexus ✅
- [x] **GOVERNANCE.md v3.0:** Definir el Protocolo Nexus y la Regla de Oro de la Comunicación.
- [x] **LOGIC.md v2.0:** Reescribir contratos de negocio para arquitectura modular con Google-only stack.
- [x] **ONBOARDING.md (Actualizado):** Guía Local-First para colaboradores.
- [x] **ROADMAP.md (Este documento):** Plan de fases alineado con Protocolo Nexus.

### 1.2. Estructura de Directorios Obligatoria ✅
- [x] **Crear `/src` como raíz del código:**
  - [x] `/src/modules/gateway/` - Orquestador de negocio
  - [x] `/src/modules/ai_brain/` - Cerebro de inferencia (Google AI)
  - [x] `/src/modules/finance_core/` - Motor contable
  - [x] `/src/core/` - Infraestructura compartida (DB, Auth, Config)
  - [x] `/src/main.py` - Punto de entrada FastAPI

### 1.3. Módulo: Core (Infraestructura Compartida) ✅
- [x] **`core/config.py`:** Gestión de variables de entorno (`.env`)
- [x] **`core/database.py`:** Conexión a SQLite local (desarrollo) con SQLAlchemy
- [x] **`core/auth.py`:** Autenticación JWT (generación y validación de tokens)
- [x] **Script de inicialización:** `python -m src.core.database init` para crear tablas

### 1.4. Módulo: AIBrain (El Cerebro de Inferencia) ✅
- [x] **`ai_brain/service.py` (Interfaz Pública):**
  - [x] `transcribe_audio(audio_bytes: bytes, language: str) -> str`
  - [x] `extract_transaction_data(text: str) -> TransactionData`
  - [x] `analyze_document(image_bytes: bytes) -> DocumentData`
  - [x] `classify_category(concept: str, merchant: str) -> str`
  - [x] `answer_query(query: str, context: dict) -> str`

### 1.5. Módulo: FinanceCore (El Motor Contable) ✅
- [x] **`finance_core/models.py`:** Modelos SQLAlchemy
  - [x] `User` (id, email, hashed_password, created_at)
  - [x] `Transaction` (id, user_id, amount, concept, status, merchant, transaction_date, category, created_at, verified_at)
  - [x] Estados: `PROVISIONAL`, `VERIFIED`, `VERIFIED_MANUAL`

### 1.6. Módulo: Gateway (El Orquestador) ✅
- [x] **`gateway/routes.py`:** Endpoints FastAPI
  - [x] `POST /api/auth/register` - Registro de usuario
  - [x] `POST /api/auth/login` - Login (devuelve JWT)
  - [x] `POST /api/transactions/voice` - Ingesta de audio

### 1.7. Integración y Pruebas Locales ✅
- [x] **Flujo End-to-End: Voz → Transacción**
- [x] **Flujo End-to-End: Documento → Verificación**
- [x] **Flujo End-to-End: Consulta Conversacional**

---

## 📅 Fase 2: Implementación del FIM (Router Semántico)
**Objetivo:** Evolucionar el sistema de un "registrador de gastos" a un "Director Financiero Personal" mediante un motor de intención conversacional.

**Contexto:** El usuario ya no solo dicta gastos, sino que conversa. El sistema debe entender la diferencia entre "Gasté 500" (WRITE), "¿Cuánto gasté?" (READ) y "Quiero ahorrar" (PLAN).

### 2.1. Refactorización del AI Brain (Semantic Router)
- [ ] **Definir Prompt de Clasificación:** Crear prompt maestro para clasificar intents (`WRITE`, `READ`, `PLAN`, `ADVICE`, `STEER`).
- [ ] **Implementar `classify_intent(text: str) -> IntentData`:** Nueva función en `ai_brain` que devuelve JSON con intent y entidades.
- [ ] **Actualizar Extracción:** Adaptar la extracción de entidades para soportar ingresos y deudas, no solo gastos.

### 2.2. Actualización del Finance Core (Modelo de Datos)
- [ ] **Migración de Base de Datos:**
    - [ ] Actualizar modelo `Transaction` para incluir campo `type` (`EXPENSE`, `INCOME`, `DEBT`).
    - [ ] Crear migraciones (o script de alter table para SQLite).
- [ ] **Implementar nuevas operaciones:**
    - [ ] Soportar creación de Ingresos y Deudas.
    - [ ] Consultas avanzadas para soportar preguntas de tipo READ.

### 2.3. Orquestación en Gateway
- [ ] **Modificar `POST /api/chat` (o endpoint unificado):**
    - [ ] Integrar el flujo: Transcribir -> Router Semántico -> Ejecución -> Respuesta.
- [ ] **Handlers por Intención:**
    - [ ] `handle_write_intent`: Crea transacciones.
    - [ ] `handle_read_intent`: Consulta BD y genera resumen.
    - [ ] `handle_advice_intent`: Consulta LLM puro.

### 2.4. Pruebas del Motor de Intención
- [ ] **Test Set de Frases:** Validar clasificación correcta de 50 frases de prueba.
- [ ] **Validación de Flujos:** Verificar que un "Ingreso" suma y un "Gasto" resta.

---

## 📅 Fase 3: Madurez y UI (Frontend Development)
**Objetivo:** Construir la interfaz de usuario para el usuario final.

**Prerequisito:** Fase 2 completada (API Inteligente funcional).

### 3.1. Definición de UX
- [ ] **Wireframes Adaptativos:** Definir cómo se ve la UI para cada intención (Tarjeta vs Chat vs Gráfica).

### 3.2. Construcción del Frontend
- [ ] **Inicializar Proyecto:** React Native / Flutter / Next.js (TBD).
- [ ] **Componentes Core:** Chat Interface como centro de la experiencia.

---

## 📅 Fase 4: Migración a la Nube (Protocolo Nexus - Cloud Split)
**Objetivo:** Separar el monolito modular en microservicios independientes en Google Cloud Platform.

### 4.1. Preparación para Migración
- [ ] **Auditoría de Fronteras:** Verificar que NO hay importaciones cruzadas de código interno.

### 4.2. Infraestructura como Código (Terraform)
- [ ] **Persistencia:** Cloud SQL.
- [ ] **Cómputo:** Cloud Run.

---

## 📊 Matriz de Estado de Módulos

| Módulo | Tipo | Ubicación | Estado Actual | Fase |
| :--- | :--- | :--- | :--- | :--- |
| **Core** | Infraestructura | `/src/core/` | 🟢 Completado | Fase 1 |
| **AIBrain** | Módulo Nexus | `/src/modules/ai_brain/` | 🟡 En Refactor | Fase 2 |
| **FinanceCore** | Módulo Nexus | `/src/modules/finance_core/` | 🟡 En Refactor | Fase 2 |
| **Gateway** | Módulo Nexus | `/src/modules/gateway/` | 🟡 En Refactor | Fase 2 |
| **Frontend** | App | TBD | ⚪ Futuro | Fase 3 |
| **Cloud Infrastructure** | Infra | GCP | ⚪ Futuro | Fase 4 |

**Leyenda:**
- 🔴 Pendiente
- 🟡 En Progreso
- 🟢 Completado
- ⚪ Futuro

---

## 🎯 Métricas de Éxito

### Fase 2 (FIM):
- ✅ Precisión de clasificación de intención > 95%
- ✅ Latencia del Router Semántico < 500ms
- ✅ Soporte correcto de Ingresos y Gastos

---

**Versión:** 3.0 (Kybern FIM Standard)
**Última Actualización:** 2025-12-22
**Estado:** Activo y Vinculante
