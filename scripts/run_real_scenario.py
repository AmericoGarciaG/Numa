"""
Script de Validación End-to-End (E2E) para Numa (Protocolo Nexus).
Simula un flujo de usuario completo usando TestClient.
"""

import json
import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient

# Agregar raíz al path para importar módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Force UTF-8 for Windows consoles
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Force credentials path
creds_path = os.path.abspath("credentials.json")
if os.path.exists(creds_path):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path

try:
    from src.core.database import Base, SessionLocal, engine
    from src.main import app
except ImportError as e:
    print(f"Error importando módulos: {e}")
    sys.exit(1)

# Inicializar cliente
client = TestClient(app)

# Configuración
TEST_EMAIL = "e2e_user@example.com"
TEST_PASSWORD = "password123"
AUDIO_FILE = "tests/test_audio.mp3"


def print_section(title):
    print(f"\n{'='*50}\n{title}\n{'='*50}")


def run_scenario():
    print_section("Validación E2E Numa con Google AI Real")

    # 1. Registro de Usuario (Idempotente)
    print("1. Registrando/Logueando usuario...")
    # Intentamos registrar, si falla asumimos que existe
    client.post(
        "/api/users/",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD, "name": "E2E User"},
    )

    # Login para obtener Token
    login_response = client.post(
        "/api/token", data={"username": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    if login_response.status_code != 200:
        print(f"❌ Login fallido: {login_response.text}")
        return

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login exitoso. Token obtenido.")

    # 2. Enviar Audio (Voice Transaction)
    print("\n2. Enviando audio a /api/transactions/voice...")
    if not os.path.exists(AUDIO_FILE):
        print(f"❌ Archivo de audio no encontrado en {AUDIO_FILE}")
        return

    try:
        with open(AUDIO_FILE, "rb") as f:
            files = {"audio_file": ("test_audio.mp3", f, "audio/mpeg")}
            response = client.post(
                "/api/transactions/voice", headers=headers, files=files
            )

        print(f"Status Code: {response.status_code}")
        if response.status_code in [200, 201]:
            print("✅ Transacción creada exitosamente.")
            print(
                f"Respuesta JSON (Lo que entendió Gemini):\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}"
            )
        else:
            print(f"❌ Error en transacción: {response.text}")
            return

    except Exception as e:
        print(f"❌ Excepción durante envío: {e}")
        return

    # 3. Verificación en Listado
    print("\n3. Verificando persistencia en BD...")
    list_response = client.get("/api/transactions/", headers=headers)
    transactions = list_response.json()

    # Buscar la última
    if transactions:
        latest = transactions[-1]
        print(f"✅ Última transacción encontrada en BD:")
        print(f"   ID: {latest.get('id')}")
        print(f"   Concepto: {latest.get('concept')}")
        print(f"   Monto: {latest.get('amount')}")
        print(f"   Estado: {latest.get('status')}")
    else:
        print("⚠️ No se encontraron transacciones en el listado.")


if __name__ == "__main__":
    # Asegurar tablas creadas
    Base.metadata.create_all(bind=engine)
    run_scenario()
