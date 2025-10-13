"""
Simulaciones de datos para el MVP de Numa.

Este módulo contiene todos los datos hardcodeados que simulan las respuestas
de servicios de AI/ML que serán reemplazados por llamadas a APIs reales.

Incluye:
- Transcripción de voz simulada
- Datos de verificación de documentos simulados
- Mapeo de categorización automática
- Keywords para categorización por concepto
"""

from datetime import datetime

# Simulación de transcripción de audio (Rule 2.1 - Step 1)
DEFAULT_VOICE_TRANSCRIPTION = "gasté 120 pesos en la cena"

# Simulación de datos de verificación de documentos (Rule 2.2 - Step 2)
DEFAULT_VERIFICATION_DATA = {
    "amount": 122.50,
    "vendor": "La Trattoria",
    "transaction_date": datetime.now(),
}

# Mapeo de merchants conocidos a categorías (Rule 2.4)
# Este mapeo simula el conocimiento de un LLM sobre categorización de comercios
CATEGORY_MAP = {
    # Alimentación y Restaurantes
    "La Trattoria": "Restaurantes",
    "Starbucks": "Alimentación", 
    "McDonald's": "Alimentación",
    "Subway": "Alimentación",
    "Pizza Hut": "Restaurantes",
    "KFC": "Alimentación",
    
    # Transporte
    "Uber": "Transporte",
    "Cabify": "Transporte",
    "Didi": "Transporte",
    "Metro": "Transporte",
    "Gasolina": "Transporte",
    
    # Entretenimiento
    "Cine": "Entretenimiento",
    "Netflix": "Entretenimiento",
    "Spotify": "Entretenimiento",
    "Steam": "Entretenimiento",
    "PlayStation": "Entretenimiento",
    
    # Compras y Retail
    "Amazon": "Compras",
    "Mercado Libre": "Compras",
    "Walmart": "Supermercado",
    "Soriana": "Supermercado",
    "Oxxo": "Conveniencia",
    
    # Servicios
    "CFE": "Servicios",
    "Telmex": "Servicios",
    "Telcel": "Servicios",
    "Agua": "Servicios",
    "Gas": "Servicios",
    
    # Salud y Farmacia
    "Farmacia": "Salud",
    "Hospital": "Salud",
    "Doctor": "Salud",
    "Dentista": "Salud",
    
    # Educación
    "Colegio": "Educación",
    "Universidad": "Educación",
    "Curso": "Educación",
    "Libros": "Educación",
}

# Mapeo de keywords en conceptos a categorías (Rule 2.4 fallback)
# Este mapeo simula análisis de NLP de conceptos cuando el merchant no es conocido
CONCEPT_KEYWORDS = {
    # Alimentación
    "cena": "Restaurantes",
    "desayuno": "Alimentación", 
    "comida": "Alimentación",
    "almuerzo": "Restaurantes",
    "café": "Alimentación",
    "pizza": "Restaurantes",
    "hamburguesa": "Alimentación",
    "tacos": "Restaurantes",
    "sushi": "Restaurantes",
    
    # Transporte
    "taxi": "Transporte",
    "uber": "Transporte",
    "gasolina": "Transporte",
    "metro": "Transporte",
    "bus": "Transporte",
    "avión": "Transporte",
    "vuelo": "Transporte",
    
    # Entretenimiento
    "cine": "Entretenimiento",
    "película": "Entretenimiento",
    "concierto": "Entretenimiento",
    "juego": "Entretenimiento",
    "streaming": "Entretenimiento",
    
    # Compras
    "ropa": "Compras",
    "zapatos": "Compras",
    "electrónicos": "Compras",
    "teléfono": "Compras",
    "laptop": "Compras",
    
    # Supermercado
    "supermercado": "Supermercado",
    "mercado": "Supermercado",
    "despensa": "Supermercado",
    "víveres": "Supermercado",
    
    # Servicios
    "luz": "Servicios",
    "agua": "Servicios",
    "gas": "Servicios",
    "internet": "Servicios",
    "teléfono": "Servicios",
    
    # Salud
    "medicina": "Salud",
    "doctor": "Salud",
    "hospital": "Salud",
    "farmacia": "Salud",
    "dentista": "Salud",
    
    # Educación
    "colegiatura": "Educación",
    "escuela": "Educación",
    "universidad": "Educación",
    "curso": "Educación",
    "libro": "Educación",
}

# Categoría por defecto cuando no se puede determinar automáticamente
DEFAULT_CATEGORY = "Otros"

# Keywords para detección de categorías en consultas de chat (Rule 3.2)
CHAT_CATEGORY_KEYWORDS = {
    "restaurantes": "Restaurantes",
    "restaurant": "Restaurantes", 
    "cena": "Restaurantes",
    "almuerzo": "Restaurantes",
    "alimentación": "Alimentación",
    "comida": "Alimentación",
    "café": "Alimentación",
    "cafe": "Alimentación",
    "starbucks": "Alimentación",
    "supermercado": "Supermercado",
    "walmart": "Supermercado",
    "transporte": "Transporte",
    "uber": "Transporte",
    "taxi": "Transporte",
    "entretenimiento": "Entretenimiento",
    "cine": "Entretenimiento",
    "netflix": "Entretenimiento",
    "compras": "Compras",
    "ropa": "Compras",
    "servicios": "Servicios",
    "luz": "Servicios",
    "agua": "Servicios",
    "gas": "Servicios",
    "salud": "Salud",
    "farmacia": "Salud",
    "doctor": "Salud",
    "educación": "Educación",
    "escuela": "Educación",
    "universidad": "Educación",
}

# Mensajes de simulación para logging/debugging
SIMULATION_MESSAGES = {
    "voice_transcription": "🎤 Simulando transcripción de audio",
    "document_analysis": "🧾 Simulando análisis multimodal de documento", 
    "categorization": "🏷️ Aplicando categorización automática",
    "concept_analysis": "🧠 Analizando concepto para categorización fallback",
}