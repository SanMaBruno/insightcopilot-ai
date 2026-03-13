<div align="center">

# InsightCopilot AI

**Plataforma analítica con inteligencia artificial para exploración de datos, comprensión documental y generación de insights.**

Sube un CSV → obtén perfilado estadístico, insights automáticos, visualizaciones, consultas en lenguaje natural,
resúmenes ejecutivos con LLM y búsqueda RAG sobre documentos — todo desde una misma interfaz.

[![CI](https://github.com/SanMaBruno/insightcopilot-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/SanMaBruno/insightcopilot-ai/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

</div>

---

## Propuesta de valor

InsightCopilot AI convierte datos crudos en conocimiento accionable. Es un sistema end-to-end que combina **Data Science**, **AI/LLM** y **Software Engineering profesional** en un solo producto cohesivo.

**¿Para quién es?** Equipos de datos, analistas y tomadores de decisiones que necesitan explorar datasets rápidamente, entender patrones y obtener resúmenes ejecutivos — sin escribir código.

---

## Capacidades principales

| Capacidad | Descripción |
|---|---|
| **Perfilado automático** | Estadísticas descriptivas por columna: tipos, nulos, media, percentiles, valores únicos. |
| **Insights inteligentes** | Detecta patrones, outliers y correlaciones. Clasifica por severidad (info, warning, critical). |
| **Visualizaciones** | Histogramas, barras, correlación — generados automáticamente y listos para presentar. |
| **Consulta analítica** | Preguntas en lenguaje natural sobre los datos. No requiere API key. |
| **Executive Summary (LLM)** | Resúmenes ejecutivos generados con GPT-4o-mini, configurables por audiencia y tono. |
| **RAG documental** | Indexa documentos, genera embeddings y responde preguntas cruzando datos + contexto. |

---

## Screenshots

> Las capturas de pantalla se encuentran en [`docs/screenshots/`](docs/screenshots/).

| Vista | Preview |
|---|---|
| Home | ![Home](docs/screenshots/home.png) |
| Profile | ![Profile](docs/screenshots/profile.png) |
| Insights | ![Insights](docs/screenshots/insights.png) |
| Visualizaciones | ![Charts](docs/screenshots/charts.png) |
| Consulta analítica | ![Query](docs/screenshots/query.png) |
| API Docs | ![API Docs](docs/screenshots/api-docs.png) |

> *Si las imágenes no cargan, las capturas se generan ejecutando la demo localmente.*

---

## Arquitectura

Clean Architecture con **5 capas** y regla de dependencia estricta:

```
presentation  →  application  →  domain  ←  infrastructure
                                    ↑
                                  shared
```

```
src/
├── presentation/    API REST (FastAPI, schemas, middleware, error handlers)
├── application/     12 use cases + 5 servicios de orquestación
├── domain/          Entidades, contratos abstractos, value objects
├── infrastructure/  CSV loader, SQLite, Matplotlib, OpenAI, vector store
└── shared/          Config, excepciones, utilidades
```

| Principio | Aplicación |
|---|---|
| **SRP** | Un use case = una responsabilidad. |
| **OCP** | Nuevas fuentes de datos → implementar `DatasetLoader`, sin tocar lo existente. |
| **LSP** | `InMemoryDatasetRepository` y `SqliteDatasetRepository` son intercambiables. |
| **ISP** | Contratos pequeños: `LlmClient`, `DocumentRetriever`, `FileStorage`. |
| **DIP** | Use cases dependen de abstracciones, no de implementaciones. |

> Decisiones técnicas documentadas como ADRs en [`docs/decisions/`](docs/decisions/).

---

## Stack tecnológico

| Capa | Tecnologías |
|---|---|
| **Backend** | Python 3.9+, FastAPI, Pydantic v2, Pandas, Matplotlib |
| **AI/LLM** | OpenAI GPT-4o-mini, text-embedding-3-small |
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS |
| **Persistencia** | SQLite |
| **Testing** | pytest (172+ tests), httpx |
| **Calidad** | Ruff, MyPy, ESLint |
| **CI/CD** | GitHub Actions (lint + test + build) |
| **Infraestructura** | Docker, Docker Compose |

---

## Quickstart

### Requisitos

- Python 3.9+
- Node.js 22+
- (Opcional) Docker

### Setup local

```bash
# Clonar
git clone https://github.com/SanMaBruno/insightcopilot-ai.git
cd insightcopilot-ai

# Backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e ".[dev]"

# Variables de entorno
cp .env.example .env
# Editar .env con OPENAI_API_KEY para funciones LLM (opcional)

# Frontend
cd frontend && npm install && cd ..
```

### Iniciar servicios

```bash
# Terminal 1 — Backend
uvicorn src.presentation.api.app:app --reload

# Terminal 2 — Frontend
cd frontend && npm run dev
```

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs

### Con Docker

```bash
cp .env.example .env
docker compose up --build
# Backend disponible en http://localhost:8000
```

### Frontend env local

```bash
cd frontend
cp .env.example .env
```

---

## Demo rápida

1. Abrir http://localhost:5173 → ver la **Home** con las capacidades del producto.
2. Ir a **Datasets** → subir `data/sample/ecommerce_products.csv` (30 productos, 10 columnas).
3. **Profile** → estadísticas por columna, nulos detectados.
4. **Insights** → patrones y advertencias clasificados por severidad.
5. **Charts** → visualizaciones generadas automáticamente.
6. **Query** → preguntar *"¿Cuántas filas tiene el dataset?"* o *"resumen"*.
7. **Summary (LLM)** → generar resumen ejecutivo (requiere API key).
8. **RAG (LLM)** → preguntas cruzando datos + documentos indexados.

> Guía completa: [`docs/demo-walkthrough.md`](docs/demo-walkthrough.md) · Guión de demo: [`docs/demo-script.md`](docs/demo-script.md)

---

## API (14 endpoints)

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/health` | Estado del servicio |
| `POST` | `/datasets` | Crear dataset (JSON) |
| `POST` | `/datasets/upload` | Subir CSV |
| `GET` | `/datasets` | Listar datasets |
| `GET` | `/datasets/{id}` | Obtener dataset |
| `GET` | `/datasets/{id}/profile` | Perfil estadístico |
| `GET` | `/datasets/{id}/insights` | Insights automáticos |
| `GET` | `/datasets/{id}/visualizations` | Gráficos (base64) |
| `POST` | `/datasets/{id}/query` | Consulta en lenguaje natural |
| `POST` | `/datasets/{id}/executive-summary` | Resumen ejecutivo (LLM) |
| `POST` | `/datasets/{id}/rag-query` | RAG query |
| `POST` | `/datasets/{id}/enriched-summary` | Resumen enriquecido |
| `POST` | `/documents/upload` | Subir documento |
| `POST` | `/documents/index` | Indexar para RAG |

---

## Testing y calidad

```bash
# 172+ tests unitarios
pytest

# Cobertura
pytest --cov=src --cov-report=term-missing

# Linter Python
ruff check src/ tests/

# TypeScript
cd frontend && npx tsc --noEmit
```

CI ejecuta automáticamente en cada push: lint + tests (backend) + build (frontend).

---

## Estructura del proyecto

```
insightcopilot-ai/
├── src/                     Código fuente — 5 capas Clean Architecture
│   ├── presentation/        FastAPI, routes, schemas, middleware
│   ├── application/         Use cases y servicios
│   ├── domain/              Entidades, contratos, value objects
│   ├── infrastructure/      CSV, SQLite, Matplotlib, OpenAI
│   └── shared/              Config, excepciones, utils
├── frontend/                React + TypeScript + Vite + Tailwind
├── tests/                   172+ tests unitarios
├── data/sample/             Datasets y documentos de ejemplo
├── docs/                    ADRs, walkthrough, screenshots
├── .github/workflows/       CI con GitHub Actions
├── Dockerfile               Imagen de producción
├── docker-compose.yml       Orquestación local
└── CHANGELOG.md             Historial de versiones
```

---

## Variables de entorno

| Variable | Descripción | Default |
|---|---|---|
| `APP_ENV` | Entorno de ejecución | `development` |
| `LOG_LEVEL` | Nivel de logging | `INFO` |
| `LLM_MODE` | Modo de IA (`openai` o `mock`) | `openai` |
| `OPENAI_API_KEY` | API key de OpenAI (opcional) | — |
| `OPENAI_MODEL` | Modelo para texto | `gpt-4o-mini` |
| `EMBEDDING_MODEL` | Modelo para embeddings | `text-embedding-3-small` |
| `DATABASE_URL` | Ruta SQLite | `data/insightcopilot.db` |
| `UPLOAD_DIR` | Directorio de uploads | `data/uploads` |

### Frontend

| Variable | Descripción | Default |
|---|---|---|
| `VITE_API_BASE_URL` | URL pública del backend | `/api` en local con proxy |

---

## Deploy

Ruta recomendada para portafolio:

- Backend en Render
- Frontend en Vercel

Guía paso a paso: [`docs/deploy.md`](docs/deploy.md)

---

## Roadmap

### v1.0.0 (actual)
- [x] Clean Architecture (5 capas, SOLID, DIP)
- [x] 12 use cases + 5 servicios
- [x] 14 endpoints REST
- [x] Perfilado, insights, visualizaciones, query analítico
- [x] Executive summary y RAG con OpenAI
- [x] Frontend React + TypeScript
- [x] 172+ tests unitarios
- [x] CI/CD con GitHub Actions
- [x] Docker ready

### Próximos pasos
- [ ] Deploy público/semi-público
- [ ] Validación end-to-end post deploy
- [ ] README con URLs públicas y release final
- [ ] Deploy público (Railway / Render)
- [ ] Tests de integración end-to-end
- [ ] Upload de documentos desde frontend
- [ ] Dashboard con métricas históricas

---

## Autor

**Bruno San Martín** — [GitHub](https://github.com/SanMaBruno) · [LinkedIn](https://www.linkedin.com/in/brunosanmartin/)

---

## Licencia

MIT — ver [LICENSE](LICENSE).
