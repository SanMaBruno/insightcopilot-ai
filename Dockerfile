FROM python:3.11-slim

WORKDIR /app

# Dependencias del sistema para matplotlib
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libffi-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install --no-cache-dir -e .

# Crear directorios de datos
RUN mkdir -p data/uploads data/sample

EXPOSE 8000

CMD ["uvicorn", "src.presentation.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
