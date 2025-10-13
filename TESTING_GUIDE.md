# Guía de Pruebas End-to-End para Numa (Arquitectura de 3 Servicios)

Esta guía te mostrará cómo lanzar y probar la comunicación entre los tres microservicios: `numa-api`, `mcp-server`, y `model-server`.

## Paso 1: Configuración de los Servicios

Antes de lanzar, necesitamos configurar cómo se hablarán los servicios.

1.  **Configurar el `mcp-server`:**
    *   Dentro de `services/mcp-server`, clona el código de `llm-mcp-server-py`.
    *   Crea un archivo `.env` dentro de `services/mcp-server`.
    *   Añade la siguiente configuración para decirle al MCP dónde encontrar nuestros modelos locales servidos por Ollama. **`model-server`** es el nombre del servicio en la red de Docker.

    ```dotenv
    # URL de nuestro servidor de modelos Ollama
    OLLAMA_API_BASE_URL=http://model-server:11434

    # Mapeamos nombres de modelo a los modelos reales en Ollama
    # Esto nos permite pedir "whisper-1" y que el MCP lo enrute a nuestro modelo Whisper local
    MODEL_ALIASES={"whisper-1": "ollama/whisper", "gpt-4o": "ollama/llama3:8b"}
    ```

2.  **Configurar el `numa-api`:**
    *   Abre el archivo `.env` que ya existe en `services/numa-api/.env`.
    *   Añade la siguiente línea para decirle a Numa dónde encontrar el servidor MCP:
    ```dotenv
    MCP_SERVER_URL=http://mcp-server:8001
    ```

## Paso 2: Lanzar el Sistema Completo

1.  Abre una terminal en la raíz del proyecto (donde está `docker-compose.yml`).
2.  Ejecuta el siguiente comando:
    ```bash
    docker-compose up --build
    ```
3.  Docker comenzará a construir las imágenes de los 3 servicios. La primera vez, esto puede tardar varios minutos mientras descarga Ollama y los modelos de IA. Sé paciente.
4.  Verás los logs de los tres servicios en tu terminal. Espera a que se estabilicen y no muestren errores.

## Paso 3: Probar el Flujo Completo (Audio -> IA -> Respuesta)

1.  Abre tu navegador web y ve a la **interfaz de documentación de Numa API**:
    [http://localhost:8000/docs](http://localhost:8000/docs)

2.  **Crea un usuario y obtén un token:**
    *   Usa el endpoint `POST /users/` para registrar un nuevo usuario.
    *   Usa el endpoint `POST /token` con las credenciales que acabas de crear para obtener un `access_token`. Copia este token.

3.  **Autoriza tus peticiones:**
    *   Haz clic en el botón "Authorize" en la parte superior derecha de la página.
    *   En el campo "value", escribe `Bearer ` (la palabra "Bearer" seguida de un espacio) y luego pega tu token. Haz clic en "Authorize".

4.  **Ejecuta la prueba de IA:**
    *   Busca el endpoint `POST /transactions/voice`.
    *   Haz clic en "Try it out".
    *   Sube un archivo de audio de prueba (puedes usar `services/numa-api/tests/audio_dummy.mp3` si existe, o grabar tu propia voz diciendo algo como "gasté 25 pesos en un refresco").
    *   Haz clic en "Execute".

## Paso 4: Analizar el Resultado

Si todo ha funcionado, deberías ver una respuesta JSON con un código 201. La clave está en los campos `amount` y `concept`.

*   **NO** deberían ser los valores hardcodeados de antes (ej. 120 y "la cena").
*   Deberían ser los valores que el modelo **Llama 3** extrajo del texto que **Whisper** transcribió de tu audio.

**¡Si esto ocurre, has validado exitosamente que todo el flujo de IA soberana funciona!**

---
**Diagrama del Flujo de la Prueba:**

`Tu Navegador` --(audio)--> `[Numa API]` --> `[MCP Server]` --> `[Model Server (Whisper)]` --> `[MCP Server]` --> `[Model Server (Llama 3)]` --> `[MCP Server]` --> `[Numa API]` --(json)--> `Tu Navegador`