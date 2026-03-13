# Changelog

Todos los cambios relevantes del proyecto se documentan en este archivo.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y el proyecto usa [Semantic Versioning](https://semver.org/lang/es/).

---

## [1.0.0] — 2026-03-13

Primera versión pública de InsightCopilot AI.

### Backend

#### Added
- **Clean Architecture** con 5 capas: presentation, application, domain, infrastructure, shared.
- **12 use cases** independientes con responsabilidad única.
- **5 servicios** de orquestación: insight generator, query resolver, executive summary context builder, text chunker, RAG context builder.
- **14 endpoints REST** organizados en health, datasets y documents.
- **Perfilado automático** de datasets CSV (tipos, nulos, estadísticas, percentiles).
- **Generación de insights** con detección de patrones, outliers y correlaciones.
- **Visualizaciones** con Matplotlib (histogramas, barras, correlación) devueltas en base64.
- **Consulta analítica** en lenguaje natural sobre datos cargados (sin API key).
- **Executive summary** con OpenAI GPT-4o-mini, configurable por audiencia y tono.
- **RAG documental**: upload, indexación, chunking, embeddings y consulta contextual.
- **Persistencia** con SQLite y repositorio in-memory intercambiables.
- **Observabilidad**: endpoint /health, logging estructurado, request logging middleware, error handlers globales.
- **CORS** configurado para desarrollo.
- **172+ tests unitarios** con aislamiento completo.
- **CI/CD** con GitHub Actions (lint + test + build).
- **Docker** y Docker Compose con health check.

### Frontend

#### Added
- Aplicación **React 19 + TypeScript + Vite + Tailwind CSS**.
- **Home** con propuesta de valor, capacidades e instrucciones de uso.
- **Datasets**: listado y upload de CSV.
- **Dataset detail** con 6 pestañas: Profile, Insights, Charts, Query, Summary (LLM), RAG (LLM).
- Componentes UI compartidos (Spinner, ErrorBox, EmptyState, SectionCard, InfoBanner).
- API client tipado conectado al backend vía proxy.

### Documentación

#### Added
- README orientado a portafolio con screenshots, quickstart y demo flow.
- **2 ADRs**: Clean Architecture (ADR-001), dependencias mínimas (ADR-002).
- Demo walkthrough paso a paso.
- Demo script para presentaciones de 1-3 minutos.
- Datos de ejemplo: ecommerce_products.csv (30 filas), product_strategy.md.

---

## Convenciones

- **Added** para funcionalidades nuevas.
- **Changed** para cambios en funcionalidades existentes.
- **Fixed** para correcciones de bugs.
- **Removed** para funcionalidades eliminadas.
