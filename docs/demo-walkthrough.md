# Demo Walkthrough — InsightCopilot AI

Guía paso a paso para mostrar el proyecto en una demo profesional.

## Requisitos previos

```bash
# Backend
cd insightcopilot-ai
source .venv/bin/activate
pip install -r requirements.txt
pip install -e ".[dev]"

# Frontend
cd frontend
npm install
```

## 1. Levantar los servicios

```bash
# Terminal 1 — Backend
uvicorn src.presentation.api.app:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend && npm run dev
```

Abrir `http://localhost:5173` en el navegador.

## 2. Pantalla de inicio

- Mostrar la **Home** que explica las capacidades del producto.
- Señalar el flujo de 4 pasos: Subir → Explorar → Preguntar → Resumir.
- Hacer clic en **"Comenzar"** para ir a Datasets.

## 3. Subir dataset de ejemplo

- En la pantalla **Datasets**, hacer clic en **"Subir CSV"**.
- Seleccionar el archivo `data/sample/ecommerce_products.csv`.
- Esperar la confirmación verde de upload exitoso.
- El dataset aparece en la lista.

## 4. Explorar Profile

- Hacer clic en el dataset **ecommerce_products**.
- Se abre en la pestaña **Profile** automáticamente.
- Mostrar:
  - Conteo de filas (30) y columnas (10).
  - Tabla de columnas con tipo, nulos y valores únicos.
  - Señalar que hay 2 campos con nulos (units_sold en P011, price en P019).

## 5. Ver Insights

- Cambiar a la pestaña **Insights**.
- Mostrar:
  - El resumen general del dataset.
  - Los insights clasificados por categoría (info, warning, critical).
  - Las advertencias sobre nulos.

## 6. Visualizaciones

- Cambiar a la pestaña **Charts**.
- Mostrar los gráficos generados automáticamente:
  - Histogramas de columnas numéricas (price, units_sold, rating).
  - Gráfico de barras de categorías (category, region).
  - Matriz de correlación.

## 7. Consulta analítica

- Cambiar a la pestaña **Query**.
- Esta sección **no requiere API key** — funciona localmente.
- Probar estas consultas:
  - `"¿Cuántas filas tiene el dataset?"` → Respuesta con conteo.
  - `"resumen"` → Resumen estadístico general.
  - `"nulos"` → Información sobre valores faltantes.
  - `"columnas numéricas"` → Lista de columnas numéricas.
- Mostrar el intent detectado y los datos de soporte.

## 8. Executive Summary (requiere OpenAI API key)

- Cambiar a la pestaña **Summary (LLM)**.
- Configurar audiencia ("equipo técnico") y tono ("profesional").
- Hacer clic en **"Generar resumen"**.
- El sistema genera un resumen ejecutivo basado en el perfil e insights.

> **Nota:** Si no hay API key configurada, se mostrará un error. Esto es esperado. Mencionar que el feature está implementado y conectado.

## 9. RAG Query (requiere OpenAI API key + documentos indexados)

- Cambiar a la pestaña **RAG (LLM)**.
- Para una demo completa con RAG:

```bash
# Subir documento
curl -X POST http://localhost:8000/documents/upload \
  -F "file=@data/sample/product_strategy.md"

# Indexar documento
curl -X POST http://localhost:8000/documents/index \
  -H "Content-Type: application/json" \
  -d '{"file_path": "data/uploads/product_strategy.md"}'
```

- Luego preguntar: `"¿Cuál es la estrategia para la categoría Electronics?"`.
- El sistema combina datos del dataset con el documento para responder.

> **Nota:** Requiere API key. Sin ella, mostrar la arquitectura RAG y explicar el flujo.

## 10. Mostrar API docs

- Abrir `http://localhost:8000/docs` para la documentación Swagger interactiva.
- Señalar los 14 endpoints organizados por categoría.
- Mostrar el endpoint `/health` como ejemplo de observabilidad.

## 11. Mostrar calidad de código

```bash
# Tests (172 passing)
pytest

# Linter (sin warnings)
ruff check src/ tests/

# TypeScript (sin errores)
cd frontend && npx tsc --noEmit
```

## 12. Cierre

Puntos clave a destacar:

- **Clean Architecture** con 5 capas y regla de dependencia estricta.
- **SOLID** aplicado en cada decisión de diseño.
- **172 tests** unitarios con aislamiento completo.
- **CI/CD** con GitHub Actions (backend + frontend).
- **Docker** ready con health check.
- **14 endpoints** REST documentados.
- **Frontend** React + TypeScript profesional conectado al backend.

## Datos de ejemplo incluidos

| Archivo | Descripción | Uso |
|---|---|---|
| `data/sample/ecommerce_products.csv` | 30 productos e-commerce con 10 columnas | Dataset principal para demo |
| `data/sample/product_strategy.md` | Estrategia de producto Q1-Q2 2024 | Documento para RAG |
| `data/sample/test_data.csv` | Dataset mínimo de 3 filas | Tests rápidos |
