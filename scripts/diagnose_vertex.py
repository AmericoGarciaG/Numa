"""
Script de Diagnóstico para Vertex AI.
Prueba la disponibilidad de diferentes versiones de modelos Gemini.
"""

import os
import sys
import vertexai
from vertexai.generative_models import GenerativeModel

# Force UTF-8 for Windows consoles
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Agregar raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Force credentials path
creds_path = os.path.abspath("credentials.json")
if os.path.exists(creds_path):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
else:
    print("⚠️  ADVERTENCIA: credentials.json no encontrado en raíz.")

try:
    from src.core.config import settings
except ImportError:
    print("❌ No se pudo importar configuración.")
    sys.exit(1)

def check_model(model_name):
    print(f"Probando modelo: '{model_name}'...", end=" ")
    try:
        model = GenerativeModel(model_name)
        # Hacer una llamada dummy muy barata (count tokens o generate simple)
        response = model.generate_content("Hi", stream=False)
        print(f"✅ DISPONIBLE. (Respuesta: {len(response.text)} chars)")
        return True
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg:
            print("❌ NO ENCONTRADO (404)")
        elif "403" in error_msg:
            print("⛔ SIN PERMISO (403)")
        else:
            print(f"⚠️ ERROR: {error_msg[:100]}...")
        return False

def main():
    print(f"Inicializando Vertex AI...")
    print(f"Proyecto: {settings.GOOGLE_PROJECT_ID}")
    print(f"Región: {settings.GOOGLE_LOCATION}")
    
    try:
        vertexai.init(project=settings.GOOGLE_PROJECT_ID, location=settings.GOOGLE_LOCATION)
    except Exception as e:
        print(f"🔥 Error fatal al inicializar Vertex AI: {e}")
        return

    print("\n--- Iniciando Sondeo de Modelos ---\n")

    candidates = [
        "gemini-1.5-flash-001",
        "gemini-1.5-flash",
        "gemini-2.0-flash-exp",
        "gemini-1.0-pro", 
        "gemini-1.0-pro-001",
        "gemini-1.5-pro-001",
        "gemini-1.5-pro",
        "gemini-pro"
    ]
    
    found_any = False
    for m in candidates:
        if check_model(m):
            found_any = True

    print("\n--- Fin del Diagnóstico ---")
    if not found_any:
        print("🔴 Ningún modelo funcionó. EL PROYECTO TIENE BLOQUEO DE API O CUOTA.")

if __name__ == "__main__":
    main()
