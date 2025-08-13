FROM python:3.11-slim

RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -U pip && if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

COPY . .

# Fuerza host/puerto para Uvicorn aunque FastMCP lo lance internamente
ENV UVICORN_CMD_ARGS="--host 0.0.0.0 --port 8000"

EXPOSE 8000

# Mantén tu arranque actual
CMD ["python", "__main__.py", "--transport", "sse", "--port", "8000"]
