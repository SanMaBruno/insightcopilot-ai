<div align="center">

<img src="https://img.shields.io/badge/InsightCopilot-AI-6C3AED?style=for-the-badge&logo=sparkles&logoColor=white" alt="InsightCopilot AI" />

# 🧠 InsightCopilot AI

**Plataforma de Inteligencia de Datos impulsada por IA**

Sube un CSV → obtén perfilado estadístico, insights automáticos, visualizaciones,
consultas en lenguaje natural, resúmenes ejecutivos con LLM y búsqueda RAG — todo en una interfaz moderna.

[![CI](https://github.com/SanMaBruno/insightcopilot-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/SanMaBruno/insightcopilot-ai/actions)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.3-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[🌐 Demo en vivo](https://sanmabruno.github.io/insightcopilot-ai/) · [📖 API Docs](http://localhost:8000/docs) · [🐛 Reportar Bug](https://github.com/SanMaBruno/insightcopilot-ai/issues)

</div>

---

## 📋 Tabla de Contenidos

- [✨ Características](#-características)
- [🏗️ Arquitectura](#️-arquitectura)
- [🛠️ Stack Tecnológico](#️-stack-tecnológico)
- [🚀 Quickstart](#-quickstart)
- [🎮 Demo Rápida](#-demo-rápida)
- [📡 API Endpoints](#-api-endpoints)
- [🧪 Testing](#-testing)
- [📁 Estructura del Proyecto](#-estructura-del-proyecto)
- [⚙️ Variables de Entorno](#️-variables-de-entorno)
- [🌍 Deploy](#-deploy)
- [🗺️ Roadmap](#️-roadmap)
- [👤 Autor](#-autor)

---

## ✨ Características

| | Característica | Descripción |
|---|---|---|
| 📊 | **Perfilado Automático** | Estadísticas descriptivas, tipos de datos, nulos, media, percentiles, valores únicos |
| 💡 | **Insights con IA** | Detección de patrones, outliers y correlaciones clasificados por severidad |
| 📈 | **Visualizaciones Inteligentes** | Histogramas, barras y correlaciones generadas automáticamente |
| 🔍 | **Consultas en Lenguaje Natural** | Preguntas en español sobre tus datos, respuestas respaldadas por SQL |
| 📝 | **Resúmenes Ejecutivos** | Generados con GPT-4o-mini para tomadores de decisiones |
| 🧠 | **Consultas RAG** | Generación aumentada por recuperación para Q&A contextual profundo |

---

## 🏗️ Arquitectura

Clean Architecture con **5 capas** y principios **SOLID**:

```
┌──────────────────────────────────────────────┐
│               presentation                    │  ← FastAPI, Routes, Schemas
├──────────────────────────────────────────────┤
│               application                     │  ← Use Cases, Services
├──────────────────────────────────────────────┤
│                 domain                        │  ← Entities, Contracts, VOs
├──────────────────────────────────────────────┤
│              infrastructure                   │  ← SQLite, OpenAI, Matplotlib
├──────────────────────────────────────────────┤
│                 shared                        │  ← Config, Exceptions, Utils
└──────────────────────────────────────────────┘
```

| Principio | Aplicación |
|---|---|
| **SRP** 🎯 | Un use case = una responsabilidad |
| **OCP** 🔓 | Nuevas fuentes de datos → implementar `DatasetLoader` sin tocar existente |
| **LSP** 🔄 | `InMemoryRepo` y `SqliteRepo` son intercambiables |
| **ISP** 📦 | Contratos pequeños: `LlmClient`, `DocumentRetriever`, `FileStorage` |
| **DIP** 🔌 | Use cases dependen de abstracciones, no de implementaciones |

---

## 🛠️ Stack Tecnológico

<table>
<tr>
<td align="center" width="50%">

### 🔧 Backend
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)

</td>
<td align="center" width="50%">

### 🎨 Frontend
![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-646CFF?logo=vite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind-06B6D4?logo=tailwindcss&logoColor=white)

</td>
</tr>
<tr>
<td align="center">

### 🤖 AI / LLM
![OpenAI](https://img.shields.io/badge/OpenAI-412991?logo=openai&logoColor=white)
![GPT-4o-mini](https://img.shields.io/badge/GPT--4o--mini-black?logo=openai&logoColor=white)

</td>
<td align="center">

### 🧪 DevOps
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?logo=githubactions&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-0A9EDC?logo=pytest&logoColor=white)

</td>
</tr>
</table>

---

## 🚀 Quickstart

### Requisitos previos

- 🐍 Python 3.9+
- 📦 Node.js 22+
- 🐳 Docker (opcional)

### Instalación local

```bash
# 1️⃣ Clonar el repositorio
git clone https://github.com/SanMaBruno/insightcopilot-ai.git
cd insightcopilot-ai

# 2️⃣ Backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e ".[dev]"

# 3️⃣ Variables de entorno
cp .env.example .env
# Editar .env con OPENAI_API_KEY para funciones LLM (opcional)

# 4️⃣ Frontend
cd frontend && npm install && cd ..
```

### ▶️ Iniciar servicios

```bash
# Terminal 1 — Backend
uvicorn src.presentation.api.app:app --reload

# Terminal 2 — Frontend
cd frontend && npm run dev
```

| Servicio | URL |
|---|---|
| 🌐 Frontend | http://localhost:5173 |
| ⚡ API Backend | http://localhost:8000 |
| 📖 Swagger Docs | http://localhost:8000/docs |

### 🐳 Con Docker

```bash
cp .env.example .env
docker compose up --build
```

---

## 🎮 Demo Rápida

1. 🏠 Abrir http://localhost:5173 → ver la **Home** con las capacidades
2. 📤 Ir a **Subir** → arrastra `data/sample/ecommerce_products.csv`
3. 📊 **Perfil** → estadísticas por columna, nulos detectados
4. 💡 **Insights** → patrones y advertencias por severidad
5. 📈 **Gráficos** → visualizaciones generadas automáticamente
6. 🔍 **Consulta** → preguntar *"¿Cuántas filas tiene el dataset?"*
7. 📝 **Resumen** → resumen ejecutivo con IA *(requiere API key con créditos)*
8. 🧠 **RAG** → preguntas cruzando datos + documentos *(requiere API key con créditos)*

> ⚠️ Las funciones de Resumen Ejecutivo, Consulta Analítica y RAG requieren una API key de OpenAI con créditos activos. Sin créditos, se mostrará un mensaje informativo.

---

## 📡 API Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/health` | 🏥 Estado del servicio |
| `POST` | `/datasets` | ➕ Crear dataset (JSON) |
| `POST` | `/datasets/upload` | 📤 Subir CSV |
| `GET` | `/datasets` | 📋 Listar datasets |
| `GET` | `/datasets/{id}` | 🔎 Obtener dataset |
| `GET` | `/datasets/{id}/profile` | 📊 Perfil estadístico |
| `GET` | `/datasets/{id}/insights` | 💡 Insights automáticos |
| `GET` | `/datasets/{id}/visualizations` | 📈 Gráficos (base64) |
| `POST` | `/datasets/{id}/query` | 🔍 Consulta en lenguaje natural |
| `POST` | `/datasets/{id}/executive-summary` | 📝 Resumen ejecutivo (LLM) |
| `POST` | `/datasets/{id}/rag-query` | 🧠 RAG query |
| `POST` | `/datasets/{id}/enriched-summary` | 📑 Resumen enriquecido |
| `POST` | `/documents/upload` | 📄 Subir documento |
| `POST` | `/documents/index` | 🗂️ Indexar para RAG |

---

## 🧪 Testing

```bash
# Ejecutar 183+ tests unitarios
pytest

# Con cobertura
pytest --cov=src --cov-report=term-missing

# Linter Python
ruff check src/ tests/

# TypeScript check
cd frontend && npx tsc --noEmit
```

CI ejecuta automáticamente en cada push: lint → tests → build.

---

## 📁 Estructura del Proyecto

```
insightcopilot-ai/
├── 📂 src/                      Backend — Clean Architecture (5 capas)
│   ├── 📂 presentation/        FastAPI, routes, schemas, middleware
│   ├── 📂 application/         12 use cases + 5 servicios
│   ├── 📂 domain/              Entidades, contratos, value objects
│   ├── 📂 infrastructure/      SQLite, OpenAI, Matplotlib, CSV
│   └── 📂 shared/              Config, excepciones, utilidades
├── 📂 frontend/                 React + TypeScript + Vite + Tailwind
│   └── 📂 src/
│       ├── 📂 api/             Cliente API
│       ├── 📂 components/      Componentes UI + dataset tabs
│       ├── 📂 layouts/         Layout principal con sidebar
│       ├── 📂 pages/           Home, Datasets, Upload, Detail
│       └── 📂 types/           Tipos TypeScript
├── 📂 docs/                     Frontend build (GitHub Pages)
├── 📂 tests/                    183+ tests unitarios
├── 📂 data/sample/              Datasets de ejemplo
├── 📂 .github/workflows/        CI con GitHub Actions
├── 🐳 Dockerfile               Imagen de producción
├── 🐳 docker-compose.yml       Orquestación local
└── 📄 CHANGELOG.md              Historial de versiones
```

---

## ⚙️ Variables de Entorno

### Backend

| Variable | Descripción | Default |
|---|---|---|
| `APP_ENV` | Entorno de ejecución | `development` |
| `LOG_LEVEL` | Nivel de logging | `INFO` |
| `LLM_MODE` | Modo de IA (`openai` / `mock`) | `openai` |
| `OPENAI_API_KEY` | API key de OpenAI | — |
| `OPENAI_MODEL` | Modelo para texto | `gpt-4o-mini` |
| `EMBEDDING_MODEL` | Modelo para embeddings | `text-embedding-3-small` |
| `DATABASE_URL` | Ruta SQLite | `data/insightcopilot.db` |
| `UPLOAD_DIR` | Directorio de uploads | `data/uploads` |

### Frontend

| Variable | Descripción | Default |
|---|---|---|
| `VITE_API_BASE_URL` | URL del backend | `http://localhost:8000` |

---

## 🌍 Deploy

### Frontend → GitHub Pages

El frontend se compila a `docs/` y se sirve desde GitHub Pages:

```bash
cd frontend && npm run build   # Build a ../docs/
```

**Configurar GitHub Pages:** Settings → Pages → Source: `Deploy from a branch` → Branch: `main`, folder: `/docs`

🔗 **URL:** [https://sanmabruno.github.io/insightcopilot-ai/](https://sanmabruno.github.io/insightcopilot-ai/)

### Backend → Docker / Render

```bash
docker compose up --build
# Backend en http://localhost:8000
```

---

## 🗺️ Roadmap

### ✅ v1.0.0 (actual)

- [x] Clean Architecture (5 capas, SOLID, DIP)
- [x] 12 use cases + 5 servicios de orquestación
- [x] 14 endpoints REST
- [x] Perfilado, insights, visualizaciones, consulta analítica
- [x] Executive summary y RAG con OpenAI
- [x] Frontend React + TypeScript (SPA)
- [x] 183+ tests unitarios
- [x] CI/CD con GitHub Actions
- [x] Docker ready
- [x] Deploy frontend en GitHub Pages
- [x] Interfaz completa en español

### 🔮 Próximos pasos

- [ ] Deploy backend público (Render / Railway)
- [ ] Tests de integración end-to-end
- [ ] Upload de documentos desde frontend
- [ ] Dashboard con métricas históricas
- [ ] Soporte multi-idioma

---

## 👤 Autor

<div align="center">

**Bruno San Martin**

[![GitHub](https://img.shields.io/badge/GitHub-SanMaBruno-181717?logo=github&logoColor=white&style=for-the-badge)](https://github.com/SanMaBruno)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-sanmabruno-0A66C2?logo=linkedin&logoColor=white&style=for-the-badge)](https://www.linkedin.com/in/sanmabruno/)

</div>

---

## 📄 Licencia

MIT — ver [LICENSE](LICENSE).
