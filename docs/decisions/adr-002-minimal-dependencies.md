# ADR-002: Dependencias mínimas en fase inicial

## Estado

Aceptado

## Contexto

Es tentador instalar todas las librerías desde el inicio (OpenAI, SQLAlchemy, Plotly, etc.), pero cada dependencia agrega complejidad, superficie de ataque y acoplamiento.

## Decisión

Solo instalamos lo estrictamente necesario para la fase actual:

- **FastAPI + Uvicorn**: base de la API
- **Pydantic + pydantic-settings**: validación y configuración tipada
- **Pandas**: manipulación de datos
- **python-dotenv**: carga de variables de entorno

Las dependencias futuras (OpenAI, SQLAlchemy, etc.) se agregarán cuando exista un caso de uso concreto que las requiera.

## Consecuencias

**Positivas:**
- Entorno ligero y rápido de instalar
- Menor superficie de conflictos de versiones
- Cada dependencia futura estará justificada por un caso de uso real

**Negativas:**
- Al agregar dependencias nuevas habrá que actualizar requirements.txt
