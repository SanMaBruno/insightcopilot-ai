# Deploy Guide

## Objetivo

Desplegar InsightCopilot AI con la menor complejidad operativa posible, manteniendo la arquitectura actual.

## Estrategia recomendada

- Backend: Render Web Service usando el `Dockerfile` existente.
- Frontend: Vercel usando el proyecto `frontend/`.

Esta combinación es simple, profesional y suficiente para portafolio:

- Render encaja bien con FastAPI + Docker.
- Vercel encaja bien con Vite + React y facilita previews.
- No requiere rediseñar persistencia ni arquitectura.

## Backend en Render

### Variables requeridas

- `APP_ENV=production`
- `LOG_LEVEL=INFO`
- `LLM_MODE=mock` o `LLM_MODE=openai`
- `OPENAI_API_KEY=` solo si `LLM_MODE=openai`
- `OPENAI_MODEL=gpt-4o-mini`
- `EMBEDDING_MODEL=text-embedding-3-small`
- `DATABASE_URL=/app/data/insightcopilot.db`
- `UPLOAD_DIR=/app/data/uploads`

### Persistencia recomendada

Para no cambiar la arquitectura:

- Montar un disco persistente en `/app/data`
- Guardar ahí SQLite y uploads

Esto mantiene intacto el uso actual de:

- SQLite
- filesystem local para uploads

### Modos de operación

- Demo estable de portafolio: `LLM_MODE=mock`
- Demo real con OpenAI: `LLM_MODE=openai`

Recomendación operativa:

- usar `mock` como default público
- pasar a `openai` solo si la cuenta tiene billing estable

### Healthcheck

- Path: `/health`
- Validación esperada: `{"status":"ok","version":"1.0.0"}`

## Frontend en Vercel

### Build

- Root directory: `frontend`
- Build command: `npm run build`
- Output directory: `dist`

### Variable requerida

- `VITE_API_BASE_URL=https://TU-BACKEND.onrender.com`

Si no se define, el frontend usa `/api`, pensado para desarrollo local con proxy de Vite.

### Routing SPA

El archivo `frontend/vercel.json` deja funcionando rutas directas como:

- `/`
- `/datasets`
- `/datasets/:id`

## Validación end-to-end

### Smoke test backend

1. Abrir `/health`
2. Confirmar status `ok`
3. Verificar que `/docs` cargue

### Flujo funcional

1. Subir CSV
2. Abrir dataset
3. Validar tab `Profile`
4. Validar tab `Insights`
5. Validar tab `Charts`
6. Validar tab `Query`
7. Validar tab `Summary (LLM)`
8. Validar tab `RAG (LLM)`

### Casos a probar

- Upload de CSV correcto
- Rechazo de archivo inválido
- Profile con conteos correctos
- Insights visibles
- Visualizaciones renderizadas
- Analytical query responde
- Summary responde en `mock`
- Summary responde en `openai` o muestra error semántico si no hay cuota
- Upload de documento para RAG
- Indexación de documento
- RAG responde en `mock`
- RAG responde en `openai` o muestra error semántico si embeddings no están disponibles

## Checklist de cierre de portafolio

- URL pública del frontend
- URL pública del backend
- README con ambas URLs
- screenshots finales actualizados
- demo walkthrough revisado
- release/tag final creado
- modo público definido: `mock` u `openai`

## Orden correcto de ejecución

1. Desplegar backend
2. Validar healthcheck y `/docs`
3. Configurar URL del backend en frontend
4. Desplegar frontend
5. Ejecutar checklist end-to-end
6. Actualizar README
7. Crear release final
