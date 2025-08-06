FROM python:3.11-slim

# Instala dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de requerimientos si existen
COPY requirements.txt ./

# Instala dependencias de Python
RUN pip install --upgrade pip
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

# Copia el resto del código fuente
COPY . .

# Expone el puerto por defecto para SSE (ajusta si es necesario)
EXPOSE 8000

# Comando de inicio (ajusta el path si tu entrypoint es diferente)
CMD ["python", "__main__.py", "--transport", "sse", "--host", "0.0.0.0", "--port", "8000"]
