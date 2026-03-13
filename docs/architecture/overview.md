# Arquitectura — InsightCopilot AI

## Diagrama de capas

```
┌─────────────────────────────────────────────┐
│              PRESENTATION                    │
│   FastAPI routes · Pydantic schemas          │
│   Middleware · Error handlers                │
├─────────────────────────────────────────────┤
│              APPLICATION                     │
│   12 Use Cases · 5 Services                 │
├─────────────────────────────────────────────┤
│               DOMAIN                         │
│   Entities · Repository contracts            │
│   Value Objects                              │
├─────────────────────────────────────────────┤
│            INFRASTRUCTURE                    │
│   CSV Loader · SQLite · Matplotlib           │
│   OpenAI · Vector Store · File Storage       │
├─────────────────────────────────────────────┤
│               SHARED                         │
│   Settings · Exceptions · Utils              │
└─────────────────────────────────────────────┘
```

## Regla de dependencia

Las capas externas dependen de las internas, nunca al revés:

```
presentation → application → domain ← infrastructure
```

- `domain` no importa nada externo.
- `infrastructure` implementa los contratos definidos en `domain`.
- `application` orquesta la lógica usando abstracciones del dominio.
- `presentation` es el punto de entrada HTTP.

## Flujo de una petición

```
HTTP Request
  → FastAPI route (presentation)
    → Use Case (application)
      → Repository / Service contract (domain)
        → Concrete implementation (infrastructure)
      ← Result
    ← Response schema (presentation)
  → HTTP Response
```

## Decisiones técnicas

Ver ADRs en [`../decisions/`](../decisions/):

- **ADR-001**: Clean Architecture como patrón base
- **ADR-002**: Dependencias mínimas en fase inicial
