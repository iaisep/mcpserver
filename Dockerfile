FROM python:3.11-slim

RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -U pip && if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

COPY . .

EXPOSE 8000
# Llamada explícita a fastmcp con el host correcto
ENTRYPOINT ["python", "-m", "fastmcp", "serve"]
CMD ["--transport", "sse", "--host", "0.0.0.0", "--port", "8000"]
