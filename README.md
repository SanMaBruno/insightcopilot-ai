# InsightCopilot AI

Plataforma analítica con inteligencia artificial para exploración de datos, comprensión documental y generación de insights — construida con **Clean Architecture** y estándares profesionales de ingeniería de software.

> **Portfolio project** — demuestra Data Science + AI Software Engineering + buenas prácticas de arquitectura en un solo sistema cohesivo.

---

## Qué hace

| Capacidad | Descripción |
|---|---|
| **Perfilado automático** | Carga un CSV y obtiene estadísticas descriptivas por columna (tipos, nulos, media, percentiles). |
| **Generación de insights** | Detecta patrones, outliers y correlaciones en los datos y los clasifica por severidad. |
| **Visualizaciones** | Genera gráficos con Matplotlib (histogramas, barras, correlación) y los devuelve en base64. |
| **Consulta analítica** | Responde preguntas en lenguaje natural sobre los datos cargados (filtros, agrupaciones, métricas). |
| **Executive summary (LLM)** | Genera resúmenes ejecutivos enriquecidos con GPT-4o-mini a partir del perfil e insights. |
| **RAG documental** | Indexa documentos (.txt, .md), los fragmenta, genera embeddings y responde preguntas contextuales. |
| **Health & observability** | Endpoint /health, logging estructurado, middleware de request logging, error handlers globales. |

---

## Arquitectura

El proyecto sigue **Clean Architecture** organizada en 5 capas con regla de dependencia estricta:

```
src/
├── presentation/       ← API REST (FastAPI, schemas, middleware)
│   └── api/
│       ├── routes/          health, datasets, documents
│       ├── schemas/         request/response models (Pydantic)
│       ├── middleware.py    request logging
│       └── error_handlers.py
│
├── application/        ← Casos de uso y servicios de orquestación
│   ├── use_cases/           12 use cases (uno por acción)
│   └── services/            insight_generator, query_resolver, text_chunker, ...
│
├── domain/             ← Núcleo de negocio puro (sin dependencias externas)
│   ├── entities/            Dataset, DatasetProfile, Insight, ExecutiveSummary, ...
│   ├── repositories/        contratos abstractos (DatasetRepository, LlmClient, ...)
│   └── value_objects/       DocumentChunk, ColumnProfile
│
├── infrastructure/     ← Implementaciones concretas
│   ├── files/               CsvDatasetLoader, LocalFileStorage
│   ├── persistence/         SqliteDatasetRepository, InMemoryDatasetRepository
│   ├── llm/                 OpenAiLlmClient, OpenAiEmbeddingFunction, InMemoryVectorStore
│   └── logging/             setup_logging()
│
└── shared/             ← Transversales
    ├── config/              Settings (pydantic-settings + .env)
    ├── exceptions/          DomainError
    └── utils/               date_utils
```

**Regla de dependencia:** las capas internas (`domain`) nunca importan de las externas (`infrastructure`). La comunicación se hace a través de contratos (interfaces abstractas).

### Principios aplicados

| Principio | Aplicación |
|---|---|
| **SRP** | Cada use case tiene una sola responsabilidad (ej: `GenerateInsightsUseCase`). |
| **OCP** | Nuevas fuentes de datos se agregan implementando `DatasetLoader`, sin tocar código existente. |
| **LSP** | `InMemoryDatasetRepository` y `SqliteDatasetRepository` son intercambiables. |
| **ISP** | Contratos pequeños y específicos (`LlmClient`, `DocumentRetriever`, `FileStorage`). |
| **DIP** | Los use cases dependen de abstracciones, no de implementaciones concretas. |

---

## API endpoints

### Health
| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/health` | Estado del servicio + versión |

### Datasets
| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/datasets` | Crear dataset desde JSON |
| `POST` | `/datasets/upload` | Subir archivo CSV |
| `GET` | `/datasets` | Listar todos los datasets |
| `GET` | `/datasets/{id}` | Obtener dataset por ID |
| `GET` | `/datasets/{id}/profile` | Perfil estadístico completo |
| `GET` | `/datasets/{id}/insights` | Insights generados automáticamente |
| `GET` | `/datasets/{id}/visualizations` | Gráficos en base64 |
| `POST` | `/datasets/{id}/query` | Consulta analítica en lenguaje natural |
| `POST` | `/datasets/{id}/executive-summary` | Resumen ejecutivo con LLM |
| `POST` | `/datasets/{id}/rag-query` | Pregunta RAG sobre documentos |
| `POST` | `/datasets/{id}/enriched-summary` | Resumen enriquecido con documentos |

### Documents
| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/documents/upload` | Subir documento (.txt, .md) |
| `POST` | `/documents/index` | Indexar documentos para RAG |

---

## Stack tecnológico

| Categoría | Tecnología |
|---|---|
| Lenguaje | Python 3.9+ |
| API | FastAPI + Uvicorn |
| Validación | Pydantic v2, pydantic-settings |
| Datos | Pandas |
| Visualización | Matplotlib |
| IA | OpenAI (GPT-4o-mini, text-embedding-3-small) |
| Persistencia | SQLite |
| Testing | pytest, httpx |
| Linting | Ruff, MyPy |
| Contenedores | Docker, Docker Compose |

---

## Setup local

```bash
# Clonar
git clone https://github.com/SanMaBruno/insightcopilot-ai.git
cd insightcopilot-ai

# Entorno virtual
python -m venv .venv
source .venv/bin/activate

# Dependencias
pip install -r requirements.txt
pip install -e ".[dev]"

# Variables de entorno
cp .env.example .env
# Editar .env con tu OPENAI_API_KEY si vas a usar funciones LLM

# Tests
pytest

# Linter
ruff check src/ tests/

# Servidor
uvicorn src.presentation.api.app:app --reload
```

La API queda disponible en `http://localhost:8000`. Documentación interactiva en `http://localhost:8000/docs`.

---

## Setup con Docker

```bash
# Configurar variables
cp .env.example .env

# Levantar
docker compose up --build

# En background
docker compose up --build -d

# Verificar salud
curl http://localhost:8000/health
```

---

## Variables de entorno

| Variable | Descripción | Default |
|---|---|---|
| `APP_ENV` | Entorno de ejecución | `development` |
| `LOG_LEVEL` | Nivel de logging (DEBUG, INFO, WARNING) | `INFO` |
| `OPENAI_API_KEY` | API key de OpenAI | — |
| `OPENAI_MODEL` | Modelo para generación de texto | `gpt-4o-mini` |
| `EMBEDDING_MODEL` | Modelo para embeddings | `text-embedding-3-small` |
| `DATABASE_URL` | Ruta de la base de datos SQLite | `data/insightcopilot.db` |
| `UPLOAD_DIR` | Directorio para archivos subidos | `data/uploads` |

---

## Testing

```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=src --cov-report=term-missing

# Solo unitarios
pytest tests/unit/

# Solo integración
pytest tests/integration/
```

---

## Estructura del proyecto

```
insightcopilot-ai/
├── src/                    # Código fuente (5 capas)
├── tests/                  # Tests unitarios e integración
│   ├── unit/
│   └── integration/
├── data/                   # Datasets y uploads
├── docs/                   # ADRs y documentación
├── notebooks/              # Notebooks de exploración
├── Dockerfile              # Imagen de producción
├── docker-compose.yml      # Orquestación local
├── pyproject.toml          # Config de proyecto y herramientas
├── requirements.txt        # Dependencias de producción
└── .env.example            # Plantilla de variables
```

---

## Roadmap

- [x] Estructura base con Clean Architecture
- [x] Entidad de dominio y primer caso de uso
- [x] Persistencia (SQLite + in-memory)
- [x] API REST con FastAPI
- [x] Carga y perfilado de datasets CSV
- [x] Generación de insights automáticos
- [x] Visualizaciones con Matplotlib
- [x] Consulta analítica en lenguaje natural
- [x] Executive summary con LLM (OpenAI)
- [x] RAG documental (indexación + consulta)
- [x] Observabilidad (health, logging, error handlers, CORS)
- [x] Docker y Docker Compose
- [x] CI/CD (GitHub Actions)
- [x] Frontend base (React + TypeScript + Vite)

---

## Decisiones arquitectónicas

Las decisiones técnicas están documentadas como ADRs en `docs/decisions/`:

- **ADR-001**: Clean Architecture con 5 capas
- **ADR-002**: Dependencias mínimas y sustituibles

---

## Licencia

MIT