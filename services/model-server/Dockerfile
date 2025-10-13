# Usamos la imagen oficial de Ollama
FROM ollama/ollama

# Durante la construcción de la imagen, descargamos los modelos que usaremos.
# Esto evita tener que descargarlos cada vez que el contenedor inicia.
RUN ollama pull llama3:8b   # Un excelente modelo de lenguaje para empezar.
RUN ollama pull whisper     # El modelo de transcripción de OpenAI.